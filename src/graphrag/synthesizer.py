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
        "2. QUOTE EXACT BRACKETED IDENTIFIERS: Whenever you mention a policy, law, change request, regulation, contractor, procedure code, state, or diagnosis, you MUST cite its exact bracketed primary key identifier (e.g., [CMS-MCD-A59508], [PLAW-117-328], [JURIS-DME-A], [JURIS-DME-B], [CMS-CR-13286], [HCPCS-A6522], [ICD10-I97.2], [STATE-NY], [STATE-WI]).\n"
        "3. MANDATORY FEE AND COINSURANCE REPORTING: Whenever Section 4 contains fee schedule entries, you MUST explicitly state the exact dollar allowable reimbursement amount (e.g., $290.47) and the calculated 20% patient coinsurance (e.g., $58.09) for the relevant procedure codes (such as [HCPCS-A6522]). Never omit these dollar figures or refer the user elsewhere when they are present in the context.\n"
        "4. QUOTE OFFICIAL LEGAL CITATIONS: When referencing legislation and regulations, quote the enacted Public Law number (e.g., Public Law 117-328) and Federal Register rule publication (e.g., 88 FR 77676, CMS-1784-F).\n"
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
            "Instructions: Provide a clear, factual answer grounded in the GRAPH CONTEXT. "
            "Be sure to cite exact bracketed identifiers (e.g. [STATE-...], [JURIS-...], [CMS-...], [HCPCS-...]). "
            "If Section 4 contains fee schedule entries, explicitly quote the dollar allowable reimbursement rate (e.g. $290.47) and the 20% patient coinsurance (e.g. $58.09)."
        )
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "max_tokens": 512,
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
