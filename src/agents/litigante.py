from src.agents.base import AgentBase

class LitiganteProcesalAgent(AgentBase):
    def get_system_prompt(self) -> str:
        return """
        Eres un abogado laboralista especializado en procedimientos judiciales ante los Juzgados de lo Social.
        TU MISIÓN: Crear borradores de demandas judiciales (LRJS).
        ESTRUCTURA: Designación, Identidad, Hechos (numerados), Fundamentos de Derecho, Súplica, Otrosí.
        TONO: Extremadamente formal, forense.
        """

    def simulated_draft(self, context: str) -> str:
        return f"""
AL JUZGADO DE LO SOCIAL DE MADRID

D. [DEMANDANTE], mayor de edad...

DIGO:

Que por medio del presente escrito interpongo DEMANDA por [TIPO DE PROCEDIMIENTO] contra la empresa [EMPRESA].

HECHOS
PRIMERO.- El trabajador presta servicios...
SEGUNDO.- {context}

FUNDAMENTOS DE DERECHO
I. Competencia...
II. Legitimación...
III. Fondo del asunto: Estatuto de los Trabajadores art...

SUPLICO AL JUZGADO
Que admita a trámite la demanda...
        """
