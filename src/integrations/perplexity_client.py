import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PerplexityClient:
    def __init__(self):
        self.primary_key = os.getenv("PERPLEXITY_API_KEY_PRIMARY")
        self.fallback_key = os.getenv("PERPLEXITY_API_KEY_FALLBACK")
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro" # Using an online model for grounding
        self.last_raw_response = None

    async def verify_draft(self, context: str, thesis: str = "", specific_point: str = "", area: str = "") -> Optional[str]:
        """
        Uses Perplexity API to verify and ground the draft text using a specialized Spanish Labor Law prompt.
        Attempts to use the primary key first, then the fallback key.
        """
        
        system_prompt = (
            "Actúa como abogado laboralista especializado en derecho laboral español. "
            f"CONTEXTO DEL CASO: {context} el centro de trabajo es el aeropuesto de madrid barajas en las torres de control que proveen el servicio de direccion de plataforma o SDP que se rige por el convenio de aplicacion es el Resolución de 27 de febrero de 2023, de la Dirección General de Trabajo, por la que se registra y publica el XX Convenio colectivo nacional de empresas de ingeniería; oficinas de estudios técnicos; inspección, supervisión y control técnico y de calidad que se puede consultar en https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-6346"
            "OBJETIVO: Busca y analiza: "
            "1. Normativa española aplicable (leyes, reales decretos) "
            f"2. Jurisprudencia del Tribunal Supremo y tribunales superiores que apoye {thesis} "
            f"3. Doctrina judicial relevante sobre {specific_point} "
            "REQUISITOS ESPECÍFICOS: "
            "- Jurisdicción: España "
            f"- Ámbito: Derecho laboral {area} "
            "- Cita fuentes verificables con números de sentencia, BOE, o referencias exactas "
            "- Prioriza jurisprudencia reciente (últimos 5 años) pero incluye doctrina consolidada si es relevante "
            "- Identifica argumentos contrarios para preparar contraargumentación "
            "FORMATO DE RESPUESTA: Estructura en: "
            "(A) Normativa aplicable citada, "
            "(B) Jurisprudencia favorable con referencias exactas, "
            "(C) Líneas argumentales principales, "
            "(D) Posibles debilidades y cómo refutarlas"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            # User message is implicit in the system prompt structure requested, 
            # but keeping a minimal user trigger is good practice or just empty. 
            # The spec put everything in one big block. 
            # I'll put the instruction in system and a trigger in user.
            {"role": "user", "content": "Por favor, procede con la verificación y análisis jurídico según las instrucciones."}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "web_search_options": {
                "search_type": "auto"  # Automatic classification
            }
        }

        # Try Primary Key
        if self.primary_key:
            result = await self._make_request(self.primary_key, payload)
            if result:
                return result
            logger.warning("Perplexity Primary Key failed. Attempting Fallback.")
        else:
            logger.warning("Perplexity Primary Key not configured.")

        # Try Fallback Key
        if self.fallback_key:
            result = await self._make_request(self.fallback_key, payload)
            if result:
                return result
            logger.error("Perplexity Fallback Key also failed.")
        else:
            logger.warning("Perplexity Fallback Key not configured.")

        return None

    async def research_case(self, context: str, document_type: str = "demanda") -> Optional[str]:
        """
        Uses Perplexity to research legal grounds for a case.
        Returns raw research output to be fed verbatim to OpenRouter for document generation.
        
        Args:
            context: User-provided facts of the case
            document_type: Type of document ('demanda' or 'denuncia')
        """
        
        # Build research prompt based on document type
        if document_type == "denuncia":
            action_focus = "denuncia ante la Inspección de Trabajo y Seguridad Social (ITSS)"
            legal_focus = "infracciones administrativas laborales y sanciones según LISOS"
        else:
            action_focus = "demanda judicial ante los Juzgados de lo Social"
            legal_focus = "procedimientos judiciales laborales según la LRJS"
        
        system_prompt = (
            "Eres un investigador jurídico especializado en derecho laboral español. "
            "Tu tarea es investigar y proporcionar información legal para fundamentar una acción legal.\n\n"
            f"TIPO DE ACCIÓN: {action_focus}\n"
            f"ENFOQUE LEGAL: {legal_focus}\n\n"
            "CONTEXTO LABORAL FIJO:\n"
            "- Centro de trabajo: Aeropuerto Adolfo Suárez Madrid-Barajas\n"
            "- Servicio: Dirección de Plataforma (SDP)\n"
            "- Convenio aplicable: XX Convenio colectivo nacional de empresas de ingeniería "
            "(BOE-A-2023-6346, Resolución 27 febrero 2023)\n\n"
            "INSTRUCCIONES:\n"
            "1. Analiza los hechos proporcionados e identifica las posibles vulneraciones legales\n"
            "2. Busca normativa española aplicable (Estatuto de los Trabajadores, LRJS, LISOS, convenio)\n"
            "3. Encuentra jurisprudencia reciente del Tribunal Supremo y TSJ que apoye la reclamación\n"
            "4. Proporciona citas exactas con números de sentencia y fechas\n"
            "5. Identifica el tipo de procedimiento y plazos aplicables\n\n"
            "FORMATO DE RESPUESTA:\n"
            "## CALIFICACIÓN JURÍDICA\n"
            "[Tipo de acción recomendada y fundamento]\n\n"
            "## NORMATIVA APLICABLE\n"
            "[Artículos específicos del ET, LRJS, convenio]\n\n"
            "## JURISPRUDENCIA\n"
            "[Sentencias con referencia exacta: Tribunal, fecha, nº recurso]\n\n"
            "## ARGUMENTACIÓN\n"
            "[Líneas argumentales principales]\n\n"
            "## PLAZOS Y PROCEDIMIENTO\n"
            "[Plazos de caducidad/prescripción y trámites previos]"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"HECHOS DEL CASO:\n{context}\n\nInvestiga y proporciona la fundamentación jurídica completa."}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "web_search_options": {
                "search_type": "auto"
            }
        }

        # Try Primary Key
        if self.primary_key:
            result = await self._make_request(self.primary_key, payload)
            if result:
                logger.info(f"✅ Perplexity Research SUCCESS for {document_type}. Length: {len(result)} chars.")
                return result
            logger.warning("Perplexity Primary Key failed for research. Attempting Fallback.")
        else:
            logger.warning("Perplexity Primary Key not configured.")

        # Try Fallback Key
        if self.fallback_key:
            result = await self._make_request(self.fallback_key, payload)
            if result:
                logger.info(f"✅ Perplexity Research SUCCESS (fallback) for {document_type}. Length: {len(result)} chars.")
                return result
            logger.error("Perplexity Fallback Key also failed for research.")
        else:
            logger.warning("Perplexity Fallback Key not configured.")

        return None

    async def _make_request(self, api_key: str, payload: dict) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(self.api_url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.last_raw_response = data
                        content = data["choices"][0]["message"]["content"]
                        logger.info(f"✅ Perplexity Verification SUCCESS. Status Code: 200. Response Length: {len(content)} characters.")
                        return content
                    else:
                        logger.warning(f"Attempt {attempt + 1}/{max_retries} failed. Status Code: {response.status_code}. Error: {response.text}")
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} Exception: {str(e)}")
            
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(retry_delay * (2 ** attempt)) # Exponential backoff
        
        logger.error("❌ Perplexity Verification FAILURE after max retries.")
        return None
