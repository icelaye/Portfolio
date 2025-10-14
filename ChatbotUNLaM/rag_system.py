import os
from openai import OpenAI
import numpy as np
from typing import List, Dict

class RAGSystem:
    """Sistema RAG para búsqueda en documentos de las carreras"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.documents = self._load_documents()
        self.embeddings = self._create_embeddings()
    
    def _load_documents(self) -> List[Dict[str, str]]:
        """Carga los documentos de las carreras con información detallada"""
        documents = [
            {
                "id": "admin_desc",
                "carrera": "Licenciatura en Administración",
                "content": """La Licenciatura en Administración tiene como objetivo formar profesionales 
que posean aptitudes y conocimientos para desempeñarse en la gestión de organizaciones 
privadas y públicas desde diferentes posiciones jerárquicas o en forma independiente.

El egresado está facultado para cumplir, en calidad de director y/o consultor, con el rol 
de líder en las distintas áreas de las actividades asociadas a sus incumbencias, sean estas 
comerciales, administrativas, de gestión y toma de decisiones, productivas, de planeamiento, 
de logística, de conducción y/o de control de organizaciones.

Duración: 5 años
Cantidad de materias: 36
Carga horaria total: 3,360 horas
Modalidad: Presencial"""
            },
            {
                "id": "economia_desc",
                "carrera": "Licenciatura en Economía",
                "content": """La Licenciatura en Economía tiene como objetivo formar profesionales con un 
profundo conocimiento sobre los fundamentos técnicos y teóricos de la ciencia económica y con 
capacidad para reconocer y comprender la diversidad de enfoques e interés existentes en cuanto 
a la forma y el método de encarar la problemática económica.

El egresado está capacitado para aplicar los métodos e instrumentos del análisis económico en 
diversos contextos institucionales y espaciales; elaborar estrategias de desarrollo de la economía 
argentina en el contexto regional, latinoamericano y mundial; participar en procesos de definición 
y elaboración de políticas públicas.

Duración: 5 años
Cantidad de materias: 40
Modalidad: Presencial"""
            },
            {
                "id": "comercio_desc",
                "carrera": "Licenciatura en Comercio Internacional",
                "content": """La Licenciatura en Comercio Internacional se enmarca en el escenario complejo 
de un mundo hiperconectado, por ello presta especial atención a los entornos cambiantes que 
provocan la multiplicidad de procesos económicos y sociales.

El egresado está capacitado para tener a su cargo la gestión de negocios y el diseño, la evaluación, 
la ejecución, la realización y el seguimiento de proyectos para la inserción en los mercados 
internacionales e intervenir en la creación de estrategias de negocios en ámbitos públicos y privados.

Duración: 5 años
Cantidad de materias: 36
Modalidad: Presencial"""
            },
            {
                "id": "contador_desc",
                "carrera": "Contador Público",
                "content": """La carrera de Contador Público tiene como objetivo central formar profesionales 
con las capacidades y aptitudes para desempeñarse competentemente tanto en organizaciones públicas 
como privadas, en relación de dependencia o en forma independiente con su propia oficina o emprendimiento.

El egresado posee las condiciones técnicas y legales para realizar el diseño y la implementación de 
sistemas contables; organizar el proceso de registración de los hechos económicos; preparar, analizar 
y proyectar estados contables, presupuestarios, de costos y de impuestos.

Duración: 5 años
Cantidad de materias: 36
Modalidad: Presencial"""
            },
            {
                "id": "admin_plan_detallado",
                "carrera": "Licenciatura en Administración - Plan de Estudios Detallado",
                "content": """Plan de estudios Licenciatura en Administración con carga horaria:

PRIMER AÑO:
- Matemática I: 8 hs semanales (128 hs totales)
- Historia Económica Social y Contemporánea: 4 hs semanales (64 hs totales)
- Administración General: 8 hs semanales (128 hs totales)
- Contabilidad Básica: 8 hs semanales (128 hs totales)
- Derecho Público: 4 hs semanales (64 hs totales)
- Introducción al Conocimiento Científico: 4 hs semanales (64 hs totales)
- Matemática II: 6 hs semanales (96 hs totales)
- Inglés Nivel I: 4 hs semanales (64 hs totales)
- Computación Nivel I: 4 hs semanales (64 hs totales)

