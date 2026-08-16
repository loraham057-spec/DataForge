from pathlib import Path
import shutil

# ============================================================
# CORRECTION DU MENU "EVALUATE THE APP"
# ============================================================

APP = Path("app/streamlit_app.py")

if not APP.exists():
    raise FileNotFoundError(
        f"""
❌ Fichier introuvable :

{APP.resolve()}

Lance ce script depuis la racine du projet :
C:\\Users\\IT VillageReach\\Documents\\Data_collection_exam
"""
    )

# ------------------------------------------------------------
# Lecture du fichier Streamlit
# ------------------------------------------------------------

code = APP.read_text(encoding="utf-8")

# ------------------------------------------------------------
# Vérification de la fonction evaluation_dashboard()
# ------------------------------------------------------------

if "def evaluation_dashboard(" not in code:
    raise RuntimeError(
        """
❌ La fonction evaluation_dashboard() n'existe pas dans
app/streamlit_app.py.

Il faut d'abord utiliser la version de l'application
qui contient la page d'évaluation.
"""
    )

# ------------------------------------------------------------
# Correction du branchement du menu
# ------------------------------------------------------------

old = """else:
    evaluation()"""

new = """else:
    evaluation_dashboard()"""

# Déjà corrigé
if new in code:

    print("✅ Le menu Evaluate the App est déjà correctement configuré.")

# Ancienne version trouvée
elif old in code:

    # Création d'une sauvegarde
    backup = APP.with_suffix(".py.backup")

    shutil.copy2(APP, backup)

    # Remplacement
    code = code.replace(old, new, 1)

    # Sauvegarde
    APP.write_text(code, encoding="utf-8")

    print("✅ Correction appliquée.")
    print(f"📦 Sauvegarde créée : {backup}")

else:

    raise RuntimeError(
        """
❌ Impossible de trouver le bloc :

else:
    evaluation()

Le fichier semble avoir une structure différente.
"""
    )

# ------------------------------------------------------------
# Vérification de la syntaxe Python
# ------------------------------------------------------------

try:

    compile(
        APP.read_text(encoding="utf-8"),
        str(APP),
        "exec"
    )

    print("✅ Syntaxe Python vérifiée.")

except SyntaxError as error:

    print("❌ Une erreur de syntaxe a été détectée.")
    print()
    print(f"Ligne : {error.lineno}")
    print(f"Erreur : {error.msg}")

    raise

# ------------------------------------------------------------
# Vérification finale
# ------------------------------------------------------------

final_code = APP.read_text(encoding="utf-8")

if "evaluation_dashboard()" in final_code:

    print()
    print("=" * 60)
    print("🎉 CORRECTION TERMINÉE")
    print("=" * 60)
    print()
    print("Le menu 🧪 Evaluate the App appelle maintenant :")
    print()
    print("    evaluation_dashboard()")
    print()
    print("Cette page doit afficher :")
    print()
    print("    📝 KoboToolbox")
    print("    📋 Google Forms")
    print()
    print("Les boutons ouvriront directement les formulaires.")
    print()
    print("=" * 60)

else:

    raise RuntimeError(
        "❌ La correction n'a pas pu être vérifiée."
    )