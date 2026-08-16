from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


URL = "https://www.gaaraas.com/fr/vehicle_listings/annonce-citroen-c3-dakar-dakar-304"


options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

try:

    driver.get(URL)

    time.sleep(2)

    print("=" * 70)
    print("🚗 DIAGNOSTIC ANNONCE GAARAAS")
    print("=" * 70)

    print("\nTitre de la page :")
    print(driver.title)

    print("\nURL :")
    print(driver.current_url)

    print("\n" + "=" * 70)
    print("TEXTE DE LA PAGE")
    print("=" * 70)

    body_text = driver.find_element(
        By.TAG_NAME,
        "body"
    ).text

    print(body_text)

finally:

    driver.quit()

    print("\nNavigateur fermé.")