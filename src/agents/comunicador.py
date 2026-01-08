from src.agents.base import AgentBase

class ComunicadorCorporativoAgent(AgentBase):
    def get_system_prompt(self) -> str:
        return """
        Eres un asesor de comunicación institucional especializado en relaciones laborales.
        TU MISIÓN: Redactar comunicaciones escritas a RRHH.
        ESTRUCTURA: Asunto, Saludo, Cuerpo (Contexto, Motivo, Petición), Cierre, Despedida.
        TONO: Profesional, constructivo, firme.
        """

    def simulated_draft(self, context: str) -> str:
        return f"""
ASUNTO: Comunicación formal sobre [ASUNTO]

A la atención del Responsable de Recursos Humanos:

Por la presente, en representación del Comité de Empresa, nos ponemos en contacto con ustedes en relación con:
{context}

Solicitamos que se nos facilite la información correspondiente/se subsane la situación en un plazo de [X] días.

Quedamos a la espera de su respuesta.

Atentamente,
Los Delegados de Personal
        """
