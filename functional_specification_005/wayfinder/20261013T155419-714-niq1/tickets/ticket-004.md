# Decision Ticket 004: Anti-Hallucination Synthesizer System Prompt and Citation Grounding Specification

**Ticket ID:** `ticket-004.md`  
**Scope:** GraphRAG Stage 4 & 5 - LLM Synthesis & Anti-Hallucination Grounding (`src/graphrag/synthesizer.py`)  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-003.md`  

---

## 1. Architectural Question
How must `HuggingFaceSynthesizer` be configured and prompted to strictly guarantee zero-hallucination answers quoting exact bracketed primary key identifiers (`[CMS-MCD-A59508]`, `[PLAW-117-328]`, `[JURIS-DME-A]`), exact reimbursement and coinsurance figures, and official statutory/regulatory citations?

---

## 2. Technical Audit and Empirical Findings

1. **Current Codebase System Prompt:**
   - In `src/graphrag/synthesizer.py` lines 30-34:
     ```python
     SYSTEM_PROMPT = (
         "You are an expert Medicare policy intelligence assistant.\n"
         "Answer the user's question using ONLY the factual statements provided in the GRAPH CONTEXT below.\n"
         "You are strictly forbidden from guessing reimbursement rates, making up procedure codes, or extrapolating unverified coverage criteria.\n"
     )
     ```
   - While it forbids guessing, it does not explicitly instruct the model to:
     - Quote bracketed node IDs (e.g. `[CMS-MCD-A59508]`).
     - Quote both exact allowable reimbursement amounts and 20% patient coinsurance.
     - Cite Public Law and Federal Register references directly.
2. **External Remote Service Integration (Hugging Face Router):**
   - Candidate Datasource / API: Hugging Face Serverless Chat Completion API via Router.
   - Endpoint URL: `https://router.huggingface.co/v1/chat/completions`
   - HTTP Method: `POST`
   - Headers:
     - `Authorization: Bearer <HF_TOKEN>`
     - `Content-Type: application/json`
     - `User-Agent: wayfinder-graphrag-pipeline/1.0`
   - Default Model: `meta-llama/Llama-3.1-8B-Instruct`
   - Decoding Parameters: `temperature: 0.01` (greedy/deterministic), `max_tokens: 1024`.
   - Timeout: 25.0 seconds.

---

## 3. Concrete Architectural Decision & System Prompt Specification

### 3.1. Grounded Anti-Hallucination System Prompt
Replace `SYSTEM_PROMPT` in `HuggingFaceSynthesizer` with the strict specification conforming to Section 4.4:
```python
SYSTEM_PROMPT = (
    "You are an authoritative Medicare policy intelligence system.\n"
    "Your objective is to provide precise, factual answers based EXCLUSIVELY on the provided GRAPH CONTEXT.\n"
    "You must adhere strictly to the following rules:\n"
    "1. RELY STRICTLY ON CONTEXT: Do not extrapolate unlisted coverage, invent billing rules, or speculate. If information is not in the context, state that it is not present.\n"
    "2. QUOTE EXACT BRACKETED IDENTIFIERS: Whenever you mention a policy, law, change request, regulation, contractor, procedure code, or diagnosis, you MUST cite its exact bracketed primary key identifier (e.g., [CMS-MCD-A59508], [PLAW-117-328], [JURIS-DME-A], [JURIS-DME-B], [CMS-CR-13286], [HCPCS-A6522], [ICD10-I97.2], [STATE-NY]).\n"
    "3. QUOTE EXACT DOLLAR FIGURES: When discussing fees, state both the exact allowable fee (e.g., $290.47) and the calculated 20% patient coinsurance (e.g., $58.09) exactly as provided.\n"
    "4. QUOTE OFFICIAL LEGAL CITATIONS: When referencing legislation and regulations, quote the enacted Public Law number (e.g., Public Law 117-328) and Federal Register rule publication (e.g., 88 FR 77676, CMS-1784-F).\n"
    "5. NO PROBABILISTIC GUESSING: Do not assume coverage for unlisted conditions or unverified items.\n"
)
```

### 3.2. Fail-Fast Network and Authentication Boundaries (`INV-FAIL-FAST`)
In `_call_hf_inference_api`:
- If `self.token` is None or empty: immediately raise `ModelAuthenticationError("Missing Hugging Face API token. Configure HF_TOKEN or HUGGINGFACE_API_KEY in .env.")`.
- If response status code is `401`: raise `ModelAuthenticationError("Invalid or missing HF_TOKEN. Please provide a valid Hugging Face API key.")`.
- If response status code is `429`: raise `ModelRateLimitError("Hugging Face Inference API rate limit exceeded; please retry with exponential backoff.")`.
- If response status code is `>= 400`: raise `ModelInferenceError(f"Hugging Face API error {response.status_code}: {response.text}")`.
- If HTTP request times out (25.0s): raise `ModelInferenceError(f"Hugging Face API request timed out after 25s: {exc}")`.
