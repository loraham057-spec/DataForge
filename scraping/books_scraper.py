from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException
)

import pandas as pd
import os
import time


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

START_PAGE = 1
END_PAGE = 50

OUTPUT_DIR = "data/cleaned"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "books_full.csv"
)

WAIT_TIME = 10


# ============================================================
# NAVIGATEUR
# ============================================================

def create_driver():
    """
    Crée un navigateur Selenium compatible Windows et
    Streamlit Community Cloud/Linux.

    Sur Linux/Cloud, on privilégie Chromium + ChromeDriver
    installés par le système (packages.txt).
    Sur Windows, Selenium Manager reste le fallback.
    """

    import os
    import shutil
    import platform

    options = Options()

    # -------------------------------------------------
    # Mode serveur / Cloud
    # -------------------------------------------------
    # Headless fonctionne aussi sur Windows.
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--window-size=1920,1080")

    # -------------------------------------------------
    # User-Agent
    # -------------------------------------------------
    options.add_argument(
        "--user-agent="
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    # -------------------------------------------------
    # Recherche du navigateur
    # -------------------------------------------------
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
            path for path in browser_candidates
            if path and os.path.isfile(path)
        ),
        None,
    )

    # Sur Windows, Selenium Manager peut trouver Chrome
    # automatiquement : inutile de forcer un chemin Linux.
    if browser_path:
        options.binary_location = browser_path

    # -------------------------------------------------
    # Recherche de ChromeDriver
    # -------------------------------------------------
    driver_candidates = [
        os.environ.get("CHROMEDRIVER_PATH"),
        shutil.which("chromedriver"),
        "/usr/bin/chromedriver",
        "/usr/lib/chromium/chromedriver",
        "/usr/lib/chromium-browser/chromedriver",
    ]

    driver_path = next(
        (
            path for path in driver_candidates
            if path and os.path.isfile(path)
        ),
        None,
    )

    # -------------------------------------------------
    # Création du WebDriver
    # -------------------------------------------------
    try:
        if driver_path:
            service = Service(driver_path)
            driver = webdriver.Chrome(
                service=service,
                options=options,
            )
        else:
            # Fallback : Selenium Manager.
            # Utile notamment sur Windows.
            driver = webdriver.Chrome(
                options=options
            )

    except WebDriverException as error:
        system = platform.system()

        raise RuntimeError(
            "Impossible de démarrer Chromium/ChromeDriver.\n"
            f"Système détecté : {system}\n"
            f"Navigateur détecté : {browser_path or 'aucun'}\n"
            f"ChromeDriver détecté : {driver_path or 'aucun'}\n\n"
            "Sur Streamlit Cloud, vérifiez que packages.txt contient :\n"
            "chromium\n"
            "chromium-driver\n\n"
            f"Erreur Selenium : {error}"
        ) from error

    driver.set_page_load_timeout(60)
    driver.implicitly_wait(10)

    return driver


# ============================================================
# ATTENTE DU CHARGEMENT
# ============================================================

def wait_for_books(driver):
    """Attendre que les livres du catalogue soient chargés."""

    try:

        WebDriverWait(
            driver,
            WAIT_TIME
        ).until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    "article.product_pod"
                )
            )
        )

        return True

    except TimeoutException:

        return False


# ============================================================
# FONCTIONS DE LECTURE SÉCURISÉE
# ============================================================

def safe_text(element, selector):
    """
    Récupérer le texte d'un élément.
    Retourne une chaîne vide si l'élément n'existe plus.
    """

    try:

        return element.find_element(
            By.CSS_SELECTOR,
            selector
        ).text.strip()

    except (
        NoSuchElementException,
        StaleElementReferenceException
    ):

        return ""


def safe_attribute(
    element,
    selector,
    attribute
):
    """
    Récupérer un attribut HTML.
    """

    try:

        value = element.find_element(
            By.CSS_SELECTOR,
            selector
        ).get_attribute(attribute)

        return value.strip() if value else ""

    except (
        NoSuchElementException,
        StaleElementReferenceException
    ):

        return ""


def get_rating(element):
    """Récupérer la note du livre."""

    try:

        classes = element.find_element(
            By.CSS_SELECTOR,
            "p.star-rating"
        ).get_attribute("class")

        if not classes:
            return ""

        return classes.replace(
            "star-rating",
            ""
        ).strip()

    except (
        NoSuchElementException,
        StaleElementReferenceException
    ):

        return ""


# ============================================================
# CATALOGUE
# ============================================================