SEGUNDO AÑO:
- Estadística: 8 hs semanales (128 hs totales)
- Técnicas de Valuación: 8 hs semanales (128 hs totales)
- Derecho Civil: 4 hs semanales (64 hs totales)
- Elementos de Costos: 8 hs semanales (128 hs totales)
- Economía General: 6 hs semanales (96 hs totales)
- Psicosociología de las Organizaciones: 4 hs semanales (64 hs totales)
- Derecho Comercial I: 4 hs semanales (64 hs totales)
- Inglés Nivel II: 4 hs semanales (64 hs totales)
- Computación Nivel II: 4 hs semanales (64 hs totales)

TERCER AÑO:
- Procedimientos Administrativos: 6 hs semanales (96 hs totales)
- Sistemas de Información: 6 hs semanales (96 hs totales)
- Macroeconomía: 6 hs semanales (96 hs totales)
- Derecho Laboral y Previsional: 4 hs semanales (64 hs totales)
- Estados Contables: 8 hs semanales (128 hs totales)
- Matemática Financiera: 6 hs semanales (96 hs totales)

CUARTO AÑO:
- Administración de Personal: 6 hs semanales (96 hs totales)
- Administración de la Producción: 6 hs semanales (96 hs totales)
- Comercialización: 6 hs semanales (96 hs totales)
- Administración de Empresas Públicas: 6 hs semanales (96 hs totales)
- Teoría de la Decisión: 6 hs semanales (96 hs totales)
- Administración Financiera: 6 hs semanales (96 hs totales)
- Inglés Nivel III: 4 hs semanales (64 hs totales)

QUINTO AÑO:
- Dirección General: 6 hs semanales (96 hs totales)
- Planeamiento y Evaluación de Proyectos: 6 hs semanales (96 hs totales)
- Estructura Económica Argentina: 4 hs semanales (64 hs totales)
- Seminario de Análisis Estratégico: 8 hs semanales (128 hs totales)
- Inglés Nivel IV: 4 hs semanales (64 hs totales)

Total: 36 materias - 3,360 horas"""
            },
            {
                "id": "economia_plan_detallado",
                "carrera": "Licenciatura en Economía - Plan de Estudios Detallado",
                "content": """Plan de estudios Licenciatura en Economía con carga horaria:

PRIMER AÑO:
- Matemática I: 8 hs semanales (128 hs totales)
- Derecho Público: 4 hs semanales (64 hs totales)
- Historia Económica Social y Contemporánea: 4 hs semanales (64 hs totales)
- Inglés Nivel I: 4 hs semanales (64 hs totales)
- Computación Nivel I: 4 hs semanales (64 hs totales)
- Contabilidad Básica: 8 hs semanales (128 hs totales)
- Introducción al Conocimiento Científico: 4 hs semanales (64 hs totales)
- Administración General: 8 hs semanales (128 hs totales)

SEGUNDO AÑO:
- Inglés Nivel II: 4 hs semanales (64 hs totales)
- Computación Nivel II: 4 hs semanales (64 hs totales)
- Matemática II: 6 hs semanales (96 hs totales)
- Economía General: 6 hs semanales (96 hs totales)
- Sociología: 4 hs semanales (64 hs totales)
- Estadística: 8 hs semanales (128 hs totales)
- Macroeconomía: 6 hs semanales (96 hs totales)
- Historia Económica Argentina: 4 hs semanales (64 hs totales)

TERCER AÑO:
- Inglés Nivel III: 4 hs semanales (64 hs totales)
- Matemática Financiera: 6 hs semanales (96 hs totales)
- Estadística Avanzada: 4 hs semanales (64 hs totales)
- Cuentas Nacionales: 4 hs semanales (64 hs totales)
- Inglés Nivel IV: 4 hs semanales (64 hs totales)
- Metodología de la Investigación Económica: 4 hs semanales (64 hs totales)
- Economía de los Recursos Naturales y Ambientales: 4 hs semanales (64 hs totales)
- Matemática III: 6 hs semanales (96 hs totales)
- Microeconomía Aplicada: 4 hs semanales (64 hs totales)

CUARTO AÑO:
- Finanzas Públicas: 6 hs semanales (96 hs totales)
- Historia del Pensamiento Económico: 4 hs semanales (64 hs totales)
- Macroeconomía Avanzada: 6 hs semanales (96 hs totales)
- Análisis Sectorial: 4 hs semanales (64 hs totales)
- Planeamiento y Evaluación de Proyectos: 6 hs semanales (96 hs totales)
- Econometría: 6 hs semanales (96 hs totales)
- Dinero, Crédito y Bancos: 4 hs semanales (64 hs totales)

