import requests
import json
import logging
from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_PRIMARY, MODEL_FALLBACK

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/sindicato-tg-bot", # Required by OpenRouter for rankings
            "X-Title": "Marxnager"
        }

    def completion(self, messages: list, model: str = None, response_format: dict = None) -> str:
        """
        Generates a completion using OpenRouter.
        Tries the primary model first, then falls back to the secondary model.
        """
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not set. Returning simulation.")
            return "[SIMULATION] OpenRouter API Key missing. This is a simulated response."

        target_model = model or MODEL_PRIMARY
        
        try:
            return self._make_request(messages, target_model, response_format)
        except Exception as e:
            logger.error(f"Error with primary model {target_model}: {e}")
            if target_model != MODEL_FALLBACK:
                logger.info(f"Retrying with fallback model: {MODEL_FALLBACK}")
                try:
                    return self._make_request(messages, MODEL_FALLBACK, response_format)
                except Exception as e2:
                    logger.error(f"Error with fallback model {MODEL_FALLBACK}: {e2}")
                    return f"Error generating text: {e2}"
            else:
                return f"Error generating text: {e}"

    def _make_request(self, messages: list, model: str, response_format: dict = None) -> str:
        payload = {
            "model": model,
            "messages": messages
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    data=json.dumps(payload),
                    timeout=60 # Reasonable timeout for LLMs
                )
                
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    raise ValueError(f"Invalid response from OpenRouter: {data}")
            
            except (requests.exceptions.RequestException, ValueError) as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {model}: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay * (2 ** attempt)) # Exponential backoff
                else:
                    raise e