def collect_books_from_catalogue(
    driver,
    page_number
):
    """
    Récupérer les informations disponibles
    sur la page catalogue.

    Important :
    toutes les informations et les URLs sont
    récupérées avant de visiter les fiches détaillées.
    """

    url = BASE_URL.format(
        page_number
    )

    print()
    print("=" * 65)
    print(f"📄 PAGE {page_number}")
    print("=" * 65)

    print(
        f"🌐 {url}"
    )

    # --------------------------------------------------------
    # Ouvrir la page
    # --------------------------------------------------------

    try:

        driver.get(url)

    except WebDriverException as error:

        print(
            f"❌ Impossible d'ouvrir la page : {error}"
        )

        return []

    # --------------------------------------------------------
    # Attendre les livres
    # --------------------------------------------------------

    if not wait_for_books(driver):

        print(
            "❌ Aucun livre détecté sur cette page."
        )

        return []

    # --------------------------------------------------------
    # Récupérer les livres
    # --------------------------------------------------------

    books = driver.find_elements(
        By.CSS_SELECTOR,
        "article.product_pod"
    )

    products_count = len(
        books
    )

    print(
        f"📚 Livres trouvés : {products_count}"
    )

    catalogue_data = []

    # --------------------------------------------------------
    # Parcourir les livres
    # --------------------------------------------------------

    for index in range(
        products_count
    ):

        try:

            book = books[index]

            # ----------------------------------------------
            # Titre
            # ----------------------------------------------

            title = safe_attribute(
                book,
                "h3 a",
                "title"
            )

            if not title:

                title = safe_text(
                    book,
                    "h3 a"
                )

            # ----------------------------------------------
            # Prix
            # ----------------------------------------------

            price = safe_text(
                book,
                "p.price_color"
            )

            # ----------------------------------------------
            # Disponibilité
            # ----------------------------------------------

            availability = safe_text(
                book,
                "p.instock.availability"
            )

            # ----------------------------------------------
            # Note
            # ----------------------------------------------

            rating = get_rating(
                book
            )

            # ----------------------------------------------
            # URL
            # ----------------------------------------------

            book_url = safe_attribute(
                book,
                "h3 a",
                "href"
            )

            # ----------------------------------------------
            # Enregistrement
            # ----------------------------------------------

            catalogue_data.append(
                {
                    "page": page_number,
                    "position_page": index + 1,
                    "title": title,
                    "price": price,
                    "availability": availability,
                    "rating": rating,
                    "products_count": products_count,
                    "book_url": book_url
                }
            )

            # Affichage
            print(
                f"   ✓ {index + 1:02d}/{products_count} "
                f"- {title[:45]}"
            )

        except StaleElementReferenceException:

            print(
                f"   ⚠️ Livre {index + 1} devenu obsolète."
            )

            # ------------------------------------------------
            # Nouvelle récupération de la liste
            # ------------------------------------------------

            try:

                books = driver.find_elements(
                    By.CSS_SELECTOR,
                    "article.product_pod"
                )

                book = books[index]

                title = safe_attribute(
                    book,
                    "h3 a",
                    "title"
                )

                if not title:

                    title = safe_text(
                        book,
                        "h3 a"
                    )

                price = safe_text(
                    book,
                    "p.price_color"
                )

                availability = safe_text(
                    book,
                    "p.instock.availability"
                )

                rating = get_rating(
                    book
                )

                book_url = safe_attribute(
                    book,
                    "h3 a",
                    "href"
                )

                catalogue_data.append(
                    {
                        "page": page_number,
                        "position_page": index + 1,
                        "title": title,
                        "price": price,
                        "availability": availability,
                        "rating": rating,
                        "products_count": products_count,
                        "book_url": book_url
                    }
                )

                print(
                    f"   ✓ {index + 1:02d}/{products_count} "
                    f"- {title[:45]}"
                )

            except Exception as error:

                print(
                    f"   ❌ Impossible de récupérer "
                    f"le livre {index + 1}: {error}"
                )

    return catalogue_data


# ============================================================
# FICHE DÉTAILLÉE
# ============================================================

