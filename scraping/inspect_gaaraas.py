from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


URL = "https://www.gaaraas.com/fr/users/dakar-auto?page=1"


def create_driver():

    options = Options()
    options.add_argument("--start-maximized")

    return webdriver.Chrome(options=options)


def main():

    print("=" * 70)
    print("🚗 DIAGNOSTIC GAARAAS — PAGE 1")
    print("=" * 70)

    driver = create_driver()

    try:

        driver.get(URL)

        time.sleep(2)

        print("\nTitre de la page :")
        print(driver.title)

        print("\nURL actuelle :")
        print(driver.current_url)

        # -----------------------------------------------------
        # Tous les liens contenant une annonce
        # -----------------------------------------------------

        links = driver.find_elements(
            By.TAG_NAME,
            "a"
        )

        print(
            f"\nNombre total de liens trouvés : {len(links)}"
        )

        print("\n" + "=" * 70)
        print("LIENS AVEC CONTENU")
        print("=" * 70)

        counter = 0

        for link in links:

            text = link.text.strip()

            href = link.get_attribute("href")

            if text and href:

                counter += 1

                print("\n" + "-" * 60)

                print(
                    f"#{counter}"
                )

                print(
                    f"TEXT : {text[:500]}"
                )

                print(
                    f"HREF : {href}"
                )

                # On limite l'affichage
                if counter >= 40:
                    break

        # -----------------------------------------------------
        # Informations sur les éléments contenant "CFA"
        # -----------------------------------------------------

        print("\n" + "=" * 70)
        print("ÉLÉMENTS CONTENANT CFA")
        print("=" * 70)

        elements = driver.find_elements(
            By.XPATH,
            "//*[contains(text(), 'CFA')]"
        )

        print(
            f"Nombre trouvé : {len(elements)}"
        )

        for i, element in enumerate(
            elements[:20],
            start=1
        ):

            try:

                print(
                    f"\n[{i}]"
                )

                print(
                    element.text[:500]
                )

                print(
                    "TAG :",
                    element.tag_name
                )

                print(
                    "CLASS :",
                    element.get_attribute("class")
                )

            except Exception:
                pass

    finally:

        driver.quit()

        print("\nNavigateur fermé.")


if __name__ == "__main__":
    main()