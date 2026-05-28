from playwright.sync_api import sync_playwright

def agregar_producto_fester(producto_recomendado):
    """Navega por la página oficial de Fester y agrega el producto exacto al carrito."""
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
            
            # 3. Escribir el producto real (ej: "Proshield")
            page.fill('input[type="search"], input[name="q"]', producto_recomendado)
            page.press('input[type="search"], input[name="q"]', 'Enter')
            
            # Esperar a que carguen los resultados reales
            page.wait_for_timeout(5000) 
            
            # 4. CLIC DE PRECISIÓN: Buscamos enlaces que estén DENTRO de los resultados,
            # ignorando el botón de "Skip to Content" y menús.
            # Buscamos clases comunes en Fester como .teaser o .product-card
            selector_producto = ".teaser__title-link, .product-item a, .cmp-teaser__title-link"
            
            if page.locator(selector_producto).count() > 0:
                page.locator(selector_producto).first.click(timeout=10000)
            else:
                # Si no encuentra las clases, busca el primer enlace que NO sea el de Skip
                page.locator('main a, #maincontent a').first.click(timeout=10000)
            
            page.wait_for_timeout(4000)
            
            # 5. Clic al botón de agregar al carrito (tu llave maestra)
            page.click('button[aria-label="Add to cart"]', timeout=10000)
            
            return f"¡Misión cumplida! He agregado {producto_recomendado} a tu carrito en Fester México."
            
        except Exception as e:
            return f"El robot no pudo completar el clic. El diseño de la página dice: {e}"
            
        finally:
            browser.close()
