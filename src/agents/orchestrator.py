from src.agents.inspector import InspectorLaboralAgent
from src.agents.litigante import LitiganteProcesalAgent
from src.agents.comunicador import ComunicadorCorporativoAgent

class AgentOrchestrator:
    def __init__(self):
        self.inspector = InspectorLaboralAgent()
        self.litigante = LitiganteProcesalAgent()
        self.comunicador = ComunicadorCorporativoAgent()

    def get_agent_for_command(self, command: str):
        if command == "/denuncia":
            return self.inspector
        elif command == "/demanda":
            return self.litigante
        elif command == "/email":
            return self.comunicador
        
        # Default fallback
        return self.inspector

agent_orchestrator = AgentOrchestrator()