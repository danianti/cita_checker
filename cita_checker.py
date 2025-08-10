import os
import time
import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Read secrets from environment variables
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
        if response.status_code != 200:
            logging.error(f"Telegram API returned status {response.status_code}: {response.text}")
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")

def create_driver():
    options = Options()
    options.add_argument("--headless=new")  # use new headless mode if supported
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--single-process")
    options.add_argument("--remote-debugging-port=9222")

    logging.info(f"Starting ChromeDriver with options: {options.arguments}")
    driver = webdriver.Chrome(options=options)
    return driver

def main():
    driver = None
    try:
        driver = create_driver()
        wait = WebDriverWait(driver, 30)

        logging.info("[STEP] Opening main page...")
        driver.get('https://icp.administracionelectronica.gob.es/icpplus/index.html')

        logging.info("[STEP] Selecting province Ávila...")
        province_select = wait.until(EC.presence_of_element_located((By.ID, "form")))
        select = Select(province_select)
        avila_value = "/icpplus/citar?p=5&locale=es"
        select.select_by_value(avila_value)
        logging.info("[INFO] Province Ávila selected")

        accept_btn = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        accept_btn.click()
        logging.info("[INFO] Clicked Accept button for province")

        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "cookie_action_close_header")))
            cookie_btn.click()
            logging.info("[INFO] Cookie consent accepted")
        except TimeoutException:
            logging.info("[INFO] No cookie consent popup found, continuing...")

        tramite_select_elem = wait.until(EC.presence_of_element_located((By.ID, "tramiteGrupo[1]")))
        tramite_select = Select(tramite_select_elem)
        logging.info("[INFO] Tramite dropdown found. Selecting tramite 4010...")
        tramite_select.select_by_value("4010")
        logging.info("[INFO] Tramite 4010 selected")

        btn_aceptar = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        btn_aceptar.click()
        logging.info("[INFO] Clicked Accept button after selecting tramite")

        presentacion_div = wait.until(EC.element_to_be_clickable((By.ID, "btnEntrar")))
        presentacion_div.click()
        logging.info("[INFO] Clicked 'Presentación sin Cl@ve' option")

        wait.until(EC.presence_of_element_located((By.ID, 'txtIdCitado'))).send_keys(NIE)
        driver.find_element(By.ID, 'txtDesCitado').send_keys(FULL_NAME)
        select_nationality = Select(driver.find_element(By.ID, 'txtPaisNac'))
        select_nationality.select_by_visible_text(NATIONALITY)
        logging.info("[INFO] Filled NIE, full name, nationality")

        wait.until(EC.element_to_be_clickable((By.ID, 'btnEnviar'))).click()
        logging.info("[INFO] Clicked final 'Aceptar' button (btnEnviar)")

        time.sleep(3)  # Allow page load

        page_source = driver.page_source
        no_appointments_msg = "En este momento no hay citas disponibles"

        if no_appointments_msg in page_source:
            logging.info("[INFO] No appointments available.")
            send_telegram_message("🚫 No hay citas disponibles en Ávila para POLICÍA-TOMA DE HUELLAS.")
        else:
            logging.info("[INFO] Appointments AVAILABLE!")
            send_telegram_message("🚨 Citas disponibles en Ávila para POLICÍA-TOMA DE HUELLAS. Reserve rápido!")

    except TimeoutException:
        logging.error("[ERROR] Timeout waiting for page elements.")
    except WebDriverException as wde:
        logging.error(f"[ERROR] WebDriver exception: {wde}")
    except Exception as e:
        logging.error(f"[ERROR] Exception occurred: {e}")
    finally:
        if driver:
            driver.quit()
            logging.info("[INFO] ChromeDriver quit successfully.")

if __name__ == "__main__":
    main()
