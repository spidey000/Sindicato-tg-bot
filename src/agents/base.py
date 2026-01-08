import os
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class AgentBase(ABC):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        # In a real implementation, we would initialize the OpenAI client here
        # or use requests directly if the library is an issue.
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    def generate_draft(self, context: str) -> str:
        """
        Generates a draft document based on the user context using the agent's persona.
        """
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Returning simulated draft.")
            return self.simulated_draft(context)

        # Here we would call the LLM
        # For now, we simulate the AI response
        return self.simulated_draft(context)

    def simulated_draft(self, context: str) -> str:
        return f"[BORRADOR GENERADO POR IA - {self.__class__.__name__}]\n\n" \
               f"Contexto: {context}\n\n" \
               f"Aquí iría el texto legal completo generado por el modelo..."
