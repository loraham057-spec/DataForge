from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
import time


URL = "https://www.gaaraas.com/fr/vehicle_listings/annonce-citroen-c3-dakar-dakar-304"


def create_driver():

    options = Options()
    options.add_argument("--start-maximized")

    return webdriver.Chrome(options=options)


def clean_text(text):

    return " ".join(
        text.split()
    ).strip()


def extract_detail_value(text, field):

    lines = [
        clean_text(line)
        for line in text.split("\n")
        if clean_text(line)
    ]

    for i, line in enumerate(lines):

        if line.upper() == field.upper():

            if i + 1 < len(lines):

                return lines[i + 1]

    return ""


def main():

    driver = create_driver()

    try:

        driver.get(URL)

        time.sleep(2)

        body = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

        print("=" * 70)
        print("🚗 TEST FICHE GAARAAS")
        print("=" * 70)

        # -----------------------------------------------------
        # Informations structurées
        # -----------------------------------------------------

        gearbox = extract_detail_value(
            body,
            "BOÎTE DE VITESSES"
        )

        mileage = extract_detail_value(
            body,
            "KILOMÉTRAGE"
        )

        year = extract_detail_value(
            body,
            "ANNÉE"
        )

        # -----------------------------------------------------
        # Prix
        # -----------------------------------------------------

        price_matches = re.findall(
            r"CFA\s*([\d\s]+)",
            body,
            re.IGNORECASE
        )

        price = ""

        if price_matches:

            price = (
                price_matches[-1]
                .replace(" ", "")
            )

        # -----------------------------------------------------
        # Région
        # -----------------------------------------------------

        region = ""

        lines = [
            clean_text(line)
            for line in body.split("\n")
            if clean_text(line)
        ]

        for line in lines:

            if line.lower() == "dakar":

                region = "Dakar"
                break

        # -----------------------------------------------------
        # Résultat
        # -----------------------------------------------------

        print("\nRésultats :")

        print(
            f"Boîte       : {gearbox}"
        )

        print(
            f"Kilométrage : {mileage}"
        )

        print(
            f"Année       : {year}"
        )

        print(
            f"Prix        : {price}"
        )

        print(
            f"Région      : {region}"
        )

    finally:

        driver.quit()


if __name__ == "__main__":
    main()