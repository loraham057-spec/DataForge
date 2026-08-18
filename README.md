# 🚀 DataForge

> **Data collection, web scraping, data cleaning & visualization platform**

DataForge est une application web dédiée à la **collecte, l'extraction, le nettoyage, la structuration et la visualisation des données**.

L'objectif de DataForge est de proposer dans une même plateforme un environnement simple permettant de transformer des données brutes en données exploitables et visualisables.

---

## 🎯 Objectif du projet

DataForge a été conçu pour faciliter le processus de collecte et d'exploitation des données :

```text
🌐 Source Web
      ↓
🕷️ Scraping / Collecte
      ↓
📥 Extraction des données
      ↓
🧹 Nettoyage & préparation
      ↓
🗄️ Stockage
      ↓
📊 Analyse & visualisation
      ↓
📤 Export des résultats
```

L'application vise notamment les utilisateurs travaillant avec des données issues du Web et souhaitant disposer d'un outil centralisé pour les collecter, les préparer et les analyser.

---

## ✨ Fonctionnalités

### 🕷️ Web Scraping

- Extraction de données depuis des pages Web
- Collecte structurée des informations
- Gestion des données extraites
- Possibilité de travailler avec différentes sources Web
- Préparation des données pour l'analyse

### 📥 Collecte et téléchargement

- Importation de données
- Gestion des fichiers de données
- Téléchargement des résultats
- Export des données dans des formats exploitables

### 🧹 Data Cleaning

DataForge intègre des fonctionnalités permettant de préparer les données avant leur analyse :

- détection des données manquantes ;
- vérification de la qualité des données ;
- nettoyage des valeurs ;
- contrôle de l'intégrité ;
- préparation des données pour la visualisation.

### 🗄️ Gestion des données

L'application dispose de composants dédiés à la gestion et au stockage des données.

Les données peuvent être préparées avant leur utilisation dans les différents modules de l'application.

### 📊 Dashboard & Visualisation

DataForge permet de présenter les données sous forme de tableaux et de visualisations afin de faciliter leur compréhension et leur analyse.

### 🔎 Recherche et filtrage

Les interfaces de DataForge peuvent proposer différents mécanismes de recherche, filtrage et exploration des données.

### 📝 Évaluation de la qualité

Des modules de contrôle et d'évaluation peuvent être utilisés pour vérifier la qualité et l'intégrité des données collectées.

---

## 🖥️ Technologies utilisées

DataForge est développé principalement avec :

- **Python**
- **Streamlit**
- **Pandas**
- **Web Scraping**
- **SQL / Database**
- **HTML / CSS**
- **Git**
- **GitHub**

Les dépendances Python sont centralisées dans :

```text
requirements.txt
```

---

## 📁 Structure du projet

La structure actuelle du projet est organisée autour de plusieurs modules :

```text
DataForge/
│
├── app.py
│
├── app/
│   └── Application modules
│
├── scraping/
│   └── Web scraping & data collection
│
├── cleaning/
│   └── Data cleaning & preprocessing
│
├── dashboard/
│   └── Data visualization & dashboards
│
├── database/
│   └── Database components
│
├── data/
│   └── Data files
│
├── data_database.py
│
├── check_data_integrity.py
├── check_database.py
├── fix_evaluation_buttons.py
├── upgrade_dataforge_v16.py
│
├── improve.md
├── requirements.txt
│
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### 1. Cloner le projet

```bash
git clone https://github.com/loraham057-spec/DataForge.git
```

Entrer dans le projet :

```bash
cd DataForge
```

---

### 2. Créer un environnement virtuel

#### Windows

```powershell
python -m venv venv
```

Activer l'environnement :

```powershell
.\venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python3 -m venv venv
```

Activer :

```bash
source venv/bin/activate
```

---

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## ▶️ Lancer DataForge

Une fois les dépendances installées :

```bash
streamlit run app.py
```

L'application sera normalement accessible à l'adresse :

```text
http://localhost:8501
```

---

## 🧪 Vérification de l'environnement

Avant de lancer l'application, il est recommandé de vérifier l'environnement Python :

```bash
python --version
```

Puis :

```bash
pip --version
```

Et enfin :

```bash
pip list
```

---

## 🔍 Vérification des données

DataForge contient également des scripts destinés au contrôle des données et de la base de données.

Exemples :

```bash
python check_data_integrity.py
```

et :

```bash
python check_database.py
```

---

## 🔄 Workflow recommandé

Le workflow général d'utilisation de DataForge est :

```text
1. Sélectionner une source
        ↓
2. Collecter les données
        ↓
3. Vérifier les données
        ↓
4. Nettoyer les données
        ↓
5. Stocker les données
        ↓
6. Analyser les données
        ↓
7. Visualiser les résultats
        ↓
8. Exporter les données
```

---

## 🛡️ Gestion des fichiers sensibles

Les fichiers contenant des informations sensibles ou spécifiques à l'environnement local ne doivent pas être publiés dans le dépôt Git.

Les variables d'environnement doivent être stockées dans un fichier :

```text
.env
```

et ne doivent pas être poussées vers GitHub.

---

## 🌱 Développement

Pour créer une nouvelle fonctionnalité :

```bash
git checkout -b feature/nom-de-la-fonctionnalite
```

Après les modifications :

```bash
git status
```

Puis :

```bash
git add .
```

Créer le commit :

```bash
git commit -m "Add new feature"
```

Enfin :

```bash
git push origin feature/nom-de-la-fonctionnalite
```

---

## 📌 Version actuelle

**DataForge v1.0**

Le projet est actuellement en phase de développement et d'amélioration continue.

---

## 🗺️ Roadmap

Les prochaines évolutions peuvent notamment inclure :

- [ ] amélioration de l'interface utilisateur ;
- [ ] système avancé de gestion des projets de scraping ;
- [ ] gestion améliorée des sources Web ;
- [ ] planification automatique des collectes ;
- [ ] amélioration des contrôles de qualité des données ;
- [ ] davantage de visualisations interactives ;
- [ ] gestion avancée des bases de données ;
- [ ] système d'export avancé ;
- [ ] authentification et gestion des utilisateurs ;
- [ ] journalisation des opérations ;
- [ ] documentation technique complète ;
- [ ] déploiement Cloud.

---

## 🤝 Contribution

Les contributions sont les bienvenues.

Avant toute contribution :

1. créer une branche ;
2. développer la fonctionnalité ;
3. tester les modifications ;
4. créer un commit clair ;
5. pousser la branche ;
6. proposer une Pull Request.

---

## 📄 Licence

La licence du projet sera définie ultérieurement.

---

## 👨‍💻 Auteur

**Berly LORA**

Data & Digital Solutions

---

## ⭐ DataForge

**Collect → Clean → Store → Analyze → Visualize**

> Transforming raw data into actionable information.