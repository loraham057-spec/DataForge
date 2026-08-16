from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent

DB = ROOT / "data" / "database" / "data_collection.db"

DATASETS = {
    "books": ROOT / "data" / "cleaned" / "books_full.csv",
    "gaaraas": ROOT / "data" / "cleaned" / "gaaraas_full.csv",
}


def check_csv(name, path):
    print("\n" + "=" * 60)
    print(f"CSV : {name}")
    print("=" * 60)

    if not path.exists():
        print(f"❌ Fichier absent : {path}")
        return None

    df = pd.read_csv(path)

    print(f"✅ Fichier       : {path.name}")
    print(f"📊 Lignes        : {len(df):,}")
    print(f"📋 Colonnes      : {len(df.columns)}")

    print("\nColonnes :")
    for column in df.columns:
        print(f"   • {column}")

    duplicate_count = df.duplicated().sum()
    print(f"\n🔁 Doublons      : {duplicate_count:,}")

    empty_columns = [
        column
        for column in df.columns
        if df[column].isna().all()
    ]

    if empty_columns:
        print("⚠️ Colonnes entièrement vides :")
        for column in empty_columns:
            print(f"   • {column}")
    else:
        print("✅ Aucune colonne entièrement vide")

    return df


def check_database():
    print("\n" + "=" * 60)
    print("SQLITE")
    print("=" * 60)

    if not DB.exists():
        print(f"❌ Base absente : {DB}")
        return

    connection = sqlite3.connect(DB)

    tables = pd.read_sql_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
        """,
        connection,
    )

    print("Tables :")
    for table in tables["name"]:
        print(f"   • {table}")

    for name in DATASETS:

        result = pd.read_sql_query(
            f'SELECT COUNT(*) AS total FROM "{name}"',
            connection,
        )

        total = int(result.iloc[0]["total"])

        print(f"\n{name.upper()}")
        print(f"📊 SQLite : {total:,} lignes")

    connection.close()


def main():

    print("=" * 60)
    print("DATAFORGE — DATA INTEGRITY CHECK")
    print("=" * 60)

    csv_data = {}

    for name, path in DATASETS.items():
        csv_data[name] = check_csv(name, path)

    check_database()

    print("\n" + "=" * 60)
    print("COMPARAISON CSV / SQLITE")
    print("=" * 60)

    if not DB.exists():
        return

    connection = sqlite3.connect(DB)

    for name, df in csv_data.items():

        if df is None:
            continue

        sql_total = pd.read_sql_query(
            f'SELECT COUNT(*) AS total FROM "{name}"',
            connection,
        ).iloc[0]["total"]

        csv_total = len(df)

        if csv_total == sql_total:
            print(
                f"✅ {name}: CSV={csv_total:,} "
                f"| SQLite={sql_total:,}"
            )
        else:
            print(
                f"⚠️ {name}: CSV={csv_total:,} "
                f"| SQLite={sql_total:,}"
            )

    connection.close()

    print("\n" + "=" * 60)
    print("FIN DU CONTRÔLE")
    print("=" * 60)


if __name__ == "__main__":
    main()