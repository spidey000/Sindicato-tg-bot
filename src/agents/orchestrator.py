from src.agents.inspector import InspectorLaboralAgent

class AgentOrchestrator:
    def __init__(self):
        self.inspector = InspectorLaboralAgent()
        # Initialize other agents here

    def get_agent_for_command(self, command: str):
        if command == "/denuncia":
            return self.inspector
        # Add other mappings
        return self.inspector # Default

agent_orchestrator = AgentOrchestrator()
