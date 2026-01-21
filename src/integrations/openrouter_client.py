import aiohttp
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
from src.utils.retry import async_retry
from src.utils.monitoring import track_api_call

logger = logging.getLogger(__name__)

# Model-specific max_tokens configuration
# Maps model name patterns to their optimal max_tokens value
MODEL_MAX_TOKENS = {
    "deepseek/deepseek-r1": 32768,
    "deepseek/deepseek-chat": 8192,
    "google/gemma-3-27b": 8192,
    "moonshotai/moonlight": 8192,
    "qwen/qwen3-4b": 4096,
    "anthropic/claude": 8192,
    "openai/gpt-4": 8192,
}

DEFAULT_MAX_TOKENS = 8192

def get_max_tokens_for_model(model: str) -> int:
    """
    Returns the optimal max_tokens value for a given OpenRouter model.

    Different models have different maximum token limits. This function matches
    the model name against known patterns and returns the appropriate limit.

    Args:
        model (str): The model name/identifier (e.g., "deepseek/deepseek-r1").

    Returns:
        int: The optimal max_tokens value for the model. Defaults to 8192 if
             the model is not in the known patterns.

    Example:
        >>> get_max_tokens_for_model("deepseek/deepseek-r1")
        32768
        >>> get_max_tokens_for_model("unknown/model")
        8192
    """
    model_lower = model.lower()
    for pattern, max_tokens in MODEL_MAX_TOKENS.items():
        if pattern in model_lower:
            return max_tokens
    return DEFAULT_MAX_TOKENS

class OpenRouterClient:
    def __init__(self):
        """
        Initialize OpenRouter API client for LLM completions.

        Configures HTTP headers and authentication for OpenRouter API access.
        Uses DeepSeek R1 as primary model with Gemma 3 as fallback.

        Attributes:
            api_key: OpenRouter API key for authentication.
            base_url: Base URL for OpenRouter API endpoints.
            headers: HTTP headers including auth, content-type, and app identification.
            last_raw_response: Stores the most recent raw API response for debugging.

        Note:
            OpenRouter requires HTTP-Referer and X-Title headers for ranking and attribution.
            Raw responses are stored when SAVE_RAW_LLM_RESPONSES is enabled in config.
        """
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

    async def generate_from_template(
        self, 
        template: str, 
        context: str, 
        research: str,
        model: str = None
    ) -> str:
        """
        Generates a filled legal document by combining:
        - Template structure (with {{DYNAMIC}} placeholders)
        - User context (facts of the case)
        - Perplexity research (legal grounds, verbatim)
        
        Uses MODEL_PRIMARY by default.
        Returns the complete document as markdown.
        """
        target_model = model or MODEL_PRIMARY
        
        system_prompt = (
            "Eres un abogado laboralista español experto en redacción de documentos legales. "
            "Tu tarea es rellenar una plantilla de documento legal usando los hechos del caso "
            "y la investigación jurídica proporcionada.\n\n"
            "INSTRUCCIONES:\n"
            "1. Mantén EXACTAMENTE la estructura y formato de la plantilla\n"
            "2. Los campos marcados como [DATO FIJO] o [HARDCODED] NO deben modificarse\n"
            "3. Rellena TODOS los campos {{PLACEHOLDER}} con información apropiada\n"
            "4. Usa la investigación jurídica para los fundamentos de derecho\n"
            "5. Redacta en estilo jurídico formal español\n"
            "6. No inventes datos que no estén en los hechos o la investigación\n"
            "7. Si falta información para un campo, usa '[PENDIENTE DE COMPLETAR]'\n"
            "8. El documento final debe estar listo para revisión humana\n\n"
            "IMPORTANTE: Devuelve SOLO el documento rellenado, sin explicaciones adicionales."
        )
        
        user_prompt = (
            f"## PLANTILLA DEL DOCUMENTO\n\n{template}\n\n"
            f"---\n\n"
            f"## HECHOS DEL CASO (proporcionados por el usuario)\n\n{context}\n\n"
            f"---\n\n"
            f"## INVESTIGACIÓN JURÍDICA (Perplexity)\n\n{research}\n\n"
            f"---\n\n"
            "Genera el documento legal completo rellenando todos los campos {{PLACEHOLDER}} "
            "de la plantilla. Mantén el formato markdown."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            content = await self._make_request(messages, target_model, None)
            
            # Validation: Trigger retry if content is empty or error-like
            if not content or len(content) < 50:
                 raise ValueError("Generated content is empty or too short.")
            
            logger.info(f"✅ Document generated from template. Model: {target_model}. Length: {len(content)} chars.")
            return content
        except Exception as e:
            logger.error(f"Error generating document from template with {target_model}: {e}")
            # Try fallback
            if target_model != MODEL_FALLBACK:
                logger.info(f"Retrying document generation with fallback: {MODEL_FALLBACK}")
                try:
                    content = await self._make_request(messages, MODEL_FALLBACK, None)
                    logger.info(f"✅ Document generated (fallback). Model: {MODEL_FALLBACK}. Length: {len(content)} chars.")
                    return content
                except Exception as e2:
                    logger.error(f"Fallback also failed: {e2}")
                    raise e2
            raise e

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

    @async_retry(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        exceptions=(aiohttp.ClientError, aiohttp.ClientTimeout, ConnectionError, OSError)
    )
    @track_api_call('openrouter')
    async def _make_request(self, messages: list, model: str, response_format: dict = None) -> str:
        """
        Make HTTP request to OpenRouter API with retry logic.

        Includes retry decorator for transient failures like:
        - Network timeouts
        - Connection errors
        - Temporary API unavailability

        Args:
            messages: Chat messages for the API
            model: Model identifier to use
            response_format: Optional JSON schema for structured output

        Returns:
            Generated content string

        Raises:
            aiohttp.ClientError: For persistent API failures
            ValueError: For invalid API responses
        """
        max_tokens = get_max_tokens_for_model(model)
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens
        }

        if response_format and "deepseek" in model.lower():
            payload["response_format"] = response_format

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=300
            ) as response:
                # Check for non-200 status codes
                if response.status != 200:
                    error_text = await response.text()
                    # Non-200 status codes are not retried (they're not transient failures)
                    error_msg = (
                        f"OpenRouter API returned status {response.status} for model {model}. "
                        f"Reason: {response.reason}. Response: {error_text}"
                    )
                    logger.error(f"❌ {error_msg}")
                    raise aiohttp.ClientError(error_msg)

                # If status is 200, proceed
                data = await response.json()
                self.last_raw_response = data

                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    raise ValueError(f"Invalid response from OpenRouter: {data}")
