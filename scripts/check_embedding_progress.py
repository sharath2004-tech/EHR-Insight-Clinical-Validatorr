import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM patient_encounters WHERE clinical_embedding IS NOT NULL"))
    embedded = result.fetchone()[0]
    
    result = conn.execute(text("SELECT COUNT(*) FROM patient_encounters"))
    total = result.fetchone()[0]
    
    percentage = (embedded / total * 100) if total > 0 else 0
    
    print(f"Embedding Progress: {embedded:,} / {total:,} ({percentage:.1f}%)")
    
    if embedded == total:
        print(" All records have embeddings!")
    elif embedded > 100:
        print(f"Still processing... {total - embedded:,} records remaining")
    else:
        print(" Embedding generation may not be running")
