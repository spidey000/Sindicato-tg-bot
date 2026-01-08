from src.agents.base import AgentBase

class InspectorLaboralAgent(AgentBase):
    def get_system_prompt(self) -> str:
        return """
        Eres un asesor jurídico especializado en Derecho Laboral español y procedimientos ante la Inspección de Trabajo.
        TU MISIÓN: Redactar denuncias formales ante la ITSS.
        ESTRUCTURA: Encabezado, Hechos, Fundamentación Jurídica, Petición.
        TONO: Formal, técnico, asertivo.
        """

    def simulated_draft(self, context: str) -> str:
        return f"""
A LA INSPECCIÓN PROVINCIAL DE TRABAJO Y SEGURIDAD SOCIAL

D. [NOMBRE DELEGADO], con DNI [DNI], en calidad de Delegado Sindical.

EXPONE:

Que la empresa [EMPRESA] ha incurrido en los siguientes incumplimientos:

HECHOS:
{context}

FUNDAMENTOS DE DERECHO:
Se vulnera el artículo X del Estatuto de los Trabajadores.

SOLICITA:
Que se levante acta de infracción.
        """
