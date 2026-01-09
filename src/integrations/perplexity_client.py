import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PerplexityClient:
    def __init__(self):
        self.primary_key = os.getenv("PERPLEXITY_API_KEY_PRIMARY")
        self.fallback_key = os.getenv("PERPLEXITY_API_KEY_FALLBACK")
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro" # Using an online model for grounding

    async def verify_draft(self, draft_text: str) -> Optional[str]:
        """
        Uses Perplexity API to verify and ground the draft text.
        Attempts to use the primary key first, then the fallback key.
        """
        
        system_prompt = (
            "You are a rigorous legal verification assistant. "
            "Your task is to review the provided legal draft, cross-reference it with "
            "current Spanish legislation and jurisprudence (using your online capabilities), "
            "and provide a grounded, verified version or a critique with citations. "
            "Focus on accuracy and legal validity."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please verify and ground the following draft:\n\n{draft_text}"}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1
        }

        # Try Primary Key
        if self.primary_key:
            result = await self._make_request(self.primary_key, payload)
            if result:
                return result
            logger.warning("Perplexity Primary Key failed. Attempting Fallback.")
        else:
            logger.warning("Perplexity Primary Key not configured.")

        # Try Fallback Key
        if self.fallback_key:
            result = await self._make_request(self.fallback_key, payload)
            if result:
                return result
            logger.error("Perplexity Fallback Key also failed.")
        else:
            logger.warning("Perplexity Fallback Key not configured.")

        return None

    async def _make_request(self, api_key: str, payload: dict) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Perplexity API Error: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Perplexity Connection Error: {e}")
            return None
