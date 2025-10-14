import streamlit as st
import os
from openai import OpenAI
from rag_system import RAGSystem
from web_search import search_unlam_web

# Configuración de la página
st.set_page_config(
    page_title="Asistente Ciencias Económicas UNLaM",
    page_icon="🎓",
    layout="wide"
)

# Inicializar cliente OpenAI
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ No se encontró OPENAI_API_KEY en las variables de entorno")
        st.stop()
    return OpenAI(api_key=api_key)

# Inicializar sistema RAG
@st.cache_resource
def get_rag_system():
    return RAGSystem()

client = get_openai_client()
rag = get_rag_system()

# Información de contacto
CONTACT_INFO = """
📞 **Información de Contacto - Departamento de Ciencias Económicas**

- **Teléfono:** (54 11) 4480-8900 Int: 8954, 8819 y 8740
- **Horario de Atención:** 08:00 a 22:00 hs
- **Correo:** economicas@unlam.edu.ar
"""

# Título y descripción
st.title("🎓 Asistente Virtual - Ciencias Económicas UNLaM")
st.markdown("""
Bienvenido al asistente virtual del Departamento de Ciencias Económicas de la 
Universidad Nacional de La Matanza. Puedo ayudarte con información sobre:
- Licenciatura en Administración
- Licenciatura en Economía
- Licenciatura en Comercio Internacional
- Contador Público
""")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            # 1. Intentar responder con RAG (pasando historial para contexto)
            rag_context = rag.get_relevant_context(
                prompt, 
                conversation_history=st.session_state.messages
            )
            
            # 2. Si no hay contexto suficiente, buscar en web UNLaM
            web_context = ""
            if not rag_context or len(rag_context) < 100:
                web_context = search_unlam_web(prompt)
            
            # 3. Preparar contexto completo
            full_context = ""
            if rag_context:
                full_context += f"Información de documentos internos:\n{rag_context}\n\n"
            if web_context:
                full_context += f"Información del sitio web UNLaM:\n{web_context}\n\n"
            
            # 4. Generar respuesta con GPT
            system_prompt = f"""Eres un asistente virtual del Departamento de Ciencias Económicas 
de la Universidad Nacional de La Matanza (UNLaM). Tu objetivo es ayudar a estudiantes 
potenciales y actuales con información sobre las carreras y programas.

Carreras disponibles:
- Licenciatura en Administración (5 años, 36 materias)
- Licenciatura en Economía (5 años, 40 materias)
- Licenciatura en Comercio Internacional (5 años, 36 materias)
- Contador Público (5 años, 36 materias)

IMPORTANTE:
- Si tienes información relevante en el contexto, úsala para responder.
- Si NO puedes responder con seguridad, proporciona la información de contacto.
- Sé conciso, claro y amigable.
- Usa emojis cuando sea apropiado.

Contexto disponible:
{full_context if full_context else "No hay contexto específico disponible."}

Si no puedes responder con certeza, proporciona esta información de contacto:
{CONTACT_INFO}. Ten en cuenta que puedes usar este recurso una sola vez por historial de conversación.
"""

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    temperature=0.3,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                assistant_response = response.choices[0].message.content
                
                # Si la respuesta es muy corta o indica desconocimiento, agregar contacto
                if len(assistant_response) < 50 or any(word in assistant_response.lower() 
                    for word in ["no sé", "no puedo", "no tengo información", "no estoy seguro"]):
                    assistant_response += f"\n\n{CONTACT_INFO}"
                
                st.markdown(assistant_response)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": assistant_response
                })
                
            except Exception as e:
                error_msg = f"❌ Error al generar respuesta: {str(e)}\n\n{CONTACT_INFO}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Sidebar con información adicional
with st.sidebar:
    st.header("ℹ️ Información Útil")
    st.markdown(CONTACT_INFO)
    
    st.markdown("---")
    st.markdown("### 🔗 Enlaces Importantes")
    st.markdown("- [Curso de Ingreso](https://www.unlam.edu.ar/inicio/curso-de-ingreso/)")
    st.markdown("- [UNLaM - Inicio](https://www.unlam.edu.ar/)")
    
    st.markdown("---")
    if st.button("🗑️ Limpiar Conversación"):
        st.session_state.messages = []
        st.rerun()