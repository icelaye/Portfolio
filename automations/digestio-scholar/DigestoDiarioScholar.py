import openai
from datetime import datetime, timedelta
import os
import time
import requests

# ============================================================================
# SISTEMA DE CONTROL DE DUPLICADOS
# ============================================================================

def cargar_papers_enviados():
    """
    Carga la lista de títulos de papers ya enviados
    """
    archivo = 'papers_enviados.txt'
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def guardar_paper_enviado(titulo):
    """
    Guarda el título de un paper como enviado
    """
    archivo = 'papers_enviados.txt'
    with open(archivo, 'a', encoding='utf-8') as f:
        f.write(f"{titulo}\n")

def filtrar_papers_nuevos(papers, papers_enviados):
    """
    Filtra papers que no han sido enviados previamente
    """
    papers_nuevos = []
    papers_duplicados = 0
    
    for paper in papers:
        if paper['titulo'] not in papers_enviados:
            papers_nuevos.append(paper)
        else:
            papers_duplicados += 1
    
    print(f"\n📊 Filtrado de duplicados:")
    print(f"   Papers totales encontrados: {len(papers)}")
    print(f"   Papers ya enviados (duplicados): {papers_duplicados}")
    print(f"   Papers nuevos a enviar: {len(papers_nuevos)}")
    
    return papers_nuevos

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configuración
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'tu-api-key-local')
openai.api_key = OPENAI_API_KEY
ENVIAR_EMAIL = True

# CONFIGURACIÓN DE SEMANTIC SCHOLAR
MIN_CITATIONS = 3
MAX_PAPERS_SEMANTIC = 50

# ============================================================================
# MÓDULO DE ENVÍO DE EMAILS
# ============================================================================

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# CONFIGURACIÓN DE EMAIL
DESTINATARIOS = [
    "icelaye363@gmail.com",
    "marianoftaha@gmail.com",
    "diegofloresv16@gmail.com"
]

GMAIL_REMITENTE = "icelaye363@gmail.com"
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD', 'wgfc doem nrvm dvcb')

def enviar_email_gmail(archivo_html, destinatarios=None):
    """
    Envía el digesto usando Gmail
    """
    if destinatarios is None:
        destinatarios = DESTINATARIOS
    
    print(f"\n📧 Enviando email a {len(destinatarios)} destinatarios...")
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = GMAIL_REMITENTE
        msg['To'] = ", ".join(destinatarios)
        msg['Subject'] = f"📚 Digesto Semanal Data Science - {datetime.now().strftime('%d/%m/%Y')}"
        
        with open(archivo_html, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        parte_html = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(parte_html)
        
        with open(archivo_html, 'rb') as f:
            adjunto = MIMEBase('application', 'octet-stream')
            adjunto.set_payload(f.read())
            encoders.encode_base64(adjunto)
            adjunto.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(archivo_html)}'
            )
            msg.attach(adjunto)
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_REMITENTE, GMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email enviado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar email: {str(e)}")
        return False

# ============================================================================
# BÚSQUEDA EN SEMANTIC SCHOLAR
# ============================================================================

