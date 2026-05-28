from playwright.sync_api import sync_playwright

def agregar_producto_fester(producto_recomendado):
    with sync_playwright() as p:
        # Aquí está el truco: le damos la ruta exacta del Chrome de la nube
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium"
        ) 
        page = browser.new_page()
        
        try:
            page.goto("https://www.fester.com.mx/es.html")
            
            page.click('.search-icon, .header-search, button[aria-label="Search"]', timeout=5000)
            page.fill('input[type="search"], input[name="q"]', producto_recomendado)
            page.press('input[type="search"], input[name="q"]', 'Enter')
            
            page.wait_for_timeout(3000) 
            
            page.click('.product-card a, .product-item a', timeout=5000)
            page.wait_for_timeout(3000)
            
            page.click('button[aria-label="Add to cart"]', timeout=5000)
            
            return f"¡Listo! Operación exitosa en segundo plano. {producto_recomendado} está en tu carrito."
            
        except Exception as e:
            return f"Hubo un obstáculo en la lectura de la página: {e}"
            
        finally:
            browser.close()
