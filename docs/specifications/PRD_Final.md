# PRD: Sistema "Marxnager" (Versión Final)

## 1. Visión y Control de Acceso
El bot actúa como un asistente jurídico-administrativo exclusivo para delegados autorizados.

### 1.1 Seguridad Obligatoria
*   **Whitelist de IDs de Telegram**: El bot solo responderá a usuarios cuyos IDs estén en una lista blanca.
*   **Gestión de Acceso**: El acceso se gestiona a nivel de código o mediante una variable de entorno `AUTHORIZED_USER_IDS`.

## 2. Dualidad de Entorno (UX/UI)
### A. Operativa en Grupo (Acción Rápida)
*   **Propósito**: Notificar al equipo y registrar incidentes en el momento.
*   **Dinámica**: El delegado lanza el comando (ej. `/denuncia ...`). El bot crea el expediente, confirma la creación con enlaces a Notion/Drive y termina la interacción pública.

### B. Operativa en Privado (Modo Edición/Feature K)
*   **Propósito**: Trabajo profundo, subida de pruebas y refinado de borradores.
*   **Dinámica**: El bot invita al delegado a continuar en privado para subir fotos, audios o ajustar el texto sin saturar el grupo.

## 3. Arquitectura de la Feature K (Gestión de Expedientes)
1.  **Apertura**: El bot genera la estructura en Notion y Drive.
2.  **Transición al Privado**: Enlace al chat privado para enviar fotos y ajustar el texto.
3.  **Modo Sesión**: El bot se vincula al expediente específico en el chat privado.
4.  **Enriquecimiento**:
    *   **Adjuntos**: Fotos/PDFs se suben a Drive automáticamente.
    *   **Aclaraciones**: Mensajes de voz o texto actualizan el Google Doc usando IA.
5.  **Cierre**: El delegado pulsa [Finalizar]. El bot resume el estado final.

## 4. Especificaciones Técnicas
| Componente | Función | Detalles de Implementación |
| :--- | :--- | :--- |
| Telegram API | Interfaz de usuario y gestión de archivos. | `python-telegram-bot` v20+ |
| IA (OpenRouter API) | Procesamiento de lenguaje natural. | **Modelo Primario**: `deepseek/deepseek-r1-0528:free`<br>**Fallback**: `mistralai/devstral-2512:free` |
| Notion API | Base de datos central. | Base de datos "Expedientes" vinculada vía Internal Integration Token. |
| Google Drive API | Almacenamiento de archivos. | Estructura basada en carpetas raíz específicas (`denuncias`, `demandas`, `emails`) gestionadas por Service Account. |
| Google Docs API | Edición dinámica del borrador. | Generación automática y edición colaborativa. |

## 5. Matriz de Comandos
| Comando | Ubicación | Acción |
| :--- | :--- | :--- |
| `/denuncia [contexto]` | Grupo/Privado | Crea expediente ITSS + Carpeta + Doc. |
| `/demanda [contexto]` | Grupo/Privado | Crea expediente Judicial + Carpeta + Doc. |
| `/email [contexto]` | Grupo/Privado | Crea borrador de comunicación a RRHH. |
| `/update` | Privado | Despliega lista de casos abiertos para editar. |
| `/status [id]` | Grupo | Informa al equipo del estado de un caso. |

## 6. Definición de Prompts de Agentes

### AGENTE 1: "Inspector Laboral" (`/denuncia`)
**Misión**: Redactar denuncias formales ante la ITSS claras y fundamentadas.
**Estructura**: Encabezado, Hechos cronológicos, Fundamentación Jurídica (ET, LPRL, Convenios), Petición y Cierre.
**Tono**: Formal, técnico, asertivo.

### AGENTE 2: "Litigante Procesal" (`/demanda`)
**Misión**: Crear borradores de demandas judiciales según la Ley 36/2011.
**Estructura**: Designación del órgano, Datos identidad, Hechos numerados, Fundamentos de Derecho (ET, Jurisprudencia), Súplica y Otrosí.
**Tono**: Extremadamente formal, forense.

