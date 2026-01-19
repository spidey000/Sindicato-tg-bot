# PRD: Sistema "Marxnager" - Versión Completa y Detallada

## 1. Visión y Control de Acceso

### 1.1 Filosofía del Sistema

El sistema "Marxnager" es una herramienta de empoderamiento legal y administrativo diseñada para transformar la forma en que los delegados sindicales gestionan conflictos laborales. No es un bot de propósito general, sino un **asistente jurídico especializado** que combina:

- **Inteligencia Artificial Generativa**: Para crear documentación legal de calidad profesional
- **Automatización de Flujos**: Para eliminar trabajo administrativo repetitivo
- **Trazabilidad Absoluta**: Cada caso tiene historial completo desde su origen

### 1.2 Principio de Seguridad por Diseño

El acceso al sistema no es opcional ni configurable por usuarios: es una **restricción de arquitectura**.

#### Implementación del Control de Acceso

**Nivel 1: Whitelist Hardcoded**

```python
# config/authorized_users.py
AUTHORIZED_USERS = {
    123456789: {
        "name": "Juan Pérez",
        "role": "Delegado Principal",
        "union": "CCOO",
        "center": "Madrid Barajas",
        "granted_date": "2026-01-01",
        "permissions": ["denuncia", "demanda", "email", "admin"]
    },
    987654321: {
        "name": "María García",
        "role": "Delegado Suplente",
        "union": "UGT",
        "center": "Madrid Barajas",
        "granted_date": "2026-01-05",
        "permissions": ["denuncia", "email"]
    }
}

def is_authorized(user_id: int, command: str = None) -> bool:
    """
    Verifica si un usuario está autorizado para usar el bot.
    Si se especifica un comando, verifica permisos específicos.
    """
    if user_id not in AUTHORIZED_USERS:
        return False
    
    if command is None:
        return True
    
    user_permissions = AUTHORIZED_USERS[user_id]["permissions"]
    return "admin" in user_permissions or command in user_permissions
```

**Nivel 2: Variables de Entorno (Producción)**

```bash
# .env
AUTHORIZED_USER_IDS=123456789,987654321,456789123
ADMIN_USER_IDS=123456789
BOT_TOKEN=<REDACTED_SECRET>
NOTION_API_KEY=your_notion_key
GOOGLE_DRIVE_CREDENTIALS=path/to/credentials.json
```

**Nivel 3: Respuestas a Intentos No Autorizados**

```python
UNAUTHORIZED_RESPONSES = {
    "silent": None,  # No responde nada
    "generic": "⛔ Este bot es de uso exclusivo para delegados autorizados.",
    "informative": "⛔ Acceso denegado.\n\nEste sistema es una herramienta interna de representación laboral. Si necesitas asesoramiento sindical, contacta con tu delegado en el centro de trabajo.",
    "log_and_notify": "⛔ Acceso denegado.\n\n[El intento ha sido registrado y notificado a los administradores]"
}

# Configuración por defecto
UNAUTHORIZED_MODE = "informative"
```

### 1.3 Gestión de Permisos Granulares

No todos los delegados necesitan acceso a todas las funcionalidades:

| Rol | /denuncia | /demanda | /email | /update | /status | /admin |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Delegado Principal | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delegado Suplente | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| Miembro Comité | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| Asesor Externo | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |

### 1.4 Auditoría de Acceso

Cada interacción genera un registro:

```python
# models/access_log.py
@dataclass
class AccessLog:
    timestamp: datetime
    user_id: int
    user_name: str
    command: str
    chat_type: str  # "group" | "private"
    authorized: bool
    action_taken: str  # "executed" | "denied" | "error"
    case_id: Optional[str] = None
    
    def to_notion_entry(self) -> dict:
        """Convierte el log en entrada de base de datos Notion"""
        return {
            "Fecha": self.timestamp.isoformat(),
            "Usuario": self.user_name,
            "Comando": self.command,
            "Autorizado": "✅" if self.authorized else "❌",
            "Caso": self.case_id or "N/A"
        }
```

---

## 2. Dualidad de Entorno (UX/UI Detallada)

### 2.1 Filosofía de la Separación Grupo/Privado

La clave del diseño es entender **qué información necesita el equipo vs. qué información necesita el responsable del caso**.

#### Información Pública (Grupo)
- **Apertura del caso**: Todo el equipo debe saber que se está actuando
- **Cambios de estado**: "El caso X pasó a fase judicial"
- **Asignaciones**: "María se ha hecho cargo del expediente Y"
- **Alertas urgentes**: "La empresa ha presentado alegaciones en el caso Z"

#### Información Privada (DM)
- Pruebas documentales (fotos de nóminas, contratos, mensajes de supervisores)
- Testimonios de trabajadores afectados (audio/texto con datos personales)
- Borradores en proceso de refinado
- Estrategias legales antes de ejecutarlas

### 2.2 Flujo de Transición: Del Grupo al Privado

**Escenario Típico:**

