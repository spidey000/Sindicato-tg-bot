import unittest
from unittest.mock import MagicMock, AsyncMock
from src.agents.orchestrator import AgentOrchestrator
from src.agents.inspector import InspectorLaboralAgent
from src.agents.litigante import LitiganteProcesalAgent
from src.agents.comunicador import ComunicadorCorporativoAgent

class TestAgents(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.orchestrator = AgentOrchestrator()

    def test_orchestrator_routing(self):
        self.assertIsInstance(self.orchestrator.get_agent_for_command("/denuncia"), InspectorLaboralAgent)
        self.assertIsInstance(self.orchestrator.get_agent_for_command("/demanda"), LitiganteProcesalAgent)
        self.assertIsInstance(self.orchestrator.get_agent_for_command("/email"), ComunicadorCorporativoAgent)
        self.assertIsInstance(self.orchestrator.get_agent_for_command("/unknown"), InspectorLaboralAgent)

    async def test_inspector_output(self):
        agent = InspectorLaboralAgent()
        agent.llm_client = MagicMock()
        agent.llm_client.completion = AsyncMock(return_value="SOLICITUD DE INSPECCIÓN ANTE LA ITSS. Esta es una denuncia formal por falta de medidas de seguridad en el centro de trabajo, incumpliendo la normativa vigente.")
        draft = await agent.generate_draft("Falta de medidas de seguridad")
        self.assertTrue("INSPECCIÓN" in draft.upper(), "Draft should mention INSPECCIÓN")
        self.assertTrue("seguridad" in draft.lower(), "Draft should contain context 'seguridad'")

    async def test_litigante_output(self):
        agent = LitiganteProcesalAgent()
        agent.llm_client = MagicMock()
        agent.llm_client.completion = AsyncMock(return_value="AL JUZGADO DE LO SOCIAL. El trabajador presenta demanda por despido injustificado, solicitando la readmisión o indemnización correspondiente según ley.")
        draft = await agent.generate_draft("Despido injustificado")
        self.assertTrue("JUZGADO DE LO SOCIAL" in draft.upper(), "Draft should mention JUZGADO DE LO SOCIAL")
        self.assertTrue("despido" in draft.lower(), "Draft should contain context 'despido'")

if __name__ == '__main__':
    unittest.main()