def buscar_papers_semantic_scholar(fecha_desde, fecha_hasta, campos_query, min_citations=MIN_CITATIONS, limit=50):
    """
    Busca papers en Semantic Scholar por fecha y área con reintentos automáticos
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    fecha_desde_str = fecha_desde.strftime('%Y-%m-%d')
    fecha_hasta_str = fecha_hasta.strftime('%Y-%m-%d')
    
    papers_dict = {}
    
    print(f"📊 Buscando papers en Semantic Scholar...")
    print(f"   Rango: {fecha_desde_str} a {fecha_hasta_str}")
    print(f"   Mínimo de citas: {min_citations}")
    
    for i, campo in enumerate(campos_query, 1):
        print(f"\n   [{i}/{len(campos_query)}] Buscando: {campo}...", end=' ')
        
        params = {
            'query': campo,
            'limit': limit,
            'fields': 'title,abstract,authors,year,citationCount,url,venue,publicationDate,publicationTypes',
            'minCitationCount': min_citations,
            'publicationDateOrYear': f'{fecha_desde_str}:{fecha_hasta_str}',
            'publicationTypes': 'JournalArticle,Conference,Review'
        }
        
        # Sistema de reintentos
        max_intentos = 5
        intento_actual = 0
        exito = False
        
        while intento_actual < max_intentos and not exito:
            try:
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    # Éxito
                    data = response.json()
                    papers_encontrados = data.get('data', [])
                    
                    for paper_data in papers_encontrados:
                        if not paper_data.get('abstract'):
                            continue
                        
                        paper = {
                            'titulo': paper_data.get('title', 'Sin título'),
                            'autores': ', '.join([autor.get('name', '') for autor in paper_data.get('authors', [])[:5]]),
                            'resumen': paper_data.get('abstract', ''),
                            'link': paper_data.get('url', ''),
                            'fecha': paper_data.get('publicationDate', fecha_desde_str),
                            'categorias': [paper_data.get('venue', 'N/A')],
                            'citas': paper_data.get('citationCount', 0),
                            'tipo': paper_data.get('publicationTypes', [])
                        }
                        
                        if paper['titulo'] not in papers_dict:
                            papers_dict[paper['titulo']] = paper
                    
                    print(f"✓ {len(papers_encontrados)} papers")
                    exito = True
                    
                elif response.status_code == 429:
                    # Rate limit - reintentar
                    intento_actual += 1
                    if intento_actual < max_intentos:
                        tiempo_espera = 5 * (2 ** intento_actual)  # Backoff exponencial: 30, 60, 120, 240 segundos
                        print(f"\n      ⚠️ Rate limit (intento {intento_actual}/{max_intentos}). Esperando {tiempo_espera}s...")
                        time.sleep(tiempo_espera)
                    else:
                        print(f"\n      ❌ Máximo de reintentos alcanzado. Continuando con siguiente query...")
                        
                else:
                    # Otro error HTTP
                    print(f"⚠️ Error {response.status_code}")
                    break
                    
            except requests.exceptions.Timeout:
                intento_actual += 1
                if intento_actual < max_intentos:
                    print(f"\n      ⏱️ Timeout (intento {intento_actual}/{max_intentos}). Reintentando...")
                    time.sleep(10)
                else:
                    print(f"\n      ❌ Timeout persistente. Continuando...")
                    break
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                break
        
        # Pausa entre queries exitosas
        if exito:
            time.sleep(12)  # Pausa base entre queries
    
    all_papers = list(papers_dict.values())
    all_papers.sort(key=lambda x: (x['citas'], x['fecha']), reverse=True)
    
    return all_papers

def buscar_papers_dia_anterior():
    """
    Busca papers del día anterior (t-2) usando Semantic Scholar
    """
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ayer_inicio = hoy - timedelta(days=7)
    ayer_fin = hoy - timedelta(seconds=1)
    
    queries = [
        'machine learning',
        'deep learning',
        'artificial intelligence',
        'natural language processing',
        'reinforcement learning',
        'neural networks',
        'data science',
        'knowledge graphs',
        'language models',
        'transformers',
        'econometrics',
        'chatgpt',
        'big data',
        'mlops',
        'causal inference'
    ]
    
    papers = buscar_papers_semantic_scholar(
        fecha_desde=ayer_inicio,
        fecha_hasta=ayer_fin,
        campos_query=queries,
        min_citations=MIN_CITATIONS,
        limit=50
    )
    
    if len(papers) > MAX_PAPERS_SEMANTIC:
        papers = papers[:MAX_PAPERS_SEMANTIC]
    
    return papers

# ============================================================================
# GENERACIÓN DE DIGESTOS
# ============================================================================

def generar_digesto(resumen, titulo, modelo='gpt-4o-mini'):
    """
    Genera un digesto académico estructurado usando la API de OpenAI
    """
    try:
        response = openai.chat.completions.create(
            model=modelo,
            messages=[
                {
                    "role": "system",
                    "content": """Eres un experto en análisis de papers científicos. Genera digestos académicos estructurados en español.

IMPORTANTE: NO incluyas títulos como "DIGESTO ACADÉMICO" o numeración al inicio. Comienza DIRECTAMENTE con "TEMA/PROBLEMA:".

Estructura OBLIGATORIA (3-4 oraciones concisas):
TEMA/PROBLEMA: ¿Qué problema o tema aborda?
MÉTODO/ENFOQUE: ¿Qué metodología o técnica propone?
HALLAZGO/APORTE: ¿Cuál es el principal resultado o contribución?
RELEVANCIA: ¿Por qué es importante? (opcional si es evidente)

