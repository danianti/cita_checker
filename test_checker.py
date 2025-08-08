import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import requests

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Telegram token or chat ID not set in environment variables")

NIE = 'Y5550506E'
FULL_NAME = 'FREDDY ABDIEL PERAZA BOLANOS'
NATIONALITY = 'VENEZUELA'

def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        print("[STEP] Opening main page...")
        driver.get('https://icp.administracionelectronica.gob.es/icpplus/index.html')

        # Step 1: Select province Ávila
        print("[STEP] Selecting province Ávila...")
        province_select = wait.until(EC.presence_of_element_located((By.ID, "form")))
        select = Select(province_select)
        avila_value = "/icpplus/citar?p=5&locale=es"
        select.select_by_value(avila_value)
        print("[INFO] Province Ávila selected")

        accept_btn = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        accept_btn.click()
        print("[INFO] Clicked Accept button for province")

        # Step 2: Accept cookies if present
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "cookie_action_close_header")))
            cookie_btn.click()
            print("[INFO] Cookie consent accepted")
        except TimeoutException:
            print("[INFO] No cookie consent popup found, continuing...")

        # Select tramite 4010
        tramite_select_elem = wait.until(EC.presence_of_element_located((By.ID, "tramiteGrupo[1]")))
        tramite_select = Select(tramite_select_elem)
        print("[INFO] Tramite dropdown found. Selecting tramite 4010...")
        tramite_select.select_by_value("4010")
        print("[INFO] Tramite 4010 selected")

        # Click Aceptar button
        btn_aceptar = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        btn_aceptar.click()
        print("[INFO] Clicked Accept button after selecting tramite")

        # Step 3: Click Presentación sin Cl@ve
        presentacion_div = wait.until(EC.element_to_be_clickable((By.ID, "btnEntrar")))
        presentacion_div.click()
        print("[INFO] Clicked 'Presentación sin Cl@ve' option")

        # Step 4: Fill form with NIE, name, nationality
        wait.until(EC.presence_of_element_located((By.ID, 'txtIdCitado'))).send_keys(NIE)
        driver.find_element(By.ID, 'txtDesCitado').send_keys(FULL_NAME)
        select_nationality = Select(driver.find_element(By.ID, 'txtPaisNac'))
        select_nationality.select_by_visible_text(NATIONALITY)
        print("[INFO] Filled NIE, full name, nationality")

        # Click final Accept button (btnEnviar)
        wait.until(EC.element_to_be_clickable((By.ID, 'btnEnviar'))).click()
        print("[INFO] Clicked final 'Aceptar' button (btnEnviar)")

        # Wait for page load before checking messages
        time.sleep(3)

        page_source = driver.page_source

        # The no appointments message text to look for (partial substring OK)
        no_appointments_msg = "En este momento no hay citas disponibles"

        if no_appointments_msg in page_source:
            print("[INFO] No appointments available.")
            send_telegram_message("🚫 No hay citas disponibles en Ávila para POLICÍA-TOMA DE HUELLAS.")
        else:
            print("[INFO] Appointments AVAILABLE!")
            send_telegram_message("🚨 Citas disponibles en Ávila para POLICÍA-TOMA DE HUELLAS. Reserve rápido!")

    except TimeoutException:
        print("[ERROR] Timeout waiting for page elements.")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
