# Decision Ticket 004: Hugging Face Inference API Integration, Operational Parameters, and Prompt Grounding Specification

**Ticket ID:** `ticket-004.md`  
**Scope:** GraphRAG Stages 3–5: Context Assembly, LLM Synthesis, and Provenance Citation  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-003.md`

---

## 1. Architectural Question

What Hugging Face open-weight model endpoints, endpoint operational parameters (HTTP method, parameters, headers, authentication, rate limits), target payload schemas, and prompt grounding contracts must be locked to synthesize zero-hallucination, compassionate patient and policy answers with mandatory provenance citations (`INV-PROVENANCE-COMPLETENESS`)?

---

## 2. Decision and Specification Requirements

### 2.1. Candidate Datasource & Model Selection
- **API Provider:** Hugging Face Serverless Inference API
- **Endpoint Base URL:** `https://api-inference.huggingface.co/models/{model_id}`
- **Qualified Open-Weight Models:**
  1. `meta-llama/Meta-Llama-3-8B-Instruct` (Primary default for reasoning and instruction following)
  2. `mistralai/Mistral-7B-Instruct-v0.3` (Alternative high-speed instruction model)
  3. `Qwen/Qwen2.5-7B-Instruct` (Alternative clinical and technical reasoning model)
- **Model Switching:** The user or frontend may pass an optional `model_id` parameter; if omitted, defaults to `meta-llama/Meta-Llama-3-8B-Instruct`.

### 2.2. Endpoint Operational Parameters
- **HTTP Method:** `POST`
- **Request Headers:**
  - `Authorization: Bearer {HF_TOKEN}` (retrieved from `HF_TOKEN` environment variable)
  - `Content-Type: application/json`
  - `User-Agent: wayfinder-graphrag-pipeline/1.0`
- **Request Payload Schema:**
  ```json
  {
    "inputs": "<prompt_string>",
    "parameters": {
      "max_new_tokens": 1024,
      "temperature": 0.0,
      "top_p": 0.95,
      "do_sample": false,
      "return_full_text": false
    },
    "options": {
      "wait_for_model": true,
      "use_cache": true
    }
  }
  ```
- **Target Response Payload Schema:**
  ```json
  [
    {
      "generated_text": "Patient guidance text with citations..."
    }
  ]
  ```
- **Rate Limit & Fault Operational Handling:**
  - `401 Unauthorized`: Token missing or invalid permissions $\rightarrow$ raise `ModelAuthenticationError("Invalid or missing HF_TOKEN")`.
  - `429 Too Many Requests`: Rate limit hit $\rightarrow$ raise `ModelRateLimitError("Hugging Face rate limit exceeded; retry after backoff")`.
  - `503 Service Unavailable`: Model warming up (`{"error": "Model ... is currently loading", "estimated_time": float}`) $\rightarrow$ respect `estimated_time` or surface diagnostic message.
  - Timeout: Client timeout strictly configured to 25.0 seconds.

### 2.3. Stage 3: Structured Context Assembly Format
- **Module:** `src/graphrag/context_assembler.py`
- **Class:** `GraphContextAssembler`
- **Assembly Logic:** Serializes `TraversalResult` into four explicit Markdown sections:
  1. **Administrative Authority:**
     ```markdown
     ### Program & Authority Lineage
     - Root Policy: [{policy_pk}] {policy_name}
     - Authorizing Coverage Policy: [{article_pk}] {article_title}
     - Operational Change Request: [{cr_pk}] Transmittal {transmittal} (Benefit Category: {catg})
     - Regional Claims Contractor: [{jurisdiction_pk}] {contractor_name} (Covers: {states})
     ```
  2. **Clinical Eligibility:**
     ```markdown
     ### Clinical Eligibility
     - Permitted Diagnosis: [{icd10_pk}] {icd10_description}
     - Statutory/Regulatory Authorization: 42 CFR § 410.36; requires written physician order.
     ```
  3. **Covered Items & Pricing Integration:**
     ```markdown
     ### Covered Items & Allowable Fees ({state_name}, 2024)
     - [{hcpcs_code}] {hcpcs_description}: Allowable = ${fee_amount:.2f} (Estimated 20% patient coinsurance = ${fee_amount * 0.20:.2f})
     ```
  4. **Edge Provenance Directory (`INV-PROVENANCE-COMPLETENESS`):**
     ```markdown
     ### Data Provenance & Government Citations
     - Policy Authority Source: {source_uri} (Selector: {selector}, Ingested: {ingestion_timestamp})
     - Fee Schedule Source: {source_uri} (Selector: {selector}, Run ID: {run_id})
     ```

### 2.4. Stage 4 & 5: Prompt Grounding and Anti-Hallucination Guardrail
- **System Prompt Specification:**
  ```text
  You are an expert Medicare policy intelligence assistant.
  Answer the user's question using ONLY the factual statements provided in the GRAPH CONTEXT below.
  You are strictly forbidden from guessing reimbursement rates, making up procedure codes, or extrapolating unverified coverage criteria.
  Always calculate the patient's 20% coinsurance when allowable fees are present.
  Always cite the authorizing CMS Coverage Policy article and primary source provenance for each statement.
  If an item, state rate, or diagnosis is not present in the graph context, state that it is not covered or not listed in Medicare Part B fee schedules.
  ```
- **Context Grounding Assertion:** The synthesized text must contain the exact fee amount (`$290.47`), the contractor name (`CGS Administrators`), and the mandatory citation (`CMS-MCD-A59508`).
