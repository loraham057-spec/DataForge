from pathlib import Path
import shutil
import py_compile

APP = Path("app/streamlit_app.py")

if not APP.exists():
    raise SystemExit(f"Fichier introuvable : {APP}")

backup = APP.with_suffix(".py.before_v16.bak")
shutil.copy2(APP, backup)

code = APP.read_text(encoding="utf-8")

# 1. Branding
code = code.replace("📊 DATA COLLECTION</div>", "📊 DATAFORGE</div>")
code = code.replace("📊 DATA COLLECTION TP</div>", "📊 DATAFORGE</div>")
code = code.replace("MY DATA COLLECTION APP</h1>", "MY DATA COLLECTION APP DATAFORGE</h1>")

# 2. Libellé du paramètre de pages
code = code.replace(
    'pages=st.sidebar.number_input(L["pages"],1,100,50 if source.startswith(\'📚\') else 13)',
    'pages=st.sidebar.number_input("🔢 Nombre de pages à traiter",1,100,50 if source.startswith("📚") else 13,step=1,help="Configuration du scraping Selenium.")'
)

# 3. Amélioration visuelle des KPI.
if "DATAFORGE_V16_KPI" not in code:
    marker = "# DATAFORGE_V16_KPI"
    css = (
        marker + "\n"
        "st.markdown('"
        "<style>"
        "[data-testid=\\\"stMetric\\\"]{min-height:128px!important;overflow:hidden!important;}"
        "[data-testid=\\\"stMetricValue\\\"]{font-size:clamp(1.45rem,2.5vw,2.45rem)!important;line-height:1.05!important;white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important;}"
        ".df-dashboard-note{padding:10px 14px;border-radius:12px;margin:6px 0 18px;background:rgba(127,127,127,.08);border:1px solid rgba(127,127,127,.16);}"
        "</style>',unsafe_allow_html=True)\n\n"
    )
    pos = code.find("# FILE UTILS:")
    if pos == -1:
        pos = code.find("def latest(files):")
    code = code[:pos] + css + code[pos:]

# 4. Aide discrète au-dessus des tableaux.
if "df-dashboard-note" not in code:
    target = "st.write('Filtrez les pages et explorez les indicateurs.')"
    replacement = (
        "st.markdown("
        "'<div class=\\\"df-dashboard-note\\\">💡 Utilisez <b>Filtres avancés</b> "
        "pour sélectionner plusieurs pages et analyser uniquement les données souhaitées.</div>', "
        "unsafe_allow_html=True)"
    )
    code = code.replace(target, replacement)

APP.write_text(code, encoding="utf-8")
py_compile.compile(str(APP), doraise=True)

print("✅ DATAFORGE V16 appliquée.")
print(f"📄 {APP}")
print(f"💾 Sauvegarde : {backup}")
print("✅ Branding DATAFORGE")
print("✅ Libellé des pages amélioré")
print("✅ KPI mieux dimensionnés")
print("✅ Filtre multi-pages existant conservé")
print("✅ Syntaxe Python validée")
