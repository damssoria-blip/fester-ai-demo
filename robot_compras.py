from playwright.sync_api import sync_playwright

def agregar_producto_fester(producto_recomendado):
    """Navega por la página oficial de Fester y agrega el producto usando localización visual."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium"
        ) 
        page = browser.new_page()
        
        try:
            # 1. Entrar a Fester
            page.goto("https://www.fester.com.mx/es.html", timeout=60000)
            
            # 2. Abrir buscador
            page.click('.search-icon, .header-search, button[aria-label="Search"]', timeout=10000)
            
            # 3. Escribir el producto real
            page.fill('input[type="search"], input[name="q"]', producto_recomendado)
            page.press('input[type="search"], input[name="q"]', 'Enter')
            
            # Esperar a que carguen los resultados
            page.wait_for_timeout(5000) 
            
            # 4. CLIC DE PRECISIÓN: Seleccionar el primer producto real
            selector_producto = ".teaser__title-link, .product-item a, .cmp-teaser__title-link"
            if page.locator(selector_producto).count() > 0:
                page.locator(selector_producto).first.click(timeout=10000)
            else:
                page.locator('main a, #maincontent a').first.click(timeout=10000)
            
            page.wait_for_timeout(5000)
            
            # 5. EL MODO HUMANO: Buscar el botón visualmente por su texto en mayúsculas
            page.locator('button:has-text("AGREGAR AL CARRITO")').first.click(timeout=15000)
            
            # Pausa para que el servidor registre el clic
            page.wait_for_timeout(3000)
            
            return f"¡Misión cumplida! He agregado {producto_recomendado} a tu carrito usando el modo de lectura visual."
            
        except Exception as e:
            return f"El robot llegó al producto, pero no pudo hacer el clic final. Error: {e}"
            
        finally:
            browser.close()
