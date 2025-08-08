from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import requests

# Your Telegram details
TELEGRAM_TOKEN = '8322483491:AAGLfls2dUvCs1zAIF4CXE00l2P-5qgUdyE'
TELEGRAM_CHAT_ID = '8131218642'

# Your personal info
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
    # options.add_argument("--headless")  # Comment this if you want to see the browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        # Open direct Ávila booking page
        driver.get('https://icp.administracionelectronica.gob.es/icpplus/citar?p=5&locale=es')

        # Fill NIE
        wait.until(EC.presence_of_element_located((By.ID, 'txtIdCitado'))).send_keys(NIE)
        # Fill full name
        driver.find_element(By.ID, 'txtDesCitado').send_keys(FULL_NAME)
        # Select nationality
        select_nationality = Select(driver.find_element(By.ID, 'txtPaisNac'))
        select_nationality.select_by_visible_text(NATIONALITY)

        # Click "Aceptar" button
        wait.until(EC.element_to_be_clickable((By.ID, 'btnAceptar'))).click()

        # Wait for next page with tramite select to load
        wait.until(EC.presence_of_element_located((By.ID, 'tramiteGrupo[1]')))

        # Select the tramite with value 4010
        tramite_select = Select(driver.find_element(By.ID, 'tramiteGrupo[1]'))
        tramite_select.select_by_value('4010')

        time.sleep(1)  # Wait a bit for page JS to load after selection

        # Click "Solicitar Cita"
        wait.until(EC.element_to_be_clickable((By.ID, 'btnEnviar'))).click()

        # Wait for result page to load - look for either "no hay citas disponibles" or proceed step text
        time.sleep(3)  # Wait for the page to load content

        page_source = driver.page_source

        no_appointments_msg = "En este momento no hay citas disponibles para la reserva sin cl@ve."

        if no_appointments_msg in page_source:
            print("[INFO] No appointments available.")
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
