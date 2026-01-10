import os
import logging
import json
from abc import ABC, abstractmethod
from src.integrations.openrouter_client import OpenRouterClient
from src.integrations.perplexity_client import PerplexityClient
from src.integrations.notion_client import DelegadoNotionClient

logger = logging.getLogger(__name__)

class AgentBase(ABC):
    def __init__(self):
        self.llm_client = OpenRouterClient()
        self.pplx_client = PerplexityClient()
        self.notion_client = DelegadoNotionClient()
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    async def generate_draft(self, context: str) -> str:
        """
        Generates a draft document based on the user context using the agent's persona.
        """
        system_prompt = self.get_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ]
        
        logger.info(f"Generating draft with {self.__class__.__name__} using OpenRouter...")
        return await self.llm_client.completion(messages, task_type="DRAFT")

    async def verify_draft_content(self, content: str, thesis: str = "", specific_point: str = "", area: str = "") -> str:
        """
        Public method to verify draft content using Perplexity.
        """
        return await self.pplx_client.verify_draft(
            context=content,
            thesis=thesis,
            specific_point=specific_point,
            area=area
        )

    async def refine_draft_with_feedback(self, content: str, feedback: str) -> str:
        """
        Refines the draft based on explicit verification feedback.
        """
        refinement_instruction = f"VERIFICACIÓN LEGAL OBLIGATORIA:\n{feedback}"
        return await self.refine_draft(content, refinement_instruction)

    async def generate_structured_draft_verified(self, context: str, notion_page_id: str = None) -> dict:
        """
        Generates a draft, verifies it with Perplexity (Sonar LLM), and refines it.
        Returns a dict with 'summary', 'content', and 'verification_status'.
        """
        # 1. Generate Initial Draft (includes metadata: thesis, specific_point, area)
        initial_data = await self.generate_structured_draft_with_retry(context)
        initial_content = initial_data.get("content", "")
        
        if not initial_content:
            initial_data["verification_status"] = "Skipped (No Content)"
            return initial_data

        logger.info(f"Verifying draft with Perplexity...")
        
        # 2. Verify (Grounding) using extracted metadata
        verification_feedback = await self.pplx_client.verify_draft(
            context=initial_content,
            thesis=initial_data.get("thesis", ""),
            specific_point=initial_data.get("specific_point", ""),
            area=initial_data.get("area", "")
        )
        
        if verification_feedback:
            logger.info("Draft verified. Refining...")
            
            # 3. Audit Log (Notion)
            if notion_page_id:
                logger.info(f"Logging verification report to Notion page {notion_page_id}...")
                self.notion_client.append_verification_report(notion_page_id, verification_feedback)

            # 4. Refine
            refinement_instruction = f"VERIFICACIÓN LEGAL OBLIGATORIA:\n{verification_feedback}"
            refined_content = await self.refine_draft(initial_content, refinement_instruction)
            
            initial_data["content"] = refined_content
            initial_data["verification_status"] = "Verified"
        else:
            logger.warning("Verification failed. Returning initial draft.")
            initial_data["verification_status"] = "Verification Failed"
            
        return initial_data

    async def generate_structured_draft(self, context: str) -> dict:
        """
        Legacy wrapper for generate_structured_draft_with_retry.
        """
        return await self.generate_structured_draft_with_retry(context)

    async def generate_structured_draft_with_retry(self, context: str) -> dict:
        """
        Generates a draft and a short summary, returning a JSON-parsed dictionary.
        Expected keys: 'summary', 'content'.
        Retries up to 3 times if the output is not valid JSON or content is too short.
        """
        system_prompt = self.get_system_prompt()
        json_instruction = (
            "\n\nIMPORTANT: Return your response in pure JSON format with the following keys:\n"
            "- 'summary': A concise summary of the topic (max 5-7 words), e.g., 'Falta de EPIs'.\n"
            "- 'content': The full drafted document content. CRITICAL: You must escape all newlines within the content string using \\n. Do not use literal newlines inside the string value.\n"
            "- 'thesis': The central legal argument (e.g., 'Nulidad del despido por discriminación').\n"
            "- 'specific_point': Key legal doctrine to research (e.g., 'Inversión de la carga de la prueba').\n"
            "- 'area': Specific labor law domain (e.g., 'Despido', 'Modificación sustancial').\n"
            "Do not include markdown formatting (like ```json) around the JSON."
        )
        
        messages = [
            {"role": "system", "content": system_prompt + json_instruction},
            {"role": "user", "content": context}
        ]
        
        max_retries = 3
        
        for attempt in range(max_retries):
            logger.info(f"Generating structured draft with {self.__class__.__name__} (Attempt {attempt + 1}/{max_retries})...")
            
            # Request JSON object format
            raw_response = await self.llm_client.completion(
                messages, 
                response_format={"type": "json_object"},
                task_type="DRAFT"
            )
            
            try:
                # Clean potential markdown code blocks if the LLM ignores instructions
                cleaned_response = raw_response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                
                cleaned_response = cleaned_response.strip()
                
                # Additional cleanup: find first { and last }
                first_brace = cleaned_response.find("{")
                last_brace = cleaned_response.rfind("}")
                if first_brace != -1 and last_brace != -1:
                    cleaned_response = cleaned_response[first_brace:last_brace+1]
                
                data = json.loads(cleaned_response, strict=False)
                
                # Ensure keys exist
                if "summary" not in data:
                    data["summary"] = f"Caso {context[:10]}..."
                if "content" not in data:
                    data["content"] = raw_response # Fallback
                
                # Metadata defaults
                if "thesis" not in data:
                    data["thesis"] = ""
                if "specific_point" not in data:
                    data["specific_point"] = ""
                if "area" not in data:
                    data["area"] = ""

                # Validation: Check content length > 50 chars
                if len(data["content"]) <= 50:
                    logger.warning(f"Draft content too short ({len(data['content'])} chars) on attempt {attempt + 1}.")
                    raise ValueError("Content too short")
                    
                return data
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Validation failed on attempt {attempt + 1}: {e}")
                logger.debug(f"Raw response snippet: {raw_response[:200]}...")
                if attempt == max_retries - 1:
                    logger.error("All validation attempts failed.")
                    raise ValueError("Failed to generate valid draft after multiple attempts.")
                # Continue to next iteration/retry
        
        raise ValueError("Unexpected error in retry loop.")

    async def refine_draft(self, current_content: str, new_info: str) -> str:
        """
        Refines an existing draft with new information.
        """
        system_prompt = self.get_system_prompt()
        refinement_prompt = f"""
        Has generado previamente este borrador:
        {current_content}

        El usuario te proporciona nueva información:
        {new_info}

        TAREA:
        1. Identifica qué sección del documento debe actualizarse.
        2. Integra la nueva información manteniendo la coherencia estructural.
        3. Si la información contradice algo previamente escrito, prioriza lo más reciente.
        4. Regenera el documento COMPLETO actualizado.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": refinement_prompt}
        ]
        
        logger.info(f"Refining draft with {self.__class__.__name__}...")
        return await self.llm_client.completion(messages, task_type="REFINEMENT")
