"""
DATABASE SQL - Data Collection TP
---------------------------------
Cette couche gère la base SQL de l'application.

Choix technique :
- SQLite : base SQL légère, sans serveur à installer ;
- une table `books` pour Books to Scrape ;
- une table `gaaraas` pour Gaaraas ;
- remplacement contrôlé des tables lors d'une synchronisation ;
- lecture SQL pour afficher les données dans Streamlit.

La structure pourra être migrée vers PostgreSQL plus tard sans changer
la logique métier de l'interface.
"""

from pathlib import Path
import re
import sqlite3
import pandas as pd


def database_path(root: Path) -> Path:
    path = root / "data" / "database"
    path.mkdir(parents=True, exist_ok=True)
    return path / "data_collection.db"


def connection(root: Path) -> sqlite3.Connection:
    return sqlite3.connect(database_path(root))


def safe_identifier(name: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_]", "_", str(name)).strip("_")
    return value or "column"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    used = {}
    columns = []

    for col in result.columns:
        base = safe_identifier(col).lower()
        count = used.get(base, 0)
        used[base] = count + 1
        columns.append(base if count == 0 else f"{base}_{count}")

    result.columns = columns
    return result


def init_database(root: Path) -> None:
    """Crée la base SQL si elle n'existe pas encore."""
    with connection(root) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS database_info (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                application TEXT NOT NULL,
                description TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO database_info
            (id, application, description)
            VALUES (1, 'Data Collection TP',
                    'Base SQL des données collectées par Books to Scrape et Gaaraas')
            """
        )


def replace_table(root: Path, table_name: str, df: pd.DataFrame) -> int:
    """Remplace entièrement une table par le dataset fourni."""
    init_database(root)
    clean = normalize_columns(df)

    with connection(root) as conn:
        clean.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.execute(
            "UPDATE database_info SET updated_at = CURRENT_TIMESTAMP WHERE id = 1"
        )

    return len(clean)


def sync_dataset(root: Path, source: str, csv_path: Path) -> int:
    """Lit le CSV nettoyé et le synchronise dans la table SQL correspondante."""
    df = pd.read_csv(csv_path)

    if source == "books":
        table = "books"
    elif source == "gaaraas":
        table = "gaaraas"
    else:
        raise ValueError(f"Source SQL inconnue : {source}")

    return replace_table(root, table, df)


def read_table(root: Path, table_name: str) -> pd.DataFrame:
    """Retourne une table SQL sous forme de DataFrame."""
    allowed = {"books", "gaaraas"}
    if table_name not in allowed:
        raise ValueError("Table SQL non autorisée.")

    init_database(root)

    with connection(root) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)


def table_exists(root: Path, table_name: str) -> bool:
    with connection(root) as conn:
        row = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
            """,
            (table_name,),
        ).fetchone()
    return row is not None


def table_count(root: Path, table_name: str) -> int:
    if not table_exists(root, table_name):
        return 0

    with connection(root) as conn:
        return int(conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])


def list_tables(root: Path) -> list[str]:
    init_database(root)
    with connection(root) as conn:
        rows = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
            """
        ).fetchall()

    return [row[0] for row in rows]


def database_size(root: Path) -> int:
    path = database_path(root)
    return path.stat().st_size if path.exists() else 0
