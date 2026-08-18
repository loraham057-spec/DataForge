from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, WebDriverException

import pandas as pd
import re
import time
import os
import shutil
import platform


BASE_URL = "https://www.gaaraas.com/fr/users/dakar-auto?page={}"


# ============================================================
# CRÉATION DU DRIVER SELENIUM
# Compatible Windows + Streamlit Cloud/Linux
# ============================================================

def create_driver():

    options = Options()

    # --------------------------------------------------------
    # Mode serveur / Streamlit Cloud
    # --------------------------------------------------------

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")

    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")

    options.add_argument(
        "--window-size=1920,1080"
    )

    # --------------------------------------------------------
    # User-Agent
    # --------------------------------------------------------

    options.add_argument(
        "--user-agent="
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    # ========================================================
    # RECHERCHE DU NAVIGATEUR
    # ========================================================

    browser_candidates = [

        os.environ.get("CHROME_BIN"),

        os.environ.get("CHROMIUM_BIN"),

        "/usr/bin/chromium",

        "/usr/bin/chromium-browser",

        "/usr/bin/google-chrome",

        "/usr/bin/google-chrome-stable",
    ]

    browser_path = next(
        (
            path
            for path in browser_candidates
            if path and os.path.isfile(path)
        ),
        None,
    )

    if browser_path:

        options.binary_location = browser_path

    # ========================================================
    # RECHERCHE DE CHROMEDRIVER
    # ========================================================

    driver_candidates = [

        os.environ.get(
            "CHROMEDRIVER_PATH"
        ),

        shutil.which(
            "chromedriver"
        ),

        "/usr/bin/chromedriver",

        "/usr/lib/chromium/chromedriver",

        "/usr/lib/chromium-browser/chromedriver",
    ]

    driver_path = next(
        (
            path
            for path in driver_candidates
            if path and os.path.isfile(path)
        ),
        None,
    )

    # ========================================================
    # CRÉATION DU NAVIGATEUR
    # ========================================================

    try:

        if driver_path:

            service = Service(
                driver_path
            )

            driver = webdriver.Chrome(
                service=service,
                options=options
            )

        else:

            # Fallback Selenium Manager
            driver = webdriver.Chrome(
                options=options
            )

    except WebDriverException as error:

        system = platform.system()

        raise RuntimeError(
            "Impossible de démarrer "
            "Chromium/ChromeDriver.\n\n"

            f"Système détecté : {system}\n"

            f"Navigateur détecté : "
            f"{browser_path or 'aucun'}\n"

            f"ChromeDriver détecté : "
            f"{driver_path or 'aucun'}\n\n"

            "Pour Streamlit Cloud, vérifiez "
            "que packages.txt contient :\n"

            "chromium\n"
            "chromium-driver\n\n"

            f"Erreur Selenium : {error}"
        ) from error

    # ========================================================
    # TIMEOUTS
    # ========================================================

    driver.set_page_load_timeout(
        60
    )

    driver.implicitly_wait(
        10
    )

    return driver


# ============================================================
# NETTOYAGE DU TEXTE
# ============================================================

def clean_text(text):

    if not text:
        return ""

    return " ".join(
        text.split()
    ).strip()


# ============================================================
# EXTRACTION D'UNE VALEUR DEPUIS LE BODY
# ============================================================

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


# ============================================================
# EXTRACTION DU PRIX
# ============================================================

def extract_price_from_card(card_text):

    match = re.search(
        r"CFA\s*([\d\s]+)",
        card_text,
        re.IGNORECASE
    )

    if match:

        value = (
            match.group(1)
            .replace(" ", "")
            .strip()
        )

        try:

            return int(value)

        except ValueError:

            return None

    return None


# ============================================================
# EXTRACTION DU NOM DU VÉHICULE
# ============================================================

def extract_vehicle_name(body):

    lines = [
        clean_text(line)
        for line in body.split("\n")
        if clean_text(line)
    ]

    # Cas : DétailsCitroen C3
    for line in lines:

        if line.startswith("Détails"):

            name = line.replace(
                "Détails",
                "",
                1
            ).strip()

            if name:

                return name

    # Cas : Détails / Citroen C3
    for i, line in enumerate(lines):

        if line.lower() == "détails":

            if i + 1 < len(lines):

                return lines[i + 1]

    return ""


# ============================================================
# SÉPARATION MARQUE / MODÈLE
# ============================================================

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
        "Rolls Royce",
        "Range Rover"
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

    brand = parts[0]

    model = " ".join(
        parts[1:]
    )

    return brand, model


# ============================================================
# NETTOYAGE DE L'ANNÉE
# ============================================================

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

        return int(
            match.group()
        )

    return None


# ============================================================
# NETTOYAGE DU KILOMÉTRAGE
# ============================================================

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

    if match:

        number = (
            match.group(1)
            .replace(" ", "")
        )

        try:

            return int(number)

        except ValueError:

            return None

    return None


# ============================================================
# RÉGION
# ============================================================

def get_region(body):

    lines = [
        clean_text(line)
        for line in body.split("\n")
        if clean_text(line)
    ]

    for line in lines:

        if line.lower() == "dakar":

            return "Dakar"

    return ""


# ============================================================
# SCRAPING D'UNE PAGE
# ============================================================

def scrape_page(driver, page_number):

    url = BASE_URL.format(
        page_number
    )

    print(
        f"\n📄 PAGE {page_number}"
    )

    driver.get(url)

    time.sleep(1)

    listings = driver.find_elements(
        By.CSS_SELECTOR,
        "a[href*='/vehicle_listings/']"
    )

    print(
        f"   Annonces trouvées : {len(listings)}"
    )

    results = []

    listing_data = []

    # --------------------------------------------------------
    # Sauvegarder les URLs avant navigation
    # --------------------------------------------------------

    for position, listing in enumerate(
        listings,
        start=1
    ):

        href = listing.get_attribute(
            "href"
        )

        card_text = listing.text.strip()

        if not href:

            continue

        listing_data.append(
            {
                "position": position,
                "url": href,
                "card_text": card_text
            }
        )

    # --------------------------------------------------------
    # Visite des fiches
    # --------------------------------------------------------

    for item in listing_data:

        position = item["position"]

        listing_url = item["url"]

        card_text = item["card_text"]

        print(
            f"\n   [{position}/{len(listing_data)}]"
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

            # ------------------------------------------------
            # Nom véhicule
            # ------------------------------------------------

            vehicle_name = extract_vehicle_name(
                body
            )

            if not vehicle_name:

                card_lines = [
                    clean_text(line)
                    for line in card_text.split("\n")
                    if clean_text(line)
                ]

                vehicle_name = ""

                for line in card_lines:

                    if (
                        line.lower()
                        not in [
                            "vendu",
                            "dakar"
                        ]
                    ):

                        vehicle_name = line

                        break

            brand, model = split_brand_model(
                vehicle_name
            )

            # ------------------------------------------------
            # Année
            # ------------------------------------------------

            year_raw = extract_detail_value(
                body,
                "ANNÉE"
            )

            year = clean_year(
                year_raw
            )

            # ------------------------------------------------
            # Kilométrage
            # ------------------------------------------------

            mileage_raw = extract_detail_value(
                body,
                "KILOMÉTRAGE"
            )

            mileage = clean_mileage(
                mileage_raw
            )

            # ------------------------------------------------
            # Boîte
            # ------------------------------------------------

            gearbox = extract_detail_value(
                body,
                "BOÎTE DE VITESSES"
            )

            gearbox = clean_text(
                gearbox
            )

            if gearbox.upper() == "N/A":

                gearbox = ""

            # ------------------------------------------------
            # Prix
            # ------------------------------------------------

            price = extract_price_from_card(
                card_text
            )

            # ------------------------------------------------
            # Région
            # ------------------------------------------------

            region = get_region(
                body
            )

            # ------------------------------------------------
            # Résultat
            # ------------------------------------------------

            result = {

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

            results.append(
                result
            )

            print(
                f"      ✓ {brand} {model}"
            )

            print(
                f"        Année       : {year}"
            )

            print(
                f"        Prix        : {price}"
            )

            print(
                f"        Kilométrage : {mileage}"
            )

            print(
                f"        Boîte       : {gearbox}"
            )

            print(
                f"        Région      : {region}"
            )

        except Exception as e:

            print(
                f"      ❌ Erreur : {e}"
            )

    return results


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    print("=" * 70)

    print(
        "🚗 GAARAAS — TEST COMPLET PAGE 1"
    )

    print("=" * 70)

    driver = create_driver()

    data = []

    try:

        data = scrape_page(
            driver,
            1
        )

    finally:

        driver.quit()

    # --------------------------------------------------------
    # DataFrame
    # --------------------------------------------------------

    columns = [
        "page",
        "position_page",
        "brand",
        "model",
        "year",
        "price",
        "mileage",
        "gearbox",
        "region",
        "listing_url"
    ]

    df = pd.DataFrame(
        data,
        columns=columns
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "🔍 CONTRÔLE PAGE 1"
    )

    print(
        "=" * 70
    )

    print(
        f"\nNombre d'annonces : {len(df)}"
    )

    print(
        f"Nombre de colonnes : {len(df.columns)}"
    )

    print(
        "\nDonnées :"
    )

    print(
        df.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Contrôles
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "🧪 CONTRÔLES"
    )

    print(
        "=" * 70
    )

    print(
        f"\nMarques manquantes : "
        f"{df['brand'].eq('').sum()}"
    )

    print(
        f"Modèles manquants : "
        f"{df['model'].eq('').sum()}"
    )

    print(
        f"Années manquantes : "
        f"{df['year'].isna().sum()}"
    )

    print(
        f"Prix manquants : "
        f"{df['price'].isna().sum()}"
    )

    print(
        f"Kilométrages manquants : "
        f"{df['mileage'].isna().sum()}"
    )

    print(
        f"Boîtes manquantes : "
        f"{df['gearbox'].eq('').sum()}"
    )

    print(
        f"Régions manquantes : "
        f"{df['region'].eq('').sum()}"
    )

    # --------------------------------------------------------
    # Sauvegarde
    # --------------------------------------------------------

    os.makedirs(
        "data/cleaned",
        exist_ok=True
    )

    output = (
        "data/cleaned/"
        "gaaraas_page1_test.csv"
    )

    df.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"\n📄 Fichier créé : {output}"
    )


if __name__ == "__main__":

    main()