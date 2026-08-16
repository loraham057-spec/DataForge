from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time


INPUT_FILE = "data/cleaned/books_full.csv"


def create_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def get_details(driver, url):

    driver.get(url)
    time.sleep(1)

    tax = None
    reviews = None

    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "table.table-striped tr"
    )

    print(f"      Lignes Product Information : {len(rows)}")

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

            print(f"      {field} → {value}")

            if field == "Tax":
                tax = value

            elif field == "Number of reviews":
                reviews = value

        except NoSuchElementException:
            continue

    return tax, reviews


df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig"
)

print("=" * 70)
print("TEST DE COMPLÉTION")
print("=" * 70)

print(f"\nNombre de lignes : {len(df)}")
print(f"URL présente : {'book_url' in df.columns}")

driver = create_driver()

try:

    for index in range(3):

        row = df.iloc[index]

        print("\n" + "-" * 70)
        print(f"Livre {index + 1}")
        print(f"Titre : {row['title']}")
        print(f"URL   : {row['book_url']}")

        tax, reviews = get_details(
            driver,
            row["book_url"]
        )

        print("\n      RÉSULTAT :")
        print(f"      Tax     = {tax}")
        print(f"      Reviews = {reviews}")

finally:

    driver.quit()