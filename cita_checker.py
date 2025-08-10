import os
import time
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import requests

# Read secrets from environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

NIE = 'Y5550506E'
FULL_NAME = 'FREDDY ABDIEL PERAZA BOLANOS'
NATIONALITY = 'VENEZUELA'

def log(msg):
    """Log with timestamp for CI debugging."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        log(f"Failed to send Telegram message: {e}")

def main():
    options = webdriver.ChromeOptions()

    # Headless in CI (set CI=true in GitHub Actions)
    if os.getenv("CI", "").lower() == "true":
        log("[INFO] Running in CI - enabling headless mode.")
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--remote-debugging-port=9222")

    driver = None
    try:
        log("[STEP] Starting ChromeDriver...")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 30)

        log("[STEP] Opening main page...")
        driver.get('https://icp.administracionelectronica.gob.es/icpplus/index.html')

        log("[STEP] Selecting province Ávila...")
        province_select = wait.until(EC.presence_of_element_located((By.ID, "form")))
        select = Select(province_select)
        select.select_by_value("/icpplus/citar?p=5&locale=es")
        log("[INFO] Province Ávila selected")

        wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar"))).click()
        log("[INFO] Clicked Accept button for province")

        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "cookie_action_close_header")))
            cookie_btn.click()
            log("[INFO] Cookie consent accepted")
        except TimeoutException:
            log("[INFO] No cookie consent popup found, continuing...")

        tramite_select_elem = wait.until(EC.presence_of_element_located((By.ID, "tramiteGrupo[1]")))
        tramite_select = Select(tramite_select_elem)
        log("[INFO] Tramite dropdown found. Selecting tramite 4010...")
        tramite_select.select_by_value("4010")
        log("[INFO] Tramite 4010 selected")

        wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar"))).click()
        log("[INFO] Clicked Accept button after selecting tramite")

        wait.until(EC.element_to_be_clickable((By.ID, "btnEntrar"))).click()
        log("[INFO] Clicked 'Presentación sin Cl@ve' option")

        wait.until(EC.presence_of_element_located((By.ID, 'txtIdCitado'))).send_keys(NIE)
        driver.find_element(By.ID, 'txtDesCitado').send_keys(FULL_NAME)
        Select(driver.find_element(By.ID, 'txtPaisNac')).select_by_visible_text(NATIONALITY)
        log("[INFO] Filled NIE, full name, nationality")

        wait.until(EC.element_to_be_clickable((By.ID, 'btnEnviar'))).click()
        log("[INFO] Clicked final 'Aceptar' button (btnEnviar)")

        time.sleep(3)  # Let results load

        page_source = driver.page_source
        if "En este momento no hay citas disponibles" in page_source:
            log("[INFO] No appointments available.")
            send_telegram_message("🚫 No hay citas disponibles en Ávila para POLICÍA-TOMA DE HUELLAS.")
        else:
            log("[INFO] Appointments AVAILABLE!")
            send_telegram_message("🚨 Citas disponibles en Ávila para POLICÍA-TOMA DE HUELLAS. Reserve rápido!")

    except TimeoutException:
        log("[ERROR] Timeout waiting for page elements.")
        traceback.print_exc()
    except Exception as e:
        log(f"[ERROR] Exception occurred: {e}")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            log("[INFO] ChromeDriver quit successfully.")

if __name__ == "__main__":
    main()
