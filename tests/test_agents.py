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
        self.assertTrue("INSPECCIÓN" in draft.upper(), "Draft should mention INSPECCIÓN")
        self.assertTrue("seguridad" in draft.lower(), "Draft should contain context 'seguridad'")

    def test_litigante_output(self):
        agent = LitiganteProcesalAgent()
        draft = agent.generate_draft("Despido injustificado")
        self.assertTrue("JUZGADO DE LO SOCIAL" in draft.upper(), "Draft should mention JUZGADO DE LO SOCIAL")
        self.assertTrue("despido" in draft.lower(), "Draft should contain context 'despido'")

if __name__ == '__main__':
    unittest.main()
