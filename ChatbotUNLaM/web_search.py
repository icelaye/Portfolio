import requests
from bs4 import BeautifulSoup
from typing import Optional

def search_unlam_web(query: str) -> str:
    """
    Intenta buscar información en el sitio web de UNLaM
    Nota: Esta es una implementación básica. En producción, 
    considera usar una API de búsqueda o scraping más robusto.
    """
    try:
        # URLs relevantes de UNLaM
        urls_to_check = [
            "https://www.unlam.edu.ar/inicio/curso-de-ingreso/",
            "https://www.unlam.edu.ar/index.php?seccion=3&idArticulo=3489",  # Ciencias Económicas
        ]
        
        content_parts = []
        
        for url in urls_to_check:
            try:
                # Hacer request con timeout
                response = requests.get(url, timeout=5, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extraer texto relevante
                    # Remover scripts y estilos
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Obtener texto
                    text = soup.get_text()
                    
                    # Limpiar texto
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    # Limitar longitud
                    if len(text) > 500:
                        text = text[:500] + "..."
                    
                    if text:
                        content_parts.append(f"Fuente: {url}\n{text}")
                        
            except Exception as e:
                continue
        
        return "\n\n".join(content_parts) if content_parts else ""
        
    except Exception as e:
        return ""

def fetch_unlam_page(url: str) -> Optional[str]:
    """
    Obtiene el contenido de una página específica de UNLaM
    """
    try:
        response = requests.get(url, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remover elementos no deseados
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Extraer texto
            text = soup.get_text()
            
            # Limpiar
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
    except Exception as e:
        return None
