from playwright.sync_api import sync_playwright

def agregar_producto_fester(producto_recomendado):
    """Navega por la página oficial de Fester, busca un producto y lo agrega al carrito en la nube."""
    with sync_playwright() as p:
        # Configuración obligatoria para que el navegador funcione en el servidor de la nube
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium"
        ) 
        page = browser.new_page()
        
        try:
            # Abrir el sitio oficial de Fester México
            page.goto("https://www.fester.com.mx/es.html", timeout=60000)
            
            # 1. Hacer clic en el icono de la lupa para abrir el buscador
            page.click('.search-icon, .header-search, button[aria-label="Search"]', timeout=8000)
            
            # 2. Escribir el producto recomendado y presionar Enter
            page.fill('input[type="search"], input[name="q"]', producto_recomendado)
            page.press('input[type="search"], input[name="q"]', 'Enter')
            
            # Esperar 5 segundos a que la página procese y muestre los resultados
            page.wait_for_timeout(5000) 
            
            # 3. Hacer clic en el primer producto de la lista de resultados
            page.locator('a.teaser-link, a.product-link, a').first.click(timeout=8000)
            
            # Esperar 4 segundos a que cargue la página de detalles del producto
            page.wait_for_timeout(4000)
            
            # 4. Hacer clic en el botón "Agregar al carrito" usando la etiqueta exacta
            page.click('button[aria-label="Add to cart"]', timeout=8000)
            
            # Pausa de confirmación
            page.wait_for_timeout(2000)
            
            return f"¡Misión cumplida! El sistema automático agregó {producto_recomendado} a tu carrito en la tienda oficial."
            
        except Exception as e:
            return f"Hubo un contratiempo visual en la página oficial. Detalle del error: {e}"
            
        finally:
            browser.close()
