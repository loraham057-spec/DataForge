from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time


URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"


options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

try:

    driver.get(URL)

    time.sleep(1)

    tax = ""
    reviews = ""

    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "table.table-striped tr"
    )

    print(f"\nNombre de lignes trouvées : {len(rows)}")

    for row in rows:

        try:

            field = row.find_element(
                By.TAG_NAME,
                "th"
            ).text.strip()

            value = row.find_element(
                By.TAG_NAME,
                "td"
            ).text.strip()

            print(f"{field} → {value}")

            if field == "Tax":
                tax = value

            elif field == "Number of reviews":
                reviews = value

        except NoSuchElementException:
            continue

    print("\n" + "=" * 50)
    print("RÉSULTAT")
    print("=" * 50)

    print(f"Tax : {tax}")
    print(f"Reviews : {reviews}")

finally:

    driver.quit()