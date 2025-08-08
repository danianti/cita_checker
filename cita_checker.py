from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import requests
import tempfile
import os

# Get secrets from environment variables (set in GitHub Actions)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

NIE = 'Y5550506E'
FULL_NAME = 'FREDDY ABDIEL PERAZA BOLANOS'
NATIONALITY = 'VENEZUELA'

def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': text}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("[INFO] Telegram message sent successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")

def main():
    options = webdriver.ChromeOptions()
    # Uncomment if you want headless mode (recommended on CI)
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Create a unique temp dir for user data to avoid 'user data dir in use' error
    temp_user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_user_data_dir}")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        print("[STEP] Opening main page...")
        driver.get('https://icp.administracionelectronica.gob.es/icpplus/index.html')

        print("[STEP] Selecting province Ávila...")
        province_select = wait.until(EC.presence_of_element_located((By.ID, "form")))
        select = Select(province_select)
        avila_value = "/icpplus/citar?p=5&locale=es"
        select.select_by_value(avila_value)
        print("[INFO] Province Ávila selected")

        accept_btn = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        accept_btn.click()
        print("[INFO] Clicked Accept button for province")

        # Accept cookies if present
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

        btn_aceptar = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        btn_aceptar.click()
        print("[INFO] Clicked Accept button after selecting tramite")

        presentacion_div = wait.until(EC.element_to_be_clickable((By.ID, "btnEntrar")))
        presentacion_div.click()
        print("[INFO] Clicked 'Presentación sin Cl@ve' option")

        wait.until(EC.presence_of_element_located((By.ID, 'txtIdCitado'))).send_keys(NIE)
        driver.find_element(By.ID, 'txtDesCitado').send_keys(FULL_NAME)
        select_nationality = Select(driver.find_element(By.ID, 'txtPaisNac'))
        select_nationality.select_by_visible_text(NATIONALITY)
        print("[INFO] Filled NIE, full name, nationality")

        wait.until(EC.element_to_be_clickable((By.ID, 'btnEnviar'))).click()
        print("[INFO] Clicked final 'Aceptar' button (btnEnviar)")

        time.sleep(3)

        page_source = driver.page_source
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