def scrape_book_details(
    driver,
    book_url
):
    """
    Récupérer les informations supplémentaires
    d'une fiche détaillée.
    """

    details = {
        "description": "",
        "category": "",
        "tax": "",
        "reviews": ""
    }

    if not book_url:

        return details

    try:

        driver.get(
            book_url
        )

        # ----------------------------------------------------
        # Attendre le tableau produit
        # ----------------------------------------------------

        try:

            WebDriverWait(
                driver,
                WAIT_TIME
            ).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "table.table-striped"
                    )
                )
            )

        except TimeoutException:

            pass

        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        try:

            details["description"] = driver.find_element(
                By.CSS_SELECTOR,
                "#product_description + p"
            ).text.strip()

        except NoSuchElementException:

            details["description"] = ""

        # ----------------------------------------------------
        # CATÉGORIE
        # ----------------------------------------------------

        try:

            breadcrumbs = driver.find_elements(
                By.CSS_SELECTOR,
                "ul.breadcrumb li"
            )

            if len(breadcrumbs) >= 3:

                details["category"] = (
                    breadcrumbs[2]
                    .text
                    .strip()
                )

        except (
            NoSuchElementException,
            StaleElementReferenceException
        ):

            details["category"] = ""

        # ----------------------------------------------------
        # PRODUCT INFORMATION
        # ----------------------------------------------------

        try:

            rows = driver.find_elements(
                By.CSS_SELECTOR,
                "table.table-striped tr"
            )

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

                except (
                    NoSuchElementException,
                    StaleElementReferenceException
                ):

                    continue

                # --------------------------------------------
                # Taxe
                # --------------------------------------------

                if field == "Tax":

                    details["tax"] = value

                # --------------------------------------------
                # Nombre d'avis
                # --------------------------------------------

                elif field == "Number of reviews":

                    details["reviews"] = value

        except Exception as error:

            print(
                f"      ⚠️ Product Information : {error}"
            )

    except WebDriverException as error:

        print(
            f"      ❌ Erreur fiche : {error}"
        )

    return details


# ============================================================
# SCRAPING D'UNE PAGE
# ============================================================

def scrape_books_page(
    driver,
    page_number
):
    """
    Scraper complètement une page.
    """

    # --------------------------------------------------------
    # Étape 1 :
    # récupérer les livres du catalogue
    # --------------------------------------------------------

    catalogue_data = (
        collect_books_from_catalogue(
            driver,
            page_number
        )
    )

    if not catalogue_data:

        return []

    results = []

    total = len(
        catalogue_data
    )

    # --------------------------------------------------------
    # Étape 2 :
    # visiter les fiches
    # --------------------------------------------------------

    print()
    print(
        f"🔎 Extraction des fiches : {total}"
    )

    for index, book in enumerate(
        catalogue_data,
        start=1
    ):

        print(
            f"      → Fiche "
            f"{index}/{total}"
        )

        # ----------------------------------------------------
        # Récupérer les détails
        # ----------------------------------------------------

        details = scrape_book_details(
            driver,
            book["book_url"]
        )

        # ----------------------------------------------------
        # Construire la ligne finale
        # ----------------------------------------------------

        row = {
            "page": book["page"],
            "position_page": book["position_page"],
            "title": book["title"],
            "price": book["price"],
            "availability": book["availability"],
            "rating": book["rating"],
            "reviews": details["reviews"],
            "description": details["description"],
            "category": details["category"],
            "tax": details["tax"],
            "book_url": book["book_url"]
        }

        results.append(
            row
        )

    return results


# ============================================================
# SAUVEGARDE
# ============================================================

def save_data(
    data,
    filename=OUTPUT_FILE
):
    """Sauvegarder les données dans un fichier CSV."""

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # Accepte une liste de dictionnaires ou un DataFrame.
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.DataFrame(data)

    if df.empty:
        return df

    df.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )

    return df


# ============================================================
# SCRAPING COMPLET
# ============================================================

