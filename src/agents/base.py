import os
import logging
from abc import ABC, abstractmethod
from src.integrations.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

class AgentBase(ABC):
    def __init__(self):
        self.llm_client = OpenRouterClient()
        
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
