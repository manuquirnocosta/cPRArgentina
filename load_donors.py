import sqlite3
import pandas as pd

DB_NAME = "cpra.db"
CSV_PATH = "data/donors.csv"  # podés cambiarlo si cargás otro CSV


def load_csv_to_db(csv_path):
    # Leer CSV
    df = pd.read_csv(csv_path, sep=";", dtype=str)


    # Normalizar strings
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.upper()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    inserted = 0
    ignored = 0

    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO donors (
                    donor_id, sexo, edad, fecha_operativo,
                    A1, A2, B1, B2,
                    DRB1_1, DRB1_2,
                    DQB1_1, DQB1_2,
                    abo, rh
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["donor_id"],
                row["sexo"],
                row["edad"],
                row["fecha_operativo"],
                row["A1"],
                row["A2"],
                row["B1"],
                row["B2"],
                row["DRB1_1"],
                row["DRB1_2"],
                row["DQB1_1"],
                row["DQB1_2"],
                row["abo"],
                row["rh"],
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            # Ya existe ese donor_id → se ignora
            ignored += 1

    conn.commit()
    conn.close()

    print(f"✅ Insertados: {inserted}")
    print(f"⚠️ Ignorados (duplicados): {ignored}")


if __name__ == "__main__":
    load_csv_to_db(CSV_PATH)