```
[GRUPO SINDICAL - 15 miembros online]

👤 Delegado: /denuncia La empresa está obligando a trabajadores de baja médica a ir a las instalaciones para recoger documentación

🤖 Bot (respuesta pública):
━━━━━━━━━━━━━━━━━━━━━━
✅ EXPEDIENTE CREADO

📋 ID: D-2026-008
📂 Tipo: Denuncia ITSS
📅 Fecha: 08/01/2026 20:35
👤 Responsable: Juan Pérez
🏢 Empresa: Skyway ANS

🔗 Enlaces:
• [Ver en Notion](notion.so/D-2026-008)
• [Carpeta Drive](drive.google.com/D-2026-008)
• [Borrador Doc](docs.google.com/D-2026-008)

━━━━━━━━━━━━━━━━━━━━━━
💬 ¿Necesitas añadir pruebas o detalles?
   [Continuar en privado] 🔒
━━━━━━━━━━━━━━━━━━━━━━

[El grupo ve que el caso está abierto. La conversación pública termina aquí]

───────────────────────────

[CHAT PRIVADO con el Delegado]

🤖 Bot (mensaje directo):
Hola Juan 👋

He creado el expediente D-2026-008 sobre "obligación de asistencia durante baja médica".

🎯 MODO EDICIÓN ACTIVO
Ahora puedes:
• Enviar fotos/PDFs de pruebas
• Grabar audios con más detalles
• Escribir información adicional
• Pedirme que refine el borrador

Todo lo que envíes aquí irá directamente a este expediente.
...
```

### 2.3 Gestión de Estados del Modo Sesión

El bot debe trackear en qué "contexto" está cada conversación privada (IDLE, CASE_EDITING, etc.).

### 2.4 Notificaciones Inteligentes al Grupo

El bot debe notificar al grupo solo cuando hay cambios relevantes (Creación, Cambio de Estado, Vencimiento). No notifica ediciones menores.

---

## 3. Arquitectura de la Feature K (Gestión de Expedientes) - UNIFICADA

### 3.1 Ciclo de Vida Completo de un Expediente (Flujo Unificado)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           APERTURA (t=0)                                │
│                                                                         │
│  Comando → Investigación (IA/Perplexity) → Generación Borrador (IA)     │
│                                ↓                                        │
│  Carpeta Drive → Documento Google Doc → Entrada en Notion (Dump Completo) │
└─────────────────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────┐
│              ENRIQUECIMIENTO (t=0 a t=72h - Privado)        │
│  • Subida de pruebas documentales                          │
│  • Audios de testimonios transcritos                        │
│  • Refinado iterativo del texto                             │
└─────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────┐
│                FINALIZACIÓN (t=72h)                         │
│  Estado → "Listo para enviar"                               │
│  Generación de PDF final                                    │
└─────────────────────────────────────────────────────────────┘
```

El flujo técnico de creación para **todos** los comandos (`/demanda`, `/denuncia`, `/email`) es:
1.  **Inicialización**: Generación de ID único.
2.  **Investigación**: Perplexity busca normativa y contexto legal relevante.
3.  **Generación Documental**: LLM genera el borrador usando Plantilla + Investigación.
4.  **Estructura Drive**: Creación de carpetas.
5.  **Google Docs**: Creación del archivo editable.
6.  **Notion Entry**: Creación de página, enlazado de Drive/Doc, y **volcado** de investigación y borrador.

### 3.2 Estructura de Datos en Notion

(Base de datos "Expedientes" y "Registro de Actividad" se mantiene igual que en la versión detallada previa, con propiedades para ID, Estado, Enlace Drive, Enlace Doc, etc.)

### 3.3 Jerarquía de Carpetas en Google Drive

```
📁 Marxnager - Expedientes
│
├── 📁 2026
│   ├── 📁 01_Denuncias_ITSS
│   ├── 📁 02_Demandas_Judiciales
│   └── 📁 03_Comunicaciones_RRHH
```
(Jerarquía completa detallada en secciones anteriores se mantiene).

---

## 4. Especificaciones Técnicas de Integración

### 4.1 Stack Tecnológico
- Python 3.11+, python-telegram-bot
- Perplexity API (Investigación)
- OpenRouter/OpenAI (Generación)
- Notion, Drive, Docs APIs

### 4.2 Arquitectura de Microservicios
(Diagrama conceptual de Command Router -> Servicios -> Integraciones se mantiene).

---

## 5. Matriz de Comandos (Ampliada con Flujo Unificado)

### 5.1 Comando: `/denuncia`

**Flujo interno:**
1. Validar acceso del usuario.
2. **Investigación Jurídica**: Perplexity analiza los hechos.
3. **Generación Borrador**: Agente "Inspector Laboral" usa plantilla + investigación.
4. **Infraestructura**: Crear carpeta Drive y Google Doc.
5. **Registro**: Crear página en Notion y **volcar** contenido (Investigación + Borrador).
6. Responder con resumen + botón de [Continuar en privado].

### 5.2 Comando: `/demanda`
**Flujo interno:** Idéntico a `/denuncia` (Investigación -> Borrador -> Drive -> Docs -> Notion).
Diferencia: Usa plantilla de Demanda y Agente "Litigante Procesal".

### 5.3 Comando: `/email`
**Flujo interno:** Idéntico a `/denuncia` (Investigación -> Borrador -> Drive -> Docs -> Notion).
Diferencia: Usa plantilla de Email, Agente "Comunicador Corporativo". Investigación enfocada en contexto laboral.

### 5.4 Comando: `/update`
(Solo privado, lista casos activos).

### 5.5 Comando: `/status`
(Actualiza estado en Notion y notifica cambio).

---

## 6. Definición de Prompts de Agentes
(Se mantienen las definiciones de "Inspector Laboral", "Litigante Procesal" y "Comunicador Corporativo" detalladas anteriormente).

## 7. Mapeo de Carpetas
(Se mantiene la estructura detallada).

## 8. Diseño de la Base de Datos en Notion
(Se mantiene el diseño detallado de propiedades y estados).

## 9. Consideraciones de Seguridad
(Cifrado, logs anónimos, etc. se mantienen).
