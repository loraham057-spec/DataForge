from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
import os


INPUT_FILE = "data/cleaned/books_full.csv"
OUTPUT_FILE = "data/cleaned/books_full_completed.csv"
BACKUP_FILE = "data/cleaned/books_full_completed_backup.csv"


def create_driver():

    options = Options()
    options.add_argument("--start-maximized")

    return webdriver.Chrome(options=options)


def get_product_information(driver):

    tax = ""
    reviews = ""

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

        except NoSuchElementException:
            continue

        if field == "Tax":
            tax = value

        elif field == "Number of reviews":
            reviews = value

    return tax, reviews


def main():

    print("=" * 70)
    print("📚 COMPLÉTION TAX + REVIEWS")
    print("=" * 70)

    # ---------------------------------------------------------
    # Lecture du fichier original
    # ---------------------------------------------------------

    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    print(f"\n📂 Lignes chargées : {len(df)}")

    # ---------------------------------------------------------
    # Vérification
    # ---------------------------------------------------------

    if "book_url" not in df.columns:
        raise ValueError(
            "La colonne book_url est absente."
        )

    # ---------------------------------------------------------
    # Création explicite des colonnes
    # ---------------------------------------------------------

    if "tax" not in df.columns:
        df["tax"] = ""

    if "reviews" not in df.columns:
        df["reviews"] = ""

    # Forcer en texte
    df["tax"] = df["tax"].fillna("").astype(str)
    df["reviews"] = df["reviews"].fillna("").astype(str)

    # ---------------------------------------------------------
    # Initialisation Selenium
    # ---------------------------------------------------------

    driver = create_driver()

    total = len(df)

    success = 0
    errors = 0

    try:

        for position in range(total):

            row = df.iloc[position]

            title = row["title"]
            url = row["book_url"]

            print(
                f"\n[{position + 1}/{total}] {title}"
            )

            try:

                driver.get(url)

                time.sleep(0.25)

                tax, reviews = get_product_information(
                    driver
                )

                # ---------------------------------------------
                # Écriture directe dans le DataFrame
                # ---------------------------------------------

                df.loc[position, "tax"] = tax
                df.loc[position, "reviews"] = reviews

                success += 1

                print(
                    f"   ✓ Tax     : {tax}"
                )

                print(
                    f"   ✓ Reviews : {reviews}"
                )

            except Exception as e:

                errors += 1

                print(
                    f"   ❌ Erreur : {e}"
                )

            # -------------------------------------------------
            # Sauvegarde intermédiaire toutes les 50 lignes
            # -------------------------------------------------

            if (position + 1) % 50 == 0:

                df.to_csv(
                    BACKUP_FILE,
                    index=False,
                    encoding="utf-8-sig"
                )

                print(
                    f"\n💾 Sauvegarde intermédiaire : "
                    f"{position + 1}/{total}"
                )

    finally:

        driver.quit()

    # ---------------------------------------------------------
    # Sauvegarde finale
    # ---------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # ---------------------------------------------------------
    # Contrôle final
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("🔍 CONTRÔLE FINAL")
    print("=" * 70)

    tax_missing = (
        df["tax"]
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    reviews_missing = (
        df["reviews"]
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    print(
        f"\nNombre de lignes : {len(df)}"
    )

    print(
        f"Nombre de colonnes : {len(df.columns)}"
    )

    print(
        f"✓ Succès Selenium : {success}"
    )

    print(
        f"❌ Erreurs Selenium : {errors}"
    )

    print(
        f"Tax manquantes : {tax_missing}"
    )

    print(
        f"Reviews manquantes : {reviews_missing}"
    )

    print(
        f"\n📄 Fichier final : {OUTPUT_FILE}"
    )

    # ---------------------------------------------------------
    # Aperçu
    # ---------------------------------------------------------

    print("\nAperçu des données :")

    print(
        df[
            [
                "page",
                "position_page",
                "title",
                "price",
                "tax",
                "reviews"
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()