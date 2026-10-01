import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv
from pathlib import Path

def ingest_data():
    load_dotenv(override=True)

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    csv_path = project_root / 'data' / 'MIMIC_IV_Trasncript.csv'
    schema_path = project_root / 'src' / 'database' / 'schema.sql'

    if not csv_path.exists():
        raise FileNotFoundError(f"CRITICAL: Could not find dataset at {csv_path}")

    db_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME")
    )

    engine = create_engine(db_url)

    print(f"Executing schema setup from:\n  {schema_path}")

    with engine.begin() as conn:
        with open(schema_path, "r") as file:
            conn.execute(text(file.read()))

    print(f"Loading clinical data from:\n  {csv_path}")

    df = pd.read_csv(csv_path)
    df = df.where(pd.notnull(df), None)

    print(f"Ingesting {len(df)} records into remote AWS PostgreSQL instance...")

    df.to_sql(
        "patient_encounters",
        engine,
        if_exists="append",
        index=False
    )

    print("✅ Baseline legacy data ingestion complete.")

if __name__ == "__main__":
    ingest_data()