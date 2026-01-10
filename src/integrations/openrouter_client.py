import requests
import json
import logging
from src.config import (
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL, 
    MODEL_PRIMARY, 
    MODEL_FALLBACK,
    PRIMARY_DRAFT_MODEL,
    FALLBACK_DRAFT_MODEL,
    REPAIR_MODEL
)

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

    def completion(self, messages: list, model: str = None, response_format: dict = None, task_type: str = None) -> str:
        """
        Generates a completion using OpenRouter.
        Tries the primary model first, then falls back to the secondary model.
        :param task_type: Optional task type ('DRAFT', 'REFINEMENT', 'REPAIR') to determine model hierarchy.
        """
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not set. Returning simulation.")
            return "[SIMULATION] OpenRouter API Key missing. This is a simulated response."

        # Determine Primary and Fallback models based on task type
        primary = MODEL_PRIMARY
        fallback = MODEL_FALLBACK

        if task_type == "DRAFT":
            primary = PRIMARY_DRAFT_MODEL
            fallback = FALLBACK_DRAFT_MODEL

        target_model = model or primary
        
        try:
            content = self._make_request(messages, target_model, response_format)
            
            # Check if JSON repair is needed
            if response_format and response_format.get("type") == "json_object":
                try:
                    json.loads(content)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {target_model}. Attempting repair with {REPAIR_MODEL}.")
                    content = self._repair_json(content, response_format)
            
            return content
            
        except Exception as e:
            logger.error(f"Error with primary model {target_model}: {e}")
            if target_model != fallback:
                logger.info(f"Retrying with fallback model: {fallback}")
                try:
                    content = self._make_request(messages, fallback, response_format)
                    
                    # Check if JSON repair is needed for fallback
                    if response_format and response_format.get("type") == "json_object":
                        try:
                            json.loads(content)
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON from fallback {fallback}. Attempting repair with {REPAIR_MODEL}.")
                            content = self._repair_json(content, response_format)
                    
                    return content
                except Exception as e2:
                    logger.error(f"Error with fallback model {fallback}: {e2}")
                    return f"Error generating text: {e2}"
            else:
                return f"Error generating text: {e}"

    def _repair_json(self, invalid_content: str, original_format: dict) -> str:
        """
        Attempts to repair malformed JSON using the REPAIR_MODEL.
        """
        schema_hint = original_format.get("schema", "JSON object")
        repair_prompt = (
            f"Convert this text into valid JSON matching this schema: {schema_hint}\n\n"
            f"{invalid_content}"
        )
        
        repair_messages = [
            {"role": "system", "content": "You are a JSON repair assistant. Output ONLY valid JSON."},
            {"role": "user", "content": repair_prompt}
        ]
        
        # Use qwen with structured_outputs parameter
        repair_format = {"type": "json_object"}
        
        try:
            repaired_content = self._make_request(repair_messages, REPAIR_MODEL, repair_format)
            return repaired_content
        except Exception as e:
            logger.error(f"JSON repair failed: {e}")
            return invalid_content

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