Usa lenguaje técnico pero claro. Sé preciso y objetivo."""
                },
                {
                    "role": "user",
                    "content": f"Genera un digesto académico para:\n\nTÍTULO: {titulo}\n\nABSTRACT: {resumen}"
                }
            ],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error al generar digesto: {str(e)}"

import re

def procesar_digesto_html(digesto):
    # Quitar encabezados basura tipo "DIGESTO ACADÉMICO"
    digesto = re.sub(r'^\*?\*?DIGESTO\s+ACADÉMICO.*?\n', '', digesto, flags=re.IGNORECASE)

    # Transformación de TEMA/PROBLEMA
    digesto = digesto.replace('TEMA/PROBLEMA:', '<strong>TEMA/PROBLEMA:</strong> ')

    # Transformación del resto de secciones
    secciones = ['MÉTODO/ENFOQUE:', 'HALLAZGO/APORTE:', 'RELEVANCIA:']
    for seccion in secciones:
        digesto = digesto.replace(seccion, f'<br><br><strong>{seccion}</strong> ')

    # Limpiar saltos de línea iniciales o espacios sobrantes
    digesto = digesto.strip()

    return digesto


def crear_reporte(papers):
    """
    Crea un reporte formateado con los papers encontrados
    """
    print(f"\n{'='*80}")
    print(f"REPORTE DE PAPERS RECIENTES - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Total de papers encontrados: {len(papers)}")
    print(f"{'='*80}\n")
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper['titulo']}")
        print(f"   Fecha: {paper['fecha']}")
        print(f"   Citas: {paper.get('citas', 0)}")
        print(f"   Autores: {paper['autores'][:100]}...")
        print(f"   Link: {paper['link']}")
        
        digesto = generar_digesto(paper['resumen'], paper['titulo'])
        print(f"   {digesto}")
        print(f"\n   {'-'*76}")

def guardar_reporte_html(papers, nombre_archivo='reporte_papers.html'):
    """
    Guarda el reporte en formato HTML
    """
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digesto de Papers - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .paper {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .titulo {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 12px;
            line-height: 1.4;
        }}
        .metadata {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin: 8px 0;
        }}
        .metadata a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        .metadata a:hover {{
            text-decoration: underline;
        }}
        .digesto {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            border-left: 3px solid #3498db;
            line-height: 1.7;
        }}
        .citas-badge {{
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .categoria-tag {{
            display: inline-block;
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 5px;
        }}
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 Digesto de Papers Académicos</h1>
        <p>{(datetime.now() - timedelta(days=1)).strftime('%d de %B de %Y')}</p>
    </div>
    
    <div class="stats">
        <h2>Papers seleccionados: {len(papers)}</h2>
        <p>Ordenados por relevancia (citaciones)</p>
    </div>
"""
    
    for i, paper in enumerate(papers, 1):
        digesto_raw = generar_digesto(paper['resumen'], paper['titulo'])
        digesto = procesar_digesto_html(digesto_raw)
        
        categorias_html = ''.join([f'<span class="categoria-tag">{cat}</span>' 
                                   for cat in paper['categorias'][:5]])
        
        citas = paper.get('citas', 0)
        
        html += f"""
    <div class="paper">
        <div class="titulo">
            {i}. {paper['titulo']}
            <span class="citas-badge">📊 {citas} citas</span>
        </div>
        <div class="metadata">📅 {paper['fecha']} | 👥 {paper['autores'][:150]}...</div>
        <div class="metadata">🔗 <a href="{paper['link']}" target="_blank">Ver en Semantic Scholar</a></div>
        <div class="metadata">🏷️ {categorias_html}</div>
        <div class="digesto">
            {digesto}
        </div>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Reporte HTML guardado en: {nombre_archivo}")

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("🔍 Buscando papers del día anterior...\n")
    
    fecha_archivo = datetime.now().strftime('%Y-%m-%d')
    nombre_html = f'digesto_papers_{fecha_archivo}.html'
    
    # Cargar papers ya enviados
    papers_enviados = cargar_papers_enviados()
    print(f"📚 Papers en historial: {len(papers_enviados)}")
    
    # Buscar nuevos papers
    papers = buscar_papers_dia_anterior()
    
    if papers:
        # Filtrar duplicados
        papers_nuevos = filtrar_papers_nuevos(papers, papers_enviados)
        
        if papers_nuevos:
            print(f"\n📋 Total de papers NUEVOS encontrados: {len(papers_nuevos)}")
            
            crear_reporte(papers_nuevos)
            guardar_reporte_html(papers_nuevos, nombre_html)
            
            # Guardar los títulos de papers nuevos como enviados
            for paper in papers_nuevos:
                guardar_paper_enviado(paper['titulo'])
            
            if ENVIAR_EMAIL:
                enviar_email_gmail(nombre_html)
            
            print(f"\n✅ Proceso completado exitosamente!")
            print(f"📝 {len(papers_nuevos)} nuevos papers guardados en el historial")
        else:
            print("\n⚠️ No se encontraron papers nuevos (todos son duplicados)")
            print("   No se enviará email")
    else:
        print("❌ No se encontraron papers en el período especificado.")
