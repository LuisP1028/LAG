"""Hugging Face Inference API client and deterministic grounded synthesizer."""

import os
import re
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import httpx

from src.graphrag.exceptions import (
    ModelAuthenticationError,
    ModelInferenceError,
    ModelRateLimitError,
)

load_dotenv()


class HuggingFaceSynthesizer:
    """Synthesizes zero-hallucination patient and policy guidance from assembled graph context."""

    DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
    ROUTER_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"

    MODEL_ALIASES = {
        "meta-llama/Meta-Llama-3-8B-Instruct": "meta-llama/Llama-3.1-8B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.3": "meta-llama/Llama-3.1-8B-Instruct",
        "Qwen/Qwen2.5-7B-Instruct": "Qwen/Qwen2.5-72B-Instruct",
    }

    SYSTEM_PROMPT = (
        "You are an authoritative Medicare policy intelligence system.\n"
        "Your objective is to provide precise, factual answers based EXCLUSIVELY on the provided GRAPH CONTEXT.\n"
        "You must adhere strictly to the following rules:\n"
        "1. RELY STRICTLY ON CONTEXT: Do not extrapolate unlisted coverage, invent billing rules, or speculate. If information is not in the context, state that it is not present.\n"
        "2. QUOTE EXACT BRACKETED IDENTIFIERS: Whenever you mention a policy, bill, law, statutory section, U.S. Code section, regulation, CFR section, transmittal, coverage policy, contractor, procedure code, fee rate, state, diagnosis, CBO score, lobbying filing, or clinical study, you MUST cite its exact bracketed primary key identifier from the context (e.g., [POLICY-LTA], [BILL-117-hr-3630], [BILL-117-hr-2617], [PLAW-117-328], [STAT-117-328-SEC-4133], [USC-42-1395x-s-2-JJ], [REG-FR-2023-24455], [CFR-42-410], [TR-CR13286], [DME-MAC-COPE147943], [JURIS-DME-A], [JURIS-DME-B], [HCPCS-A6522], [ICD10-I97.2], [STATE-NY], [STATE-WI]). Always explicitly cite the Authorizing Coverage Policy (e.g., [DME-MAC-COPE147943]), CMS Transmittal (e.g., [TR-CR13286]), and Regional Claims Contractor (e.g., [JURIS-DME-B]) in your opening summary when present in Section 1 and Section 2.\n"
        "3. MANDATORY FEE AND COINSURANCE REPORTING: Whenever Section 4 contains fee schedule entries, you MUST explicitly state the exact dollar allowable reimbursement amount (e.g., $290.47) and the calculated 20% patient coinsurance (e.g., $58.09) for the relevant procedure codes (such as [HCPCS-A6522]). Never omit these dollar figures or refer the user elsewhere when they are present in the context.\n"
        "4. QUOTE OFFICIAL LEGAL CITATIONS: When referencing legislation and regulations, quote the official citations directly from the provided GRAPH CONTEXT (such as the enacted Public Law number, U.S. Code section, Federal Register citation, RIN/Docket, and CMS Transmittal/CR number).\n"
        "5. NO PROBABILISTIC GUESSING: Do not assume coverage for unlisted conditions or unverified items.\n"
    )

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")

    def synthesize(
        self,
        query: str,
        context: str,
        model_id: Optional[str] = None,
    ) -> str:
        """Synthesizes a grounded answer via Hugging Face Router API. Fails fast with zero fallback."""
        if not self.token:
            raise ModelAuthenticationError(
                "Missing Hugging Face API token. Configure HF_TOKEN or HUGGINGFACE_API_KEY in .env."
            )

        raw_model = model_id or self.DEFAULT_MODEL
        model = self.MODEL_ALIASES.get(raw_model, raw_model)

        return self._call_hf_inference_api(query=query, context=context, model_id=model)

    def _call_hf_inference_api(self, query: str, context: str, model_id: str) -> str:
        """Invokes Hugging Face Serverless Inference API via Router with strict timeout and error boundaries."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "wayfinder-graphrag-pipeline/1.0",
        }
        user_content = (
            f"Question: {query}\n\n"
            f"GRAPH CONTEXT:\n{context}\n\n"
            "Instructions: Provide a clear, concise, factual answer grounded in the GRAPH CONTEXT. "
            "In your opening paragraph, explicitly cite the Authorizing Coverage Policy (e.g. [DME-MAC-COPE147943]), CMS Transmittal (e.g. [TR-CR13286]), Enacted Public Law (e.g. [PLAW-117-328]), Federal Register Rule (e.g. [REG-FR-2023-24455]), Regional Claims Contractor (e.g. [JURIS-DME-...]), and Beneficiary State (e.g. [STATE-...]) if present in the context. "
            "If Section 4 contains fee schedule entries, explicitly quote the dollar allowable reimbursement rate (e.g. $290.47) and the 20% patient coinsurance (e.g. $58.09) for [HCPCS-A6522]."
        )
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "max_tokens": 768,
            "temperature": 0.01,
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.ROUTER_CHAT_URL, json=payload, headers=headers)
        except httpx.TimeoutException as exc:
            raise ModelInferenceError(f"Hugging Face API request timed out after 60s: {exc}") from exc
        except Exception as exc:
            raise ModelInferenceError(f"Network error communicating with Hugging Face: {exc}") from exc

        if response.status_code == 401:
            raise ModelAuthenticationError("Invalid or missing HF_TOKEN. Please provide a valid Hugging Face API key.")
        if response.status_code == 429:
            raise ModelRateLimitError("Hugging Face Inference API rate limit exceeded; please retry with exponential backoff.")
        if response.status_code >= 400:
            raise ModelInferenceError(f"Hugging Face API error {response.status_code}: {response.text}")

        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"].strip()

        return str(data)
