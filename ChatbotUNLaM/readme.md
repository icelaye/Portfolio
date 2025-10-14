# 🎓 Chatbot Asistente - Ciencias Económicas UNLaM

Chatbot con RAG para asesorar sobre las carreras del Departamento de Ciencias Económicas de la Universidad Nacional de La Matanza.

## 🚀 Características

- ✅ RAG (Retrieval-Augmented Generation) con embeddings de OpenAI
- ✅ Búsqueda web en dominios de UNLaM como fallback
- ✅ Información de contacto cuando no puede responder
- ✅ Interfaz amigable con Streamlit
- ✅ Modelo GPT-3.5-turbo (económico) con temperatura baja (0.3)

## 📋 Carreras Incluidas

1. **Licenciatura en Administración** (5 años, 36 materias)
2. **Licenciatura en Economía** (5 años, 40 materias)
3. **Licenciatura en Comercio Internacional** (5 años, 36 materias)
4. **Contador Público** (5 años, 36 materias)

## 🛠️ Instalación

### 1. Crear los archivos

Crea estos 4 archivos en tu carpeta de proyecto:
- `app.py` - Aplicación principal
- `rag_system.py` - Sistema RAG
- `web_search.py` - Búsqueda web
- `requirements.txt` - Dependencias

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variable de entorno

Tu variable ya está configurada: `OPENAI_API_KEY`

Si necesitas configurarla manualmente:

**Linux/Mac:**
```bash
export OPENAI_API_KEY="tu-api-key-aqui"
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="tu-api-key-aqui"
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

## 📖 Uso

1. Escribe tu pregunta en el chat
2. El sistema buscará primero en los documentos cargados (RAG)
3. Si no encuentra información suficiente, buscará en el sitio web de UNLaM
4. Si no puede responder, proporcionará información de contacto

## 🔍 Ejemplos de Preguntas

- "¿Cuántas materias tiene la Licenciatura en Administración?"
- "¿Qué aprenderé en Comercio Internacional?"
- "¿Cuál es el plan de estudios de Contador Público?"
- "¿Cómo me inscribo al curso de ingreso?"
- "¿Cuál es la diferencia entre Economía y Administración?"
- "¿Qué materias tiene el primer año de Economía?"

## 📞 Información de Contacto

Si el chatbot no puede responder tu pregunta, contacta directamente:

- **Teléfono:** (54 11) 4480-8900 Int: 8954, 8819 y 8740
- **Horario:** 08:00 a 22:00 hs
- **Email:** economicas@unlam.edu.ar

## 🏗️ Arquitectura

```
Usuario
   ↓
Streamlit UI (app.py)
   ↓
┌──────────────────────────┐
│   Query del usuario      │
└──────────────────────────┘
   ↓
┌──────────────────────────┐
│  RAG System              │
│  - Embeddings            │
│  - Similarity Search     │
└──────────────────────────┘
   ↓
¿Contexto suficiente?
   ↓ No
┌──────────────────────────┐
│  Web Search              │
│  - Scraping UNLaM        │
└──────────────────────────┘
   ↓
┌──────────────────────────┐
│  GPT-3.5-turbo           │
│  (temp=0.3)              │
└──────────────────────────┘
   ↓
Respuesta + Contacto (si es necesario)
```

## ⚙️ Configuración

### Modelo y Temperatura

En `app.py`, línea ~75:

```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # Modelo económico
    temperature=0.3,         # Baja para respuestas consistentes
    messages=[...]
)
```

### Umbral de Similitud RAG

En `rag_system.py`, línea ~165:

```python
if score > 0.5:  # Umbral de relevancia (0.0 a 1.0)
```

## 💰 Costos Estimados (OpenAI)

- **Embeddings**: ~$0.02 USD por millón de tokens
- **GPT-3.5-turbo**: ~$0.50 USD por millón de tokens input
- **Conversación típica**: Menos de $0.01 USD por pregunta

## 🔒 Seguridad

- ✅ Tu `OPENAI_API_KEY` ya está configurada como variable de entorno
- ❌ Nunca compartas tu API key en el código
- ❌ No subas archivos `.env` a repositorios públicos

## 📝 Estructura de Archivos

```
proyecto/
│
├── app.py                 # Aplicación principal Streamlit
├── rag_system.py          # Sistema RAG con embeddings
├── web_search.py          # Búsqueda web UNLaM
├── requirements.txt       # Dependencias Python
└── README.md             # Esta documentación
```

## 🐛 Troubleshooting

**Error: "OPENAI_API_KEY not found"**
```bash
# Verifica que esté configurada
echo $OPENAI_API_KEY  # Linux/Mac
echo $env:OPENAI_API_KEY  # Windows PowerShell
```

**Error de instalación:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

**El scraping web falla:**
- Es normal, algunos sitios bloquean requests
- El sistema funcionará solo con RAG

**Respuestas lentas:**
- Normal en la primera ejecución (genera embeddings)
- Las siguientes serán más rápidas (usa caché)

## 🚀 Mejoras Futuras

- [ ] Agregar más documentos al RAG
- [ ] Implementar historial persistente (base de datos)
- [ ] Agregar autenticación de usuarios
- [ ] Mejorar el scraping web
- [ ] Agregar más opciones de idiomas
- [ ] Implementar feedback de usuarios

## 📄 Licencia

Proyecto educativo para la Universidad Nacional de La Matanza.
