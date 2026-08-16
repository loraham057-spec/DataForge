from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import re
import time
import os


BASE_URL = "https://www.gaaraas.com/fr/users/dakar-auto?page={}"

TARGET_PAGES = 100

OUTPUT_FILE = "data/cleaned/gaaraas_full.csv"


def create_driver():

    options = Options()
    options.add_argument("--start-maximized")

    return webdriver.Chrome(options=options)


def clean_text(text):

    if not text:
        return ""

    return " ".join(
        text.split()
    ).strip()


def extract_detail_value(body, field):

    lines = [
        clean_text(line)
        for line in body.split("\n")
        if clean_text(line)
    ]

    for i, line in enumerate(lines):

        if line.upper() == field.upper():

            if i + 1 < len(lines):

                return lines[i + 1]

    return ""


def extract_price(text):

    matches = re.findall(
        r"CFA\s*([\d\s]+)",
        text,
        re.IGNORECASE
    )

    if not matches:
        return None

    value = (
        matches[-1]
        .replace(" ", "")
        .strip()
    )

    try:
        return int(value)

    except ValueError:
        return None


def extract_vehicle_name(body):

    lines = [
        clean_text(line)
        for line in body.split("\n")
        if clean_text(line)
    ]

    for line in lines:

        if line.startswith("Détails"):

            name = line.replace(
                "Détails",
                "",
                1
            ).strip()

            if name:
                return name

    for i, line in enumerate(lines):

        if line.lower() == "détails":

            if i + 1 < len(lines):

                return lines[i + 1]

    return ""


def split_brand_model(vehicle_name):

    vehicle_name = clean_text(
        vehicle_name
    )

    if not vehicle_name:
        return "", ""

    multiword_brands = [
        "Land Rover",
        "Alfa Romeo",
        "Mercedes Benz",
        "Mercedes-Benz",
        "Aston Martin",
        "Rolls Royce"
    ]

    for brand in multiword_brands:

        if vehicle_name.lower().startswith(
            brand.lower()
        ):

            model = vehicle_name[
                len(brand):
            ].strip()

            return brand, model

    parts = vehicle_name.split()

    if len(parts) == 1:

        return parts[0], ""

    return (
        parts[0],
        " ".join(parts[1:])
    )


def clean_year(value):

    if not value:
        return None

    value = value.strip()

    if value.upper() in [
        "N/A",
        "NA",
        "N.A.",
        "-"
    ]:
        return None

    match = re.search(
        r"\b(19|20)\d{2}\b",
        value
    )

    if match:
        return int(match.group())

    return None


def clean_mileage(value):

    if not value:
        return None

    value = value.strip()

    if value.upper() in [
        "N/A",
        "NA",
        "N.A.",
        "-"
    ]:
        return None

    match = re.search(
        r"([\d\s]+)",
        value
    )

    if not match:
        return None

    number = (
        match.group(1)
        .replace(" ", "")
    )

    try:
        return int(number)

    except ValueError:
        return None


def get_region(body):

    lines = [
        clean_text(line)
        for line in body.split("\n")
        if clean_text(line)
    ]

    # Le site actuel affiche Dakar pour
    # les annonces de cette sélection.

    for line in lines:

        if line.lower() == "dakar":
            return "Dakar"

    return ""


def get_listing_urls(driver):

    listings = driver.find_elements(
        By.CSS_SELECTOR,
        "a[href*='/vehicle_listings/']"
    )

    urls = []

    seen = set()

    for listing in listings:

        href = listing.get_attribute(
            "href"
        )

        if href and href not in seen:

            seen.add(href)

            urls.append(href)

    return urls


def scrape_page(driver, page_number):

    url = BASE_URL.format(
        page_number
    )

    print("\n" + "=" * 70)

    print(
        f"📄 PAGE {page_number}"
    )

    print("=" * 70)

    driver.get(url)

    time.sleep(1)

    listing_urls = get_listing_urls(
        driver
    )

    print(
        f"Annonces trouvées : "
        f"{len(listing_urls)}"
    )

    if len(listing_urls) == 0:

        return []

    page_data = []

    for position, listing_url in enumerate(
        listing_urls,
        start=1
    ):

        print(
            f"\n   [{position}/{len(listing_urls)}]"
        )

        try:

            driver.get(
                listing_url
            )

            time.sleep(0.5)

            body = driver.find_element(
                By.TAG_NAME,
                "body"
            ).text

            vehicle_name = extract_vehicle_name(
                body
            )

            brand, model = split_brand_model(
                vehicle_name
            )

            year = clean_year(
                extract_detail_value(
                    body,
                    "ANNÉE"
                )
            )

            mileage = clean_mileage(
                extract_detail_value(
                    body,
                    "KILOMÉTRAGE"
                )
            )

            gearbox = extract_detail_value(
                body,
                "BOÎTE DE VITESSES"
            )

            gearbox = clean_text(
                gearbox
            )

            if gearbox.upper() == "N/A":

                gearbox = ""

            price = extract_price(
                body
            )

            region = get_region(
                body
            )

            page_data.append(
                {
                    "page": page_number,
                    "position_page": position,
                    "brand": brand,
                    "model": model,
                    "year": year,
                    "price": price,
                    "mileage": mileage,
                    "gearbox": gearbox,
                    "region": region,
                    "listing_url": listing_url
                }
            )

            print(
                f"      ✓ {brand} {model}"
                f" | {year}"
                f" | {price} CFA"
            )

        except Exception as e:

            print(
                f"      ❌ Erreur : {e}"
            )

    return page_data


def save_data(data):

    df = pd.DataFrame(
        data
    )

    os.makedirs(
        "data/cleaned",
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    return df


def main():

    print("=" * 70)
    print("🚗 GAARAAS — SCRAPING COMPLET")
    print("=" * 70)

    print(
        f"\nPages maximum prévues : "
        f"{TARGET_PAGES}"
    )

    all_data = []

    driver = create_driver()

    try:

        for page in range(
            1,
            TARGET_PAGES + 1
        ):

            page_data = scrape_page(
                driver,
                page
            )

            if not page_data:

                print(
                    f"\n🛑 Plus aucune annonce "
                    f"à la page {page}."
                )

                break

            all_data.extend(
                page_data
            )

            df = save_data(
                all_data
            )

            print(
                f"\n💾 Sauvegarde : "
                f"{len(df)} annonces"
            )

    finally:

        driver.quit()

    # ---------------------------------------------------------
    # Contrôle final
    # ---------------------------------------------------------

    df = pd.DataFrame(
        all_data
    )

    print("\n" + "=" * 70)
    print("🔍 CONTRÔLE FINAL GAARAAS")
    print("=" * 70)

    print(
        f"\nPages réellement collectées : "
        f"{df['page'].nunique() if len(df) else 0}"
    )

    print(
        f"Annonces collectées : "
        f"{len(df)}"
    )

    print(
        f"Colonnes : "
        f"{len(df.columns)}"
    )

    print("\nValeurs manquantes :")

    print(
        df.isna().sum()
    )

    print(
        "\n📄 Fichier : "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()