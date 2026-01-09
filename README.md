# Marxnager

**Marxnager** es un asistente sindical avanzado para Telegram, diseñado para potenciar la labor de los delegados mediante la automatización de documentos legales y la gestión centralizada de expedientes.

![Status](https://img.shields.io/badge/Status-Development-yellow)
![Python](https://img.shields.io/badge/Python-3.11+-blue)

## 🚀 Visión General

El bot permite a los delegados sindicales autorizados:
1.  **Generar Documentación Legal**: Crear borradores de denuncias a la ITSS, demandas judiciales y comunicaciones a RRHH usando IA.
2.  **Gestión Centralizada**: Cada caso se registra automáticamente en una base de datos de **Notion** y crea su propia carpeta en **Google Drive**.
3.  **Flujo Dual (Público/Privado)**: Inicia la acción en el grupo sindical para visibilidad, y refina los detalles (pruebas, redacción) en privado.

### ✨ Características Clave (Actualizado)
*   **🛡️ Creación Atómica y Rollback**: Garantía de integridad "todo o nada". Si falla la creación de cualquier activo (Notion, Drive, Doc) durante el proceso, el sistema revierte automáticamente todos los cambios parciales y notifica al usuario, evitando archivos huérfanos.
*   **⚖️ Verificación Legal (Dos Etapas)**: Cada borrador generado por la IA pasa por una fase de "Grounding" con **Perplexity Sonar**, que verifica la validez jurídica y cita la normativa vigente antes de entregarte el documento.
*   **🔄 Seguimiento en Tiempo Real**: Lista de verificación dinámica en Telegram que se actualiza en vivo (tachado/negrita) a medida que el bot completa cada paso (Drafting, Notion, Drive, Docs).
*   **🆔 IDs Secuenciales Inteligentes**: Detección automática del último ID (ej. `D-2026-005`) y asignación del siguiente.
*   **📂 Nombres Descriptivos**: Organización automática en Notion y Drive con formato `ID - Resumen`.

---

## 🛠️ Requisitos Previos

*   **Python 3.11+**
*   **Telegram Bot Token** (vía @BotFather)
*   **OpenRouter API Key** (para generación de borradores)
*   **Perplexity API Key** (para verificación legal y citas)
*   **Notion Integration Token** y ID de Base de Datos
*   **Google Cloud Service Account** (con Drive y Docs API habilitadas)

---

## ⚙️ Configuración e Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd sindicato-tg-bot
```

### 2. Entorno Virtual y Dependencias
```bash
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar Credenciales (.env)
Crea un archivo `.env` en la raíz del proyecto. Puedes copiar `.env.example`:
```bash
cp .env.example .env
```

Edita `.env` con tus valores reales:

```ini
# Telegram
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
AUTHORIZED_USER_IDS=123456789,987654321  # IDs separados por comas
LOG_LEVEL=INFO

# OpenRouter (IA - Generación)
OPENROUTER_API_KEY=sk-or-v1-...
MODEL_PRIMARY=deepseek/deepseek-r1-0528:free
MODEL_FALLBACK=mistralai/devstral-2512:free

# Perplexity (IA - Verificación)
PERPLEXITY_API_KEY_PRIMARY=pplx-...
PERPLEXITY_API_KEY_FALLBACK=pplx-...

# Notion
NOTION_TOKEN=ntn_...
NOTION_DATABASE_ID=32-char-database-id

# Google Drive & Docs
GOOGLE_DRIVE_CREDENTIALS_PATH=google_credentials.json
GOOGLE_DRIVE_ROOT_FOLDER_ID=your_root_id_here (opcional, usa las carpetas específicas abajo)

# Drive Specific Folders (IDs de las carpetas raíz para cada tipo)
DRIVE_FOLDER_DENUNCIAS=13x3wClghMGTzFBB8WRGDvmItogNe4vtZ
DRIVE_FOLDER_DEMANDAS=1JWq_nk0doWX6pUaDD34y7mt8YMuLegpU
DRIVE_FOLDER_EMAILS=14XQGsA9ROCqUzfw8y0RYXzLwkeN9M09U
```

### 4. Credenciales de Google
Asegúrate de tener el archivo `google_credentials.json` (la clave de tu Service Account) en la raíz del proyecto.

---

## 📖 Uso

### Comandos Principales

| Comando | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `/denuncia <texto>` | Inicia un expediente de denuncia a la ITSS. | `/denuncia Falta de EPIs en el almacén` |
| `/demanda <texto>` | Inicia un borrador de demanda judicial. | `/demanda Despido improcedente de Juan` |
| `/email <texto>` | Redacta un correo formal para RRHH. | `/email Solicitud calendario laboral` |
| `/status <id> <estado>` | Actualiza el estado de un caso en Notion. | `/status D-2026-001 enviado` |

### Flujo de Trabajo (Feature K)
1.  **Grupo**: El delegado usa `/denuncia ...`. El bot confirma y crea los enlaces (Drive/Notion).
2.  **Privado**: El bot envía un mensaje directo al delegado.
3.  **Enriquecimiento**: El delegado puede enviar fotos, audios o más texto al chat privado para que el bot actualice el expediente y el borrador automáticamente.

---

## 📂 Estructura del Proyecto

```
sindicato-tg-bot/
├── src/
│   ├── agents/          # Lógica de la IA (Prompts y generación)
│   ├── integrations/    # Clientes para Notion, Drive, Docs, OpenRouter
│   ├── handlers.py      # Manejadores de comandos de Telegram
│   ├── main.py          # Punto de entrada
│   └── config.py        # Configuración central
├── tests/               # Tests unitarios
├── .env                 # Variables de entorno (NO COMMIT)
├── google_credentials.json # Key de Google (NO COMMIT)
├── PRD_Final.md         # Documentación funcional completa
└── requirements.txt     # Dependencias Python
```

## 🧪 Tests
Para verificar que las integraciones funcionan correctamente:
```bash
python -m unittest discover tests
```

---
**Nota**: Este bot utiliza modelos de IA gratuitos a través de OpenRouter. La disponibilidad y calidad de las respuestas dependen del estado de estos modelos experimentales.
