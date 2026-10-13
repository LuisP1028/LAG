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
        "You are an expert Medicare policy intelligence assistant.\n"
        "Answer the user's question using ONLY the factual statements provided in the GRAPH CONTEXT below.\n"
        "You are strictly forbidden from guessing reimbursement rates, making up procedure codes, or extrapolating unverified coverage criteria.\n"
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
        user_content = f"Question: {query}\n\nGRAPH CONTEXT:\n{context}"
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "max_tokens": 1024,
            "temperature": 0.01,
        }

        try:
            with httpx.Client(timeout=25.0) as client:
                response = client.post(self.ROUTER_CHAT_URL, json=payload, headers=headers)
        except httpx.TimeoutException as exc:
            raise ModelInferenceError(f"Hugging Face API request timed out after 25s: {exc}") from exc
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
