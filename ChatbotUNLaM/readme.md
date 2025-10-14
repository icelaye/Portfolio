# 🎓 Chatbot Asistente - Ciencias Económicas UNLaM

Chatbot inteligente con RAG (Retrieval-Augmented Generation) para asesorar sobre las carreras del Departamento de Ciencias Económicas de la Universidad Nacional de La Matanza.

## 🚀 Características

- ✅ **RAG con memoria contextual**: Mantiene el contexto de la conversación para respuestas coherentes
- ✅ **Información detallada**: Incluye carga horaria completa de cada materia (horas semanales y totales)
- ✅ **Embeddings semánticos**: Usa OpenAI para búsqueda inteligente en documentos
- ✅ **Búsqueda web**: Fallback automático al sitio de UNLaM cuando no hay información en RAG
- ✅ **Información de contacto**: Proporciona datos de contacto cuando no puede responder
- ✅ **Interfaz amigable**: Desarrollada con Streamlit para una experiencia de usuario óptima
- ✅ **Modelo económico**: Usa GPT-3.5-turbo con temperatura baja (0.3) para respuestas precisas

## 📋 Carreras Incluidas

1. **Licenciatura en Administración** (5 años, 36 materias, 3,360 horas totales)
2. **Licenciatura en Economía** (5 años, 40 materias)
3. **Licenciatura en Comercio Internacional** (5 años, 36 materias)
4. **Contador Público** (5 años, 36 materias)

## 🛠️ Requisitos Previos

- Python 3.8 o superior
- Cuenta de OpenAI con acceso a la API
- Clave API de OpenAI (obtener en: https://platform.openai.com/api-keys)

## 📦 Instalación

### 1. Clonar o descargar el repositorio

```bash
git clone https://github.com/icelaye/Portfolio/tree/main/ChatbotUNLaM
cd chatbot-unlam
```

O descarga los siguientes archivos en una carpeta:
- `app.py` o `unlam_chatbot_app.py`
- `rag_system.py`
- `web_search.py`
- `requirements.txt`

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar la clave API de OpenAI

Hay tres formas de configurar la variable de entorno `OPENAI_API_KEY`:

#### **Opción A: Archivo .env (Recomendado para desarrollo local)**

1. Crear un archivo `.env` en la raíz del proyecto:
```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

2. Asegurarse de que `.env` esté en `.gitignore`:
```bash
echo ".env" >> .gitignore
```

#### **Opción B: Variable de entorno del sistema**

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-..."
```

Para hacerlo permanente, agregar al archivo `~/.bashrc` o `~/.zshrc`:
```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=sk-...
```

#### **Opción C: Secrets de Streamlit Cloud (Para deployment)**

Si se despliega en Streamlit Cloud:

1. Ir a la configuración de la app en Streamlit Cloud
2. En "Secrets", agregar:
```toml
OPENAI_API_KEY = "sk-..."
```

## ▶️ Ejecutar la Aplicación

### Ejecución local:

```bash
streamlit run app.py
```

O si el archivo se llama diferente:
```bash
streamlit run unlam_chatbot_app.py
```

Si `streamlit` no se reconoce como comando:
```bash
python -m streamlit run app.py
```

## 🌐 Deployment en Streamlit Cloud

### Pasos para publicar:

1. **Crear repositorio en GitHub**:
   - Subir todos los archivos (.py y requirements.txt)
   - Asegurarse de NO subir el archivo `.env`

2. **Ir a Streamlit Cloud**:
   - Acceder a https://streamlit.io/cloud
   - Click en "New app"

3. **Configurar la app**:
   - Seleccionar el repositorio de GitHub
   - Elegir la rama (main/master)
   - Especificar el archivo principal (app.py)

4. **Agregar Secrets**:
   - En "Advanced settings" → "Secrets"
   - Agregar:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```

5. **Deploy**:
   - Click en "Deploy"
   - La app estará disponible en: `https://[nombre-app].streamlit.app`

## 📖 Uso del Chatbot

### Ejemplos de preguntas que puede responder:

**Información general:**
- "¿Cuántas materias tiene la Licenciatura en Administración?"
- "¿Qué aprenderé en Comercio Internacional?"
- "¿Cuántos años dura la carrera de Contador Público?"

**Carga horaria:**
- "¿Cuántas horas tiene Matemática I?"
- "¿Cuál es la carga horaria semanal de Estadística?"
- "¿Cuántas horas totales tiene el primer año de Economía?"

**Plan de estudios:**
- "¿Qué materias veré en el segundo año de Administración?"
- "¿Cuál es el plan de estudios completo de Comercio Internacional?"

**Conversaciones contextuales:**
```
Usuario: "Cuéntame sobre Administración"
Bot: [Explica la Licenciatura en Administración]

Usuario: "¿Cuántas materias tiene el tercer año?"
Bot: [Entiende que sigue hablando de Administración]

Usuario: "¿Y la carga horaria de ese año?"
Bot: [Mantiene el contexto y responde sobre Administración - tercer año]
```

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────┐
│   Usuario/Pregunta  │
└──────────┬──────────┘
           ↓
┌─────────────────────────────────┐
│   Streamlit Interface (app.py)  │
│   - Gestión de sesión           │
│   - Historial de conversación   │
└──────────┬──────────────────────┘
           ↓
┌────────────────────────────────────┐
│   RAG System (rag_system.py)       │
│   - Búsqueda semántica             │
│   - Embeddings con contexto        │
│   - 9 documentos de conocimiento   │
└──────────┬─────────────────────────┘
           ↓
     ¿Suficiente info?
           ↓ No
┌────────────────────────────────────┐
│   Web Search (web_search.py)       │
│   - Scraping de unlam.edu.ar       │
└──────────┬─────────────────────────┘
           ↓
┌────────────────────────────────────┐
│   GPT-3.5-turbo (OpenAI)           │
│   - Temperatura: 0.3               │
│   - Contexto: últimos 10 mensajes  │
└──────────┬─────────────────────────┘
           ↓
┌────────────────────────────────────┐
