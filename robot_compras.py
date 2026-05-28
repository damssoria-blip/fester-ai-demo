from playwright.sync_api import sync_playwright

def agregar_producto_fester(producto_recomendado):
    """Navega por la página oficial de Fester, busca un producto y lo agrega al carrito en la nube."""
    with sync_playwright() as p:
        # Configuración OBLIGATORIA para que no explote en la nube de Streamlit
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium"
        ) 
        page = browser.new_page()
        
        try:
            # Le damos hasta 60 segundos para cargar la página inicial por si el servidor está lento
            page.goto("https://www.fester.com.mx/es.html", timeout=60000)
            
            # 1. Hacer clic en la lupa para abrir el buscador
            page.click('.search-icon, .header-search, button[aria-label="Search"]', timeout=8000)
            
            # 2. Escribir el producto y dar Enter
            page.fill('input[type="search"], input[name="q"]', producto_recomendado)
            page.press('input[type="search"], input[name="q"]', 'Enter')
            
            # Pausa de 5 segundos para que la página de Fester arroje los resultados
            page.wait_for_timeout(5000) 
            
            # 3. EL TRUCO RUDO: Clic en el PRIMER enlace que encuentre en la página de resultados
            # Usamos .first para decirle "no te confundas, agarra el primero de la lista"
            page.locator('a.teaser-link, a.product-link, a').first.click(timeout=8000)
            
            # Esperamos a que cargue la página del detalle del producto
            page.wait_for_timeout(4000)
            
            # 4. EL CLIC AL BOTÓN DE AGREGAR AL CARRITO (con la llave maestra que descubriste)
            page.click('button[aria-label="Add to cart"]', timeout=8000)
            
            # Pausa final cortita para asegurar que el sistema de Fester procesó el carrito
            page.wait_for_timeout(2000)
            
            return f"¡Misión cumplida! El robot operó en silencio y agregó {producto_recomendado} a tu carrito."
            
        except Exception as e:
            # Si algo falla, ahora nos dirá exactamente en qué paso se tropezó
            return f"Hubo un obstáculo visual al navegar por Fester. Detalle del error: {e}"
            
        finally:
            browser.close()