### AGENTE 3: "Comunicador Corporativo" (`/email`)
**Misión**: Redactar comunicaciones a RRHH firmes pero conciliadoras.
**Tipos**: Solicitud info (Art. 64 ET), Convocatorias, Notificaciones, Recordatorios.
**Tono**: Profesional, constructivo.

## 7. Mapeo de Carpetas (Drive)
Estructura: `2026 / [Tipo] / [ID] - [Contexto] / {Pruebas, Respuestas}`.

## 8. Diseño Notion
Base de datos "Expedientes" con propiedades:
*   **ID**: Identificador secuencial automático (ej. `D-2026-001`).
*   **Nombre (Title)**: Formato descriptivo `ID - Resumen` (ej. `D-2026-001 - Falta de EPIs`).
*   **Tipo**: Select (Denuncia ITSS, Demanda, Email).
*   **Estado**: Status (Borrador, En revisión, Enviado...).
*   **Responsable**: Persona asignada.
*   **Enlaces**: URLs a carpeta de Drive y Documento de Google (almacenado en propiedad `Perplexity` o `Enlace Doc`).

## 9. Plan de Implementación Orientado a Features (AI-Driven)

En lugar de un cronograma lineal, el desarrollo se estructura en "Slices" (rebanadas) funcionales. Cada fase entrega una capacidad completa y testeable, diseñada para ser implementada por agentes de IA de codificación.

### Fase 1: Core Foundation (El Esqueleto)
*Objetivo: Establecer la infraestructura base y la seguridad.*
1.  **Boilerplate del Bot**: Configuración inicial de `python-telegram-bot`, manejo de variables de entorno y conexión básica.
2.  **Sistema de Seguridad (Whitelist)**: Implementación del decorador o middleware que rechaza interacciones de IDs no autorizados (hardcoded o vía `.env`).
3.  **Router de Comandos**: Estructura básica que escucha `/denuncia`, `/demanda`, etc., y responde con un "Echo" (ej. "Comando recibido: [texto]").
4.  **Logging**: Sistema de logs para auditoría de accesos.

### Fase 2: Integración Vertical - "El Inspector Laboral"
*Objetivo: Un flujo completo de principio a fin para una sola funcionalidad (Denuncias).*
1.  **Conectores API**: Implementación de clientes *wrapper* mínimos para Notion y Google Drive.
2.  **Lógica `/denuncia`**:
    *   Parseo del input del usuario.
    *   Creación de la entrada en base de datos Notion (ID y Estado).
    *   Creación de la carpeta en Google Drive.
3.  **Generación de Documentos (Básico)**: Creación de un Google Doc en la carpeta con el texto plano del usuario.
4.  **Respuesta al Grupo**: El bot responde con los links generados.

### Fase 3: La Feature K (Dualidad y Enriquecimiento)
*Objetivo: Habilitar el trabajo profundo en privado.*
1.  **Gestión de Sesiones**: Lógica para trackear si un usuario está "editando" un expediente específico en privado.
2.  **Handover Público -> Privado**: Implementación del botón "Continuar en privado" y deep linking al bot.
3.  **Manejo de Archivos**: Capacidad de recibir fotos/PDFs en privado y subirlos a la carpeta correcta de Drive.
4.  **Refinado con IA (Prompting)**: Integración de OpenRouter API (DeepSeek/Kimi) para tomar el input del usuario + contexto y reescribir el Google Doc con formato jurídico.

### Fase 4: Escalado de Agentes (Nuevas Capacidades)
*Objetivo: Replicar el éxito de la Fase 2 para otros dominios.*
1.  **Agente "Litigante Procesal"**: Implementación de prompts complejos para `/demanda` (estructuras forenses).
2.  **Agente "Comunicador"**: Implementación de `/email` con selectores de tono.
3.  **Transcripción de Audio**: Integración de Whisper para permitir "dictar" los hechos en el chat privado.

### Fase 5: Refinamiento y Observabilidad
*Objetivo: Pulir la UX y asegurar la estabilidad.*
1.  **Feedback Loops**: Comandos `/status` para actualizar Notion desde Telegram.
2.  **Manejo de Errores**: Respuestas amigables ante fallos de API (Notion/Drive caídos).
3.  **Limpieza**: Jobs para archivar expedientes antiguos o limpiar temporales.
