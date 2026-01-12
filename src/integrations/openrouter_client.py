import aiohttp
import asyncio
import json
import logging
from src.config import (
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL, 
    MODEL_PRIMARY, 
    MODEL_FALLBACK,
    PRIMARY_DRAFT_MODEL,
    FALLBACK_DRAFT_MODEL,
    REPAIR_MODEL,
    SAVE_RAW_LLM_RESPONSES
)

logger = logging.getLogger(__name__)

# Model-specific max_tokens configuration
# Maps model name patterns to their optimal max_tokens value
MODEL_MAX_TOKENS = {
    "deepseek/deepseek-r1": 16384,
    "deepseek/deepseek-chat": 8192,
    "google/gemma-3-27b": 8192,
    "moonshotai/moonlight": 8192,
    "qwen/qwen3-4b": 4096,
    "anthropic/claude": 8192,
    "openai/gpt-4": 8192,
}

DEFAULT_MAX_TOKENS = 8192

def get_max_tokens_for_model(model: str) -> int:
    """Returns the optimal max_tokens value for a given model."""
    model_lower = model.lower()
    for pattern, max_tokens in MODEL_MAX_TOKENS.items():
        if pattern in model_lower:
            return max_tokens
    return DEFAULT_MAX_TOKENS

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
        self.last_raw_response = None

    async def completion(self, messages: list, model: str = None, response_format: dict = None, task_type: str = None) -> str:
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
            content = await self._make_request(messages, target_model, response_format)
            
            # Check if JSON repair is needed
            if response_format and response_format.get("type") == "json_object":
                try:
                    json.loads(content)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {target_model}. Attempting repair with {REPAIR_MODEL}.")
                    content = await self._repair_json(content, response_format)
            
            return content
            
        except Exception as e:
            logger.error(f"Error with primary model {target_model}: {e}")
            if target_model != fallback:
                logger.info(f"Retrying with fallback model: {fallback}")
                try:
                    content = await self._make_request(messages, fallback, response_format)
                    
                    # Check if JSON repair is needed for fallback
                    if response_format and response_format.get("type") == "json_object":
                        try:
                            json.loads(content)
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON from fallback {fallback}. Attempting repair with {REPAIR_MODEL}.")
                            content = await self._repair_json(content, response_format)
                    
                    return content
                except Exception as e2:
                    logger.error(f"Error with fallback model {fallback}: {e2}")
                    return f"Error generating text: {e2}"
            else:
                return f"Error generating text: {e}"

    async def _repair_json(self, invalid_content: str, original_format: dict) -> str:
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
        
        # The `original_format` contains the schema. We must pass it to the repair model.
        repair_format = original_format
        
        try:
            # For qwen, response_format was removed in _make_request.
            # So we pass it as a regular param here, and the model must rely on the prompt.
            # This is a bit of a hack, but given the previous failures, we try to be flexible.
            if "qwen" in REPAIR_MODEL.lower():
                repaired_content = await self._make_request(repair_messages, REPAIR_MODEL, None)
            else:
                repaired_content = await self._make_request(repair_messages, REPAIR_MODEL, repair_format)
            
            # DEBUG: Log the repair attempt response
            if SAVE_RAW_LLM_RESPONSES and self.last_raw_response:
                raw_response_json = json.dumps(self.last_raw_response, indent=2)
                print("\n--- RAW LLM RESPONSE (JSON Repair Attempt) ---")
                print(raw_response_json)
                logger.debug(f"RAW LLM RESPONSE (JSON Repair Attempt):\n{raw_response_json}")

            return repaired_content
        except Exception as e:
            logger.error(f"JSON repair failed: {e}")
            return invalid_content

    async def _make_request(self, messages: list, model: str, response_format: dict = None) -> str:
        max_tokens = get_max_tokens_for_model(model)
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        if response_format and "deepseek" in model.lower():
            payload["response_format"] = response_format
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=payload,
                        timeout=300
                    ) as response:
                        # Check for non-200 status codes first and log detailed error
                        if response.status != 200:
                            error_text = await response.text()
                            logger.warning(
                                f"Attempt {attempt + 1}/{max_retries} for {model} failed with status {response.status}. "
                                f"Reason: {response.reason}. Full Response: {error_text}"
                            )
                            # Raise a generic exception to trigger the retry logic
                            response.raise_for_status()

                        # If status is 200, proceed
                        data = await response.json()
                        self.last_raw_response = data
                        
                        if "choices" in data and len(data["choices"]) > 0:
                            return data["choices"][0]["message"]["content"]
                        else:
                            raise ValueError(f"Invalid response from OpenRouter: {data}")
            
            except (aiohttp.ClientError, ValueError) as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} for {model} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                else:
                    logger.error(f"All attempts failed for model {model}.")
                    raise e