QUINTO AÑO:
- Crecimiento y Desarrollo Económico: 6 hs semanales (96 hs totales)
- Electiva 1: Sin especificar
- Economía Internacional: 4 hs semanales (64 hs totales)
- Economía del Comportamiento: 4 hs semanales (64 hs totales)
- Política Económica: 4 hs semanales (64 hs totales)
- Seminario de Actuación Profesional: 6 hs semanales (96 hs totales)
- Mercado de Capitales: 4 hs semanales (64 hs totales)
- Electiva 2: Sin especificar

Total: 40 materias"""
            },
            {
                "id": "comercio_plan_detallado",
                "carrera": "Licenciatura en Comercio Internacional - Plan de Estudios Detallado",
                "content": """Plan de estudios Licenciatura en Comercio Internacional con carga horaria:

PRIMER AÑO:
- Matemática I: 8 hs semanales (128 hs totales)
- Derecho Público: 4 hs semanales (64 hs totales)
- Historia Económica Social y Contemporánea: 4 hs semanales (64 hs totales)
- Inglés Nivel I: 4 hs semanales (64 hs totales)
- Contabilidad Básica: 8 hs semanales (128 hs totales)
- Introducción al Conocimiento Científico: 4 hs semanales (64 hs totales)
- Administración General: 8 hs semanales (128 hs totales)

SEGUNDO AÑO:
- Inglés Nivel II: 4 hs semanales (64 hs totales)
- Economía General: 6 hs semanales (96 hs totales)
- Derecho Civil y Comercial: 6 hs semanales (96 hs totales)
- Introducción al Comercio Internacional: 6 hs semanales (96 hs totales)
- Computación Nivel I: 4 hs semanales (64 hs totales)
- Estadística: 8 hs semanales (128 hs totales)
- Macroeconomía: 6 hs semanales (96 hs totales)
- Legislación Aduanera: 6 hs semanales (96 hs totales)

TERCER AÑO:
- Geografía Económica: 6 hs semanales (96 hs totales)
- Operatoria del Comercio Internacional: 6 hs semanales (96 hs totales)
- Valoración y Clasificación Arancelaria: 4 hs semanales (64 hs totales)
- Costos y Elementos de Finanzas: 6 hs semanales (96 hs totales)
- Computación Nivel II: 4 hs semanales (64 hs totales)
- Práctica Aduanera: 6 hs semanales (96 hs totales)
- Logística Internacional: 4 hs semanales (64 hs totales)
- Régimen Financiero del Comercio Internacional: 6 hs semanales (96 hs totales)

CUARTO AÑO:
- Inglés Nivel III: 4 hs semanales (64 hs totales)
- Comercialización: 6 hs semanales (96 hs totales)
- Investigación de Mercados: 4 hs semanales (64 hs totales)
- Integración Económica: 6 hs semanales (96 hs totales)
- Planeamiento y Evaluación de Proyectos: 4 hs semanales (64 hs totales)
- Taller de Gestión Operativa del Comercio Internacional: 6 hs semanales (96 hs totales)
- Economía Internacional: 6 hs semanales (96 hs totales)
- Inglés Técnico I: 4 hs semanales (64 hs totales)
- Inglés Nivel IV: 4 hs semanales (64 hs totales)

QUINTO AÑO:
- Relaciones Económicas Internacionales: 4 hs semanales (64 hs totales)
- Práctica Profesional: 8 hs semanales (128 hs totales)
- Derecho Internacional: 6 hs semanales (96 hs totales)
- Inglés Técnico II: 4 hs semanales (64 hs totales)

Total: 36 materias"""
            },
            {
                "id": "contador_plan_detallado",
                "carrera": "Contador Público - Plan de Estudios Detallado",
                "content": """Plan de estudios Contador Público con carga horaria:

PRIMER AÑO:
- Matemática I: 8 hs semanales (128 hs totales)
- Historia Económica Social y Contemporánea: 4 hs semanales (64 hs totales)
- Administración General: 8 hs semanales (128 hs totales)
- Computación Nivel I: 4 hs semanales (64 hs totales)
- Contabilidad Básica: 8 hs semanales (128 hs totales)
- Derecho Público: 4 hs semanales (64 hs totales)
- Introducción al Conocimiento Científico: 4 hs semanales (64 hs totales)

