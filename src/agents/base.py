import os
import logging
import json
from abc import ABC, abstractmethod
from src.integrations.openrouter_client import OpenRouterClient
from src.integrations.perplexity_client import PerplexityClient

logger = logging.getLogger(__name__)

class AgentBase(ABC):
    def __init__(self):
        self.llm_client = OpenRouterClient()
        self.pplx_client = PerplexityClient()
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    def generate_draft(self, context: str) -> str:
        """
        Generates a draft document based on the user context using the agent's persona.
        """
        system_prompt = self.get_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ]
        
        logger.info(f"Generating draft with {self.__class__.__name__} using OpenRouter...")
        return self.llm_client.completion(messages)

    async def generate_structured_draft_verified(self, context: str) -> dict:
        """
        Generates a draft, verifies it with Perplexity (Sonar LLM), and refines it.
        Returns a dict with 'summary', 'content', and 'verification_status'.
        """
        # 1. Generate Initial Draft
        initial_data = self.generate_structured_draft(context)
        initial_content = initial_data.get("content", "")
        
        if not initial_content:
            initial_data["verification_status"] = "Skipped (No Content)"
            return initial_data

        logger.info(f"Verifying draft with Perplexity...")
        
        # 2. Verify (Grounding)
        verification_feedback = await self.pplx_client.verify_draft(initial_content)
        
        if verification_feedback:
            logger.info("Draft verified. Refining...")
            
            # 3. Refine
            refinement_instruction = f"VERIFICACIÓN LEGAL OBLIGATORIA:\n{verification_feedback}"
            refined_content = self.refine_draft(initial_content, refinement_instruction)
            
            initial_data["content"] = refined_content
            initial_data["verification_status"] = "Verified"
        else:
            logger.warning("Verification failed. Returning initial draft.")
            initial_data["verification_status"] = "Verification Failed"
            
        return initial_data

    def generate_structured_draft(self, context: str) -> dict:
        """
        Generates a draft and a short summary, returning a JSON-parsed dictionary.
        Expected keys: 'summary', 'content'.
        """
        system_prompt = self.get_system_prompt()
        json_instruction = (
            "\n\nIMPORTANT: Return your response in pure JSON format with two keys:\n"
            "- 'summary': A concise summary of the topic (max 5-7 words), e.g., 'Falta de EPIs'.\n"
            "- 'content': The full drafted document content.\n"
            "Do not include markdown formatting (like ```json) around the JSON."
        )
        
        messages = [
            {"role": "system", "content": system_prompt + json_instruction},
            {"role": "user", "content": context}
        ]
        
        logger.info(f"Generating structured draft with {self.__class__.__name__}...")
        raw_response = self.llm_client.completion(messages)
        
        try:
            # Clean potential markdown code blocks if the LLM ignores instructions
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            data = json.loads(cleaned_response.strip())
            
            # Ensure keys exist
            if "summary" not in data:
                data["summary"] = f"Caso {context[:10]}..."
            if "content" not in data:
                data["content"] = raw_response # Fallback
                
            return data
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from LLM. Returning fallback structure.")
            return {
                "summary": f"Caso {context[:15]}...",
                "content": raw_response
            }

    def refine_draft(self, current_content: str, new_info: str) -> str:
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
        return self.llm_client.completion(messages)

        """
        Generates a draft and a short summary, returning a JSON-parsed dictionary.
        Expected keys: 'summary', 'content'.
        """
        system_prompt = self.get_system_prompt()
        json_instruction = (
            "\n\nIMPORTANT: Return your response in pure JSON format with two keys:\n"
            "- 'summary': A concise summary of the topic (max 5-7 words), e.g., 'Falta de EPIs'.\n"
            "- 'content': The full drafted document content.\n"
            "Do not include markdown formatting (like ```json) around the JSON."
        )
        
        messages = [
            {"role": "system", "content": system_prompt + json_instruction},
            {"role": "user", "content": context}
        ]
        
        logger.info(f"Generating structured draft with {self.__class__.__name__}...")
        raw_response = self.llm_client.completion(messages)
        
        try:
            # Clean potential markdown code blocks if the LLM ignores instructions
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            data = json.loads(cleaned_response.strip())
            
            # Ensure keys exist
            if "summary" not in data:
                data["summary"] = f"Caso {context[:10]}..."
            if "content" not in data:
                data["content"] = raw_response # Fallback
                
            return data
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from LLM. Returning fallback structure.")
            return {
                "summary": f"Caso {context[:15]}...",
                "content": raw_response
            }

    def refine_draft(self, current_content: str, new_info: str) -> str:
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
        return self.llm_client.completion(messages)
