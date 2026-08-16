import streamlit as st

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Data Collection App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("User Input Features")

    st.divider()

    source = st.selectbox(
        "Data source",
        [
            "Books to Scrape",
            "Gaaraas"
        ]
    )

    st.subheader("Pages")

    if source == "Books to Scrape":
        number_of_pages = st.number_input(
            "Number of pages",
            min_value=1,
            max_value=100,
            value=1,
            step=1
        )

    else:
        number_of_pages = st.number_input(
            "Number of pages",
            min_value=1,
            max_value=100,
            value=1,
            step=1
        )

    st.subheader("Options")

    option = st.selectbox(
        "Choose an action",
        [
            "Scrape data using Selenium",
            "Download scraped data",
            "Dashboard of the data",
            "Evaluate the app"
        ]
    )

    st.divider()

    st.caption("Data Collection — Exam Project")
    st.caption("2026")


# ============================================================
# PAGE D'ACCUEIL
# ============================================================

st.title("MY DATA COLLECTION APP")

st.markdown(
    """
    ### Web scraping, data cleaning and visualization

    Cette application permet de collecter, nettoyer, stocker et
    visualiser des données provenant de différentes sources web.
    """
)

st.divider()


# ============================================================
# INFORMATIONS DU PROJET
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        """
        ### 🕷 Web Scraping

        Collecte des données avec **Selenium** sur plusieurs pages.
        """
    )

with col2:
    st.success(
        """
        ### 🧹 Data Cleaning

        Nettoyage et préparation des données collectées.
        """
    )

with col3:
    st.warning(
        """
        ### 📊 Dashboard

        Analyse et visualisation des données nettoyées.
        """
    )


st.divider()


# ============================================================
# SOURCES
# ============================================================

st.subheader("Data Sources")

col1, col2 = st.columns(2)

with col1:

    st.markdown("### 📚 Books to Scrape")

    st.write(
        "Catalogue de livres utilisé pour la collecte des données."
    )

    if st.button("Books data", use_container_width=True):
        st.session_state["selected_source"] = "Books to Scrape"
        st.success("Source Books to Scrape sélectionnée.")


with col2:

    st.markdown("### 🚗 Gaaraas")

    st.write(
        "Annonces automobiles de Dakar utilisées pour la collecte."
    )

    if st.button("Vehicles data", use_container_width=True):
        st.session_state["selected_source"] = "Gaaraas"
        st.success("Source Gaaraas sélectionnée.")


st.divider()


# ============================================================
# ETAT ACTUEL
# ============================================================

st.subheader("Current selection")

st.write(f"**Source :** {source}")
st.write(f"**Pages :** {number_of_pages}")
st.write(f"**Action :** {option}")


# ============================================================
# MESSAGE
# ============================================================

st.divider()

st.caption(
    "Projet d'examen — Data Collection | "
    "Web scraping, nettoyage et déploiement Streamlit"
)