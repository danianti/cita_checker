from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment if you want no browser window

service = Service()  # Or specify path: Service('/path/to/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get('https://icp.administracionelectronica.gob.es/icpplus/index.html')

    wait = WebDriverWait(driver, 30)

    # Wait for province dropdown and select Ávila
    province_select = wait.until(EC.presence_of_element_located((By.ID, "prov_selecc")))
    select = Select(province_select)
    select.select_by_visible_text("Ávila")

    # Wait for Accept button and click
    accept_button = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
    accept_button.click()

    print("[INFO] Selected Ávila and clicked Accept")

    # Add a pause or wait here to observe what page loads next
    # For example:
    wait.until(EC.url_contains('citar'))  # waits for URL change containing 'citar'
    print("[INFO] Moved to next page:", driver.current_url)

finally:
    driver.quit()
