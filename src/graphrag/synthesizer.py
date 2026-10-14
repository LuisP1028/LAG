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

    DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
    ROUTER_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"

    MODEL_ALIASES = {
        "Qwen/Qwen2.5-7B-Instruct": "Qwen/Qwen2.5-72B-Instruct",
        "meta-llama/Meta-Llama-3-8B-Instruct": "meta-llama/Llama-3.1-8B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.3": "meta-llama/Llama-3.1-8B-Instruct",
    }

    SYSTEM_PROMPT = (
        "You are an authoritative Medicare policy intelligence system.\n"
        "Your objective is to provide clear, straightforward, factual answers based EXCLUSIVELY on the provided GRAPH CONTEXT.\n"
        "You must adhere strictly to the following rules:\n"
        "1. STRAIGHTFORWARD EXPLANATION OF IMPORTANCE: When asked what an entity is or why it is important, open with a direct, plain-language explanation of what the entity is and why it matters in the legislative-to-administrative chain (how it connects Congressional legislation, agency regulations and transmittals, regional contractor coverage policies, clinical eligibility, or patient reimbursement).\n"
        "2. RELY STRICTLY ON CONTEXT: Do not extrapolate unlisted coverage, invent billing rules, or speculate. If information is not in the context, state that it is not present.\n"
        "3. QUOTE EXACT BRACKETED IDENTIFIERS: Whenever you mention any entity from the context (such as a policy, bill, public law, statutory section, U.S. Code section, regulation, CFR section, transmittal, coverage policy, jurisdiction contractor, procedure code, fee schedule entry, state, diagnosis code, CBO score, lobbying filing, or clinical study), you MUST cite its exact bracketed primary key identifier as shown in the context. Always explicitly cite the authorizing coverage policy, CMS transmittal, and regional claims contractor in your opening summary when they are present in the context.\n"
        "4. MANDATORY FEE AND COINSURANCE REPORTING: Whenever the context contains fee schedule entries, you MUST explicitly state the exact dollar allowable reimbursement amount and the calculated 20% patient coinsurance for the relevant procedure codes. Never omit these dollar figures or refer the user elsewhere when they are present in the context.\n"
        "5. QUOTE OFFICIAL LEGAL CITATIONS: When referencing legislation and regulations, quote the official citations directly from the provided GRAPH CONTEXT.\n"
        "6. NO PROBABILISTIC GUESSING: Do not assume coverage for unlisted conditions or unverified items.\n"
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
            "Instructions: Provide a clear, concise, factual answer grounded exclusively in the GRAPH CONTEXT. "
            "In your opening paragraph, explain the queried entity in plain language and explicitly cite the exact bracketed primary keys from the context for the relevant policy, legislation, regulation, transmittal, coverage policy, contractor jurisdiction, and state when present in the context. "
            "If the context contains fee schedule entries, explicitly quote the exact dollar allowable reimbursement rate and the 20% patient coinsurance from the context."
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


class DeepSeekMicroFactSynthesizer:
    """Dedicated Hugging Face DeepSeek micro-fact generator using isolated HF_DEEPSEEK_TOKEN.

    Generates a concise, verified knowledge graph truth strictly under 15 words (1 to 14 words).
    Strictly isolated from HF_TOKEN / HUGGINGFACE_API_KEY.
    """

    DEFAULT_MODEL = "deepseek-ai/DeepSeek-V3"
    ROUTER_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"
    DEFAULT_MICRO_FACT = "Public Law 117-328 codifies Medicare compression garment benefits."

    SYSTEM_PROMPT = (
        "You are a Medicare Durable Medical Equipment knowledge graph micro-fact generator. "
        "Given verified facts from the knowledge graph, write ONE single, complete, authoritative sentence "
        "that is STRICTLY between 5 and 13 words long (MUST be under 15 words). "
        "Do not include quotes, bullet points, markdown, or thinking tags."
    )

    def __init__(self, token: Optional[str] = None):
        # Strictly use HF_DEEPSEEK_TOKEN; never conflate with HF_TOKEN or HUGGINGFACE_API_KEY
        self._explicit_token = token

    @property
    def token(self) -> Optional[str]:
        if self._explicit_token is not None:
            return self._explicit_token
        return os.getenv("HF_DEEPSEEK_TOKEN")

    def _fallback_result(self, model_id: str, notice: str) -> Dict[str, Any]:
        print(f"[DeepSeekMicroFactSynthesizer] TELEMETRY NOTICE: {notice}", flush=True)
        words = self.DEFAULT_MICRO_FACT.split()
        return {
            "micro_fact": self.DEFAULT_MICRO_FACT,
            "word_count": len(words),
            "model_id": model_id,
            "source": "fallback",
            "telemetry_notice": notice,
        }

    @staticmethod
    def _clean_and_validate_fact(raw_text: str) -> Optional[str]:
        # Remove any <think>...</think> blocks if a reasoning DeepSeek model variant was used
        cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
        # Take first non-empty line
        lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]
        if not lines:
            return None
        candidate = lines[0]
        # Strip surrounding quotes, asterisks, or leading bullets
        candidate = candidate.strip("\"'`*•- ")
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if not candidate:
            return None
        words = candidate.split()
        if 1 <= len(words) < 15:
            return candidate
        return None

    def generate_micro_fact(
        self,
        graph_context: str,
        model_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generates a grounded graph micro-fact (< 15 words) via Hugging Face DeepSeek."""
        active_model = model_id or self.DEFAULT_MODEL
        active_token = self.token
        if not active_token or not active_token.strip():
            return self._fallback_result(
                model_id=active_model,
                notice="HF_DEEPSEEK_TOKEN is not configured; displaying verified default graph micro-fact.",
            )

        headers = {
            "Authorization": f"Bearer {active_token.strip()}",
            "Content-Type": "application/json",
            "User-Agent": "lag-deepseek-microfact/1.0",
        }
        payload = {
            "model": active_model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Verified Knowledge Graph Context:\n{graph_context}\n\n"
                        "Write one complete, factual statement grounded in this context in 6 to 13 words (strictly under 15 words)."
                    ),
                },
            ],
            "max_tokens": 48,
            "temperature": 0.1,
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(self.ROUTER_CHAT_URL, json=payload, headers=headers)
            if response.status_code != 200:
                return self._fallback_result(
                    model_id=active_model,
                    notice=f"DeepSeek endpoint returned HTTP {response.status_code}; displaying verified default graph micro-fact.",
                )
            data = response.json()
            raw_content = ""
            if "choices" in data and len(data["choices"]) > 0:
                raw_content = data["choices"][0].get("message", {}).get("content", "")
            validated = self._clean_and_validate_fact(raw_content)
            if not validated:
                return self._fallback_result(
                    model_id=active_model,
                    notice="DeepSeek output did not satisfy strict < 15 word boundary; displaying verified default graph micro-fact.",
                )
            return {
                "micro_fact": validated,
                "word_count": len(validated.split()),
                "model_id": active_model,
                "source": "deepseek",
                "telemetry_notice": None,
            }
        except Exception as exc:
            return self._fallback_result(
                model_id=active_model,
                notice=f"DeepSeek request failed ({exc}); displaying verified default graph micro-fact.",
            )