SEGUNDO AÑO:
- Inglés Nivel I: 4 hs semanales (64 hs totales)
- Matemática II: 6 hs semanales (96 hs totales)
- Derecho Civil: 4 hs semanales (64 hs totales)
- Economía General: 6 hs semanales (96 hs totales)
- Inglés Nivel II: 4 hs semanales (64 hs totales)
- Técnicas de Valuación: 8 hs semanales (128 hs totales)
- Derecho Comercial I: 4 hs semanales (64 hs totales)
- Macroeconomía: 6 hs semanales (96 hs totales)

TERCER AÑO:
- Estadística: 8 hs semanales (128 hs totales)
- Elementos de Costos: 8 hs semanales (128 hs totales)
- Psicosociología de las Organizaciones: 4 hs semanales (64 hs totales)
- Derecho Laboral y Previsional: 4 hs semanales (64 hs totales)
- Computación Nivel II: 4 hs semanales (64 hs totales)
- Estados Contables: 8 hs semanales (128 hs totales)
- Matemática Financiera: 6 hs semanales (96 hs totales)
- Estructura Económica Argentina: 4 hs semanales (64 hs totales)

CUARTO AÑO:
- Sistemas de Información: 6 hs semanales (96 hs totales)
- Derecho Comercial II: 4 hs semanales (64 hs totales)
- Finanzas Públicas: 6 hs semanales (96 hs totales)
- Costos y Actividades Especiales: 8 hs semanales (128 hs totales)
- Inglés Nivel III: 4 hs semanales (64 hs totales)
- Administración Financiera: 6 hs semanales (128 hs totales)
- Teoría y Técnica Impositiva I: 8 hs semanales (128 hs totales)
- Contabilidad y Administración Pública: 8 hs semanales (128 hs totales)

QUINTO AÑO:
- Teoría y Técnica Impositiva II: 8 hs semanales (128 hs totales)
- Auditoría: 8 hs semanales (128 hs totales)
- Inglés Nivel IV: 4 hs semanales (64 hs totales)
- Seminario de Práctica Profesional Administrativo Contable: 8 hs semanales (128 hs totales)
- Seminario de Práctica Profesional Jurídico Contable: 6 hs semanales (96 hs totales)

Total: 36 materias"""
            },
            {
                "id": "contacto_ingreso",
                "carrera": "Información General",
                "content": """Curso de Ingreso UNLaM: https://www.unlam.edu.ar/inicio/curso-de-ingreso/

Contacto Departamento de Ciencias Económicas:
- Teléfono: (54 11) 4480-8900 Int: 8954, 8819 y 8740
- Horario de Atención: 08:00 a 22:00 hs
- Correo electrónico: economicas@unlam.edu.ar

Todas las carreras son presenciales con una duración de 5 años."""
            }
        ]
        return documents
    
    def _create_embeddings(self):
        """Crea embeddings para todos los documentos"""
        embeddings = {}
        for doc in self.documents:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=doc["content"]
            )
            embeddings[doc["id"]] = response.data[0].embedding
        return embeddings
    
    def get_relevant_context(self, query: str, conversation_history: List[Dict] = None, top_k: int = 3) -> str:
        """
        Obtiene el contexto más relevante para una consulta considerando el historial
        
        Args:
            query: La pregunta actual del usuario
            conversation_history: Lista de mensajes previos [{"role": "user/assistant", "content": "..."}]
            top_k: Número de documentos a retornar
        """
        # Construir query enriquecida con contexto del historial
        enriched_query = query
        
        if conversation_history and len(conversation_history) > 0:
            # Extraer las últimas 2-3 interacciones para contexto
            recent_context = conversation_history[-6:]  # Últimos 3 intercambios (user + assistant)
            context_text = " ".join([msg["content"] for msg in recent_context if msg["role"] == "user"])
            enriched_query = f"{context_text} {query}"
        
        # Crear embedding de la consulta enriquecida
        query_response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=enriched_query
        )
        query_embedding = query_response.data[0].embedding
        
        # Calcular similitud con cada documento
        similarities = {}
        for doc in self.documents:
            doc_embedding = self.embeddings[doc["id"]]
            similarity = np.dot(query_embedding, doc_embedding)
            similarities[doc["id"]] = similarity
        
        # Obtener los top_k documentos más relevantes
        top_docs = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Construir contexto
        context_parts = []
        for doc_id, score in top_docs:
            if score > 0.5:  # Umbral de relevancia
                doc = next(d for d in self.documents if d["id"] == doc_id)
                context_parts.append(f"**{doc['carrera']}**\n{doc['content']}")
        
        return "\n\n".join(context_parts) if context_parts else ""