from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    InvalidSessionIdException
)
import pandas as pd
import re
import time
import os


BASE_URL = "https://www.gaaraas.com/fr/users/dakar-auto?page={}"

TARGET_PAGES = 100

OUTPUT_FILE = "data/cleaned/gaaraas_full.csv"

MAX_RETRIES = 3


# ============================================================
# SELENIUM
# ============================================================

def create_driver():

    options = Options()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    driver = webdriver.Chrome(
        options=options
    )

    driver.set_page_load_timeout(45)

    return driver


def restart_driver(driver):

    print("\n🔄 Redémarrage de Selenium...")

    try:

        driver.quit()

    except Exception:

        pass

    time.sleep(2)

    return create_driver()


# ============================================================
# TEXTE
# ============================================================

def clean_text(text):

    if not text:

        return ""

    return " ".join(
        text.split()
    ).strip()


# ============================================================
# EXTRACTION
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

        return int(
            match.group()
        )

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

    for line in lines:

        if line.lower() == "dakar":

            return "Dakar"

    return ""


# ============================================================
# URLs D'UNE PAGE
# ============================================================

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


# ============================================================
# CHARGEMENT PAGE AVEC RETRY
# ============================================================

def load_page(driver, url):

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            driver.get(url)

            time.sleep(1)

            return True, driver

        except (
            TimeoutException,
            WebDriverException,
            InvalidSessionIdException
        ) as e:

            print(
                f"\n⚠️ Erreur chargement "
                f"(tentative {attempt}/{MAX_RETRIES})"
            )

            print(
                str(e)[:200]
            )

            if attempt < MAX_RETRIES:

                driver = restart_driver(
                    driver
                )

            else:

                return False, driver

    return False, driver


# ============================================================
# EXTRACTION D'UNE ANNONCE
# ============================================================

def scrape_listing(
    driver,
    listing_url,
    page_number,
    position
):

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            success, driver = load_page(
                driver,
                listing_url
            )

            if not success:

                return None, driver

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

            gearbox = clean_text(
                extract_detail_value(
                    body,
                    "BOÎTE DE VITESSES"
                )
            )

            if gearbox.upper() == "N/A":

                gearbox = ""

            price = extract_price(
                body
            )

            region = get_region(
                body
            )

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

            return result, driver

        except (
            TimeoutException,
            WebDriverException,
            InvalidSessionIdException
        ) as e:

            print(
                f"\n⚠️ Erreur annonce "
                f"{position} "
                f"(tentative {attempt}/{MAX_RETRIES})"
            )

            if attempt < MAX_RETRIES:

                driver = restart_driver(
                    driver
                )

            else:

                print(
                    "❌ Annonce abandonnée après "
                    "plusieurs tentatives."
                )

                return None, driver

    return None, driver


# ============================================================
# SAUVEGARDE
# ============================================================

def save_checkpoint(data):

    if not data:

        return

    df = pd.DataFrame(
        data
    )

    os.makedirs(
        "data/cleaned",
        exist_ok=True
    )

    # Suppression des doublons
    df = df.drop_duplicates(
        subset=["listing_url"],
        keep="last"
    )

    # Écriture directe
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"\n💾 Checkpoint sauvegardé : "
        f"{len(df)} annonces"
    )


# ============================================================
# CHARGEMENT CHECKPOINT
# ============================================================

def load_existing_data():

    if not os.path.exists(
        OUTPUT_FILE
    ):

        print(
            "\n🆕 Aucun checkpoint."
        )

        return []

    try:

        df = pd.read_csv(
            OUTPUT_FILE
        )

        print(
            f"\n♻️ Checkpoint trouvé : "
            f"{len(df)} annonces"
        )

        return df.to_dict(
            orient="records"
        )

    except Exception as e:

        print(
            f"\n⚠️ Impossible de lire "
            f"le checkpoint : {e}"
        )

        return []


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("🚗 GAARAAS — SCRAPER AVEC REPRISE AUTOMATIQUE")
    print("=" * 70)

    all_data = load_existing_data()

    existing_urls = {
        row["listing_url"]
        for row in all_data
        if row.get("listing_url")
    }

    print(
        f"URLs déjà collectées : "
        f"{len(existing_urls)}"
    )

    driver = create_driver()

    try:

        # ----------------------------------------------------
        # Pages
        # ----------------------------------------------------

        for page in range(
            1,
            TARGET_PAGES + 1
        ):

            page_url = BASE_URL.format(
                page
            )

            print("\n" + "=" * 70)

            print(
                f"📄 PAGE {page}"
            )

            print("=" * 70)

            success, driver = load_page(
                driver,
                page_url
            )

            if not success:

                print(
                    f"\n❌ Impossible de charger "
                    f"la page {page}."
                )

                print(
                    "Le programme sera relancé "
                    "automatiquement au prochain lancement."
                )

                break

            listing_urls = get_listing_urls(
                driver
            )

            print(
                f"Annonces trouvées : "
                f"{len(listing_urls)}"
            )

            if not listing_urls:

                print(
                    "\n🛑 Plus aucune annonce."
                )

                break

            # ------------------------------------------------
            # Annonces
            # ------------------------------------------------

            for position, listing_url in enumerate(
                listing_urls,
                start=1
            ):

                # --------------------------------------------
                # Déjà collectée ?
                # --------------------------------------------

                if listing_url in existing_urls:

                    print(
                        f"   [{position}/{len(listing_urls)}] "
                        f"⏭️ Déjà collectée"
                    )

                    continue

                print(
                    f"\n   [{position}/{len(listing_urls)}]"
                )

                result, driver = scrape_listing(
                    driver,
                    listing_url,
                    page,
                    position
                )

                if result is None:

                    print(
                        "      ⚠️ "
                        "Annonce non récupérée."
                    )

                    continue

                all_data.append(
                    result
                )

                existing_urls.add(
                    listing_url
                )

                print(
                    f"      ✓ "
                    f"{result['brand']} "
                    f"{result['model']} "
                    f"| {result['year']} "
                    f"| {result['price']} CFA"
                )

                # Sauvegarde toutes les 5 annonces
                if len(all_data) % 5 == 0:

                    save_checkpoint(
                        all_data
                    )

            # ------------------------------------------------
            # Sauvegarde fin de page
            # ------------------------------------------------

            save_checkpoint(
                all_data
            )

            print(
                f"\n📊 Total actuel : "
                f"{len(all_data)} annonces"
            )

    finally:

        try:

            driver.quit()

        except Exception:

            pass

    # ========================================================
    # CONTRÔLE FINAL
    # ========================================================

    if all_data:

        df = pd.DataFrame(
            all_data
        )

        df = df.drop_duplicates(
            subset=["listing_url"],
            keep="last"
        )

        df.to_csv(
            OUTPUT_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        print("\n" + "=" * 70)
        print("🔍 CONTRÔLE")
        print("=" * 70)

        print(
            f"\nAnnonces : {len(df)}"
        )

        print(
            f"Pages : "
            f"{df['page'].nunique()}"
        )

        print(
            f"Dernière page : "
            f"{df['page'].max()}"
        )

        print(
            "\nValeurs manquantes :"
        )

        print(
            df.isna().sum()
        )

        print(
            f"\n📄 {OUTPUT_FILE}"
        )


if __name__ == "__main__":

    main()