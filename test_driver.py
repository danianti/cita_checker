from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://www.google.com")
WebDriverWait(driver, 10).until(EC.title_contains("Google"))
print("Google loaded successfully")
driver.quit()
