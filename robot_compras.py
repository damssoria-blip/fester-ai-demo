from playwright.sync_api import sync_playwright
import time

def agregar_producto_fester(producto_recomendado):
    """Navega por la página oficial de Fester y simula la interacción del usuario."""
    
    with sync_playwright() as p:
        # headless=False abre el navegador de forma visible para que veas la magia
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        try:
            print(f"Entrando al sitio oficial para buscar: {producto_recomendado}")
            page.goto("https://www.fester.com.mx/es.html")
            
            # 1. Hacer clic en la lupa (selectores genéricos estándar)
            page.click('.search-icon, .header-search, button[aria-label="Search"]', timeout=5000)
            
            # 2. Escribir y buscar
            page.fill('input[type="search"], input[name="q"]', producto_recomendado)
            page.press('input[type="search"], input[name="q"]', 'Enter')
            
            page.wait_for_timeout(3000) 
            
            # 3. Clic en el primer producto que cargue
            page.click('.product-card a, .product-item a', timeout=5000)
            page.wait_for_timeout(3000)
            
            # 4. EL CLIC AL BOTÓN CON TU CÓDIGO EXACTO
            print("Buscando el botón de agregar al carrito...")
            page.click('button[aria-label="Add to cart"]', timeout=5000)
            
            print("¡Producto agregado al carrito con éxito!")
            time.sleep(4)
            return f"¡Listo! He abierto la tienda oficial y agregado {producto_recomendado} a tu carrito."
            
        except Exception as e:
            print(f"Error al
