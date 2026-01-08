import unittest
from src.agents.orchestrator import AgentOrchestrator
from src.agents.inspector import InspectorLaboralAgent
from src.agents.litigante import LitiganteProcesalAgent
from src.agents.comunicador import ComunicadorCorporativoAgent

class TestAgents(unittest.TestCase):
    def setUp(self):
        self.orchestrator = AgentOrchestrator()

    def test_orchestrator_routing(self):
        self.assertIsInstance(self.orchestrator.get_agent_for_command("/denuncia"), InspectorLaboralAgent)
        self.assertIsInstance(self.orchestrator.get_agent_for_command("/demanda"), LitiganteProcesalAgent)
        self.assertIsInstance(self.orchestrator.get_agent_for_command("/email"), ComunicadorCorporativoAgent)
        self.assertIsInstance(self.orchestrator.get_agent_for_command("/unknown"), InspectorLaboralAgent)

    def test_inspector_output(self):
        agent = InspectorLaboralAgent()
        draft = agent.generate_draft("Falta de medidas de seguridad")
        self.assertIn("A LA INSPECCIÓN PROVINCIAL", draft)
        self.assertIn("Falta de medidas de seguridad", draft)

    def test_litigante_output(self):
        agent = LitiganteProcesalAgent()
        draft = agent.generate_draft("Despido injustificado")
        self.assertIn("AL JUZGADO DE LO SOCIAL", draft)
        self.assertIn("Despido injustificado", draft)

if __name__ == '__main__':
    unittest.main()
