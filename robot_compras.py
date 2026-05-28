from playwright.sync_api import sync_playwright
import os

# Truco para que el servidor de la nube instale el navegador fantasma automáticamente
os.system("playwright install chromium")

def agregar_producto_fester(producto_recomendado):
    with sync_playwright() as p:
        # headless=True es OBLIGATORIO en la nube porque los servidores no tienen monitor
        browser = p.chromium.launch(headless=True) 
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
            
            return f"¡Listo! Operación exitosa en segundo plano. {producto_recomendado} está en el carrito."
            
        except Exception as e:
            return f"Hubo un obstáculo en la lectura del código de la página web."
            
        finally:
            browser.close()