def scrape_all_books(
    start_page=START_PAGE,
    end_page=END_PAGE
):
    """
    Scraper toutes les pages demandées.
    """

    start_time = time.time()

    driver = create_driver()

    all_results = []

    pages_completed = []

    try:

        print()
        print("=" * 70)
        print("📚 BOOKS TO SCRAPE")
        print("=" * 70)

        print(
            f"Pages à scraper : "
            f"{start_page} → {end_page}"
        )

        total_pages = (
            end_page - start_page + 1
        )

        # ====================================================
        # BOUCLE DES PAGES
        # ====================================================

        for page in range(
            start_page,
            end_page + 1
        ):

            page_number = (
                page - start_page + 1
            )

            print()
            print(
                f"📊 Progression : "
                f"{page_number}/{total_pages}"
            )

            try:

                page_data = scrape_books_page(
                    driver,
                    page
                )

                # --------------------------------------------
                # Vérifier les données
                # --------------------------------------------

                if page_data:

                    all_results.extend(
                        page_data
                    )

                    pages_completed.append(
                        page
                    )

                    # ----------------------------------------
                    # Sauvegarde progressive
                    # ----------------------------------------

                    save_data(
                        all_results
                    )

                    print()
                    print(
                        f"   ✅ PAGE {page} TERMINÉE"
                    )

                    print(
                        f"   📚 Livres page : "
                        f"{len(page_data)}"
                    )

                    print(
                        f"   📊 Total actuel : "
                        f"{len(all_results)}"
                    )

                else:

                    print(
                        f"   ⚠️ PAGE {page} "
                        f"ne contient aucune donnée."
                    )

            except Exception as error:

                print()
                print(
                    f"   ❌ ERREUR PAGE {page}"
                )

                print(
                    f"   {error}"
                )

                # --------------------------------------------
                # Ne pas arrêter tout le scraping
                # --------------------------------------------

                continue

        # ====================================================
        # DATAFRAME FINAL
        # ====================================================

        columns = [
            "page",
            "position_page",
            "title",
            "price",
            "availability",
            "rating",
            "reviews",
            "description",
            "category",
            "tax",
            "book_url",
        ]

        df = pd.DataFrame(
            all_results,
            columns=columns,
        )

        duration = (
            time.time() - start_time
        )

        return (
            df,
            duration,
            pages_completed
        )

    finally:

        driver.quit()

        print()
        print(
            "🌐 Navigateur fermé."
        )


# ============================================================
# RAPPORT FINAL
# ============================================================

def print_final_report(
    df,
    duration,
    pages_completed,
    start_page,
    end_page
):
    """Afficher le rapport final."""

    expected_pages = (
        end_page - start_page + 1
    )

    expected_books = (
        expected_pages * 20
    )

    print()
    print("=" * 70)
    print("🏁 SCRAPING TERMINÉ")
    print("=" * 70)

    # --------------------------------------------------------
    # Livres
    # --------------------------------------------------------

    print()
    print(
        f"📚 Livres récupérés : {len(df)}"
    )

    print(
        f"🎯 Livres attendus : {expected_books}"
    )

    # --------------------------------------------------------
    # Pages
    # --------------------------------------------------------

    print(
        f"📄 Pages réussies : "
        f"{len(pages_completed)}/{expected_pages}"
    )

    # --------------------------------------------------------
    # Durée
    # --------------------------------------------------------

    print(
        f"⏱️ Durée : "
        f"{duration / 60:.2f} minutes"
    )

    # --------------------------------------------------------
    # Contrôle
    # --------------------------------------------------------

    if len(df) == expected_books:

        print()
        print("✅ CONTRÔLE OK")
        print(
            f"Tous les {expected_books} livres attendus "
            "ont été récupérés."
        )

    else:

        missing = max(
            expected_books - len(df),
            0
        )

        print()
        print(
            f"⚠️ ATTENTION : "
            f"{missing} livre(s) potentiellement manquant(s)."
        )

    # --------------------------------------------------------
    # Pages manquantes
    # --------------------------------------------------------

    missing_pages = [
        page
        for page in range(
            start_page,
            end_page + 1
        )
        if page not in pages_completed
    ]

    if missing_pages:

        print()
        print(
            "⚠️ Pages non récupérées :"
        )

        print(
            missing_pages
        )

    # --------------------------------------------------------
    # Colonnes
    # --------------------------------------------------------

    print()
    print(
        "📋 Colonnes :"
    )

    for column in df.columns:

        print(
            f"   - {column}"
        )


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    print()
    print(
        "🚀 Démarrage du scraping..."
    )

    df, duration, pages_completed = (
        scrape_all_books(
            start_page=START_PAGE,
            end_page=END_PAGE
        )
    )

    # --------------------------------------------------------
    # Sauvegarde finale
    # --------------------------------------------------------

    save_data(
        df.to_dict(
            orient="records"
        )
    )

    # --------------------------------------------------------
    # Rapport
    # --------------------------------------------------------

    print_final_report(
        df,
        duration,
        pages_completed,
        START_PAGE,
        END_PAGE
    )

    # --------------------------------------------------------
    # Aperçu
    # --------------------------------------------------------

    if not df.empty:

        print()
        print(
            "🔍 APERÇU DES DONNÉES"
        )

        print(
            df.head().to_string(
                index=False
            )
        )

    print()
    print(
        f"💾 Fichier final : "
        f"{OUTPUT_FILE}"
    )


# ============================================================
# EXÉCUTION
# ============================================================

if __name__ == "__main__":

    main()