
# Estructura Documento: Escrito de Denuncia ITSS

**Formato:** Markdown / Plantilla Generativa
**Uso:** Base para la generación automática de PDFs.
**Leyenda:**

* Texto Normal: Texto estático legal (Boilerplate).
* **[HARDCODED]**: Datos fijos extraídos de tus archivos (Skyway / Juan Manuel).
* `{{DYNAMIC}}`: Campos a rellenar por el LLM según el incidente.

---

## 1. CABECERA Y ORGANISMO

**Dirigido a:**
Inspección Provincial de Trabajo y Seguridad Social de **[HARDCODED] Madrid**.

---

## 2. DATOS DEL DENUNCIADO (EMPRESA)

* 
**Nombre o Razón Social:** [HARDCODED] **SKYWAY AIR NAVIGATION SERVICES** 


* 
**NIF / CIF:** [HARDCODED] **A86164894** 


* 
**Actividad:** [HARDCODED] **ACTIVIDADES ANEXAS AL TRANSPORTE AÉREO** 


* 
**CCC (Código Cuenta Cotización):** [HARDCODED] **28184193088** 


* 
**Domicilio Social:** [HARDCODED] **CALLE QUINTANAVIDES 21** 


* 
**Localidad / Provincia:** [HARDCODED] **MADRID / MADRID** 


* 
**Código Postal:** [HARDCODED] **28050** 


* 
**Centro de Trabajo:** [HARDCODED] **SERVICIO DE DIRECCIÓN EN PLATAFORMA, AEROPUERTO ADOLFO SUÁREZ MADRID - BARAJAS** 


* 
**Nº de Trabajadores:** [HARDCODED] **37** 


* 
**Horario:** [HARDCODED] **00.00 a 23.59** 


* 
**¿Continúa abierta la empresa?:** [HARDCODED] **SÍ** 



---

## 3. DATOS DEL DENUNCIANTE (TRABAJADOR/REPRESENTANTE)

* 
**Nombre y Apellidos:** [HARDCODED] **JUAN MANUEL TORALES CHORNE** 


* 
**NIF:** [HARDCODED] **44591820-H** 


* 
**NAF (Afiliación SS):** [HARDCODED] **29/10177911/13** 


* 
**Domicilio:** [HARDCODED] **CALLE PLAYA DE ZARAUZ 18, 2C** 


* 
**Localidad / Provincia:** [HARDCODED] **MADRID / MADRID** 


* 
**Código Postal:** [HARDCODED] **28042** 


* 
**Teléfono:** [HARDCODED] **627228904** 


* 
**Correo electrónico:** [HARDCODED] **delegados.sdpmad@gmail.com** 


* 
**¿Es o ha sido trabajador?:** [HARDCODED] **SÍ** 


* 
**Fecha de Ingreso:** [HARDCODED] **17/01/2023** 


* 
**¿Tiene demanda judicial presentada por el mismo motivo?:** `{{CHECK_DEMANDA_JUDICIAL}}` (Por defecto: **NO**) 



---

## 4. CUERPO DE LA DENUNCIA

### 4.1 RELATO DE HECHOS

*(Espacio reservado para la descripción cronológica extraída del input del usuario)*

`{{LISTA_HECHOS_NUMERADOS}}`
*Ejemplo generado por LLM:*

1. *El día {{FECHA}}, la empresa publicó el cuadrante...*
2. *Se ha modificado la condición laboral de...*
3. *Dicha comunicación se realizó mediante...*

### 4.2 INFRACCIONES SUPUESTAS / FUNDAMENTOS DE DERECHO

*(Espacio reservado para el enriquecimiento jurídico vía RAG/Perplexity)*

`{{BLOQUE_JURIDICO}}`

* **Normativa Vulnerada:** `{{LEYES_CITADAS}}` (Ej: Art. 41 Estatuto de los Trabajadores, LISOS).
* **Jurisprudencia:** `{{SENTENCIAS_CITADAS}}` (Ej: STS Sala de lo Social...).
* **Argumentación:** `{{ARGUMENTO_LEGAL}}`

### 4.3 DOCUMENTACIÓN Y PRUEBAS

*(Lista de adjuntos proporcionados por el usuario)*

`{{LISTA_DOCUMENTOS}}`

* *Ej: Correo electrónico de fecha...*
* *Ej: Cuadrante versión 4.0...*

---

## 5. PETICIÓN A LA ITSS

Por todo lo expuesto, **SOLICITO** a la Inspección de Trabajo y Seguridad Social:

1. Que se admita el presente escrito y se investiguen los hechos descritos.
2. `{{PETICIONES_ESPECIFICAS}}` *(Ej: Que se levante acta de infracción, que se requiera la evaluación de riesgos, etc.)*.
3. Que se notifique al denunciante el resultado de las actuaciones.

---

## 6. PIE Y NOTIFICACIONES

**Firma del Denunciante:**

---

**Fdo:** [HARDCODED] **Juan Manuel Torales Chorne** 

**Voluntad de relacionarse electrónicamente con el OEITSS:**
En base a la normativa vigente, ¿Confirma que desea seguir recibiendo sus comunicaciones y notificaciones en papel?

**[X] Sí, lo confirmo** [HARDCODED - *Preferencia marcada en fuentes*] 

*Aviso Legal sobre Protección de Datos Personales (Art. 13 RGPD y Art. 11 LO 3/2018): Los datos serán tratados por el Organismo Estatal Inspección de Trabajo y Seguridad Social para funciones de vigilancia.*