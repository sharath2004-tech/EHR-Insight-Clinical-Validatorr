"""
Quick Database Status Check
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("   DATABASE CONNECTION CHECK")
print("=" * 60)

# Check environment variables
print("\n📋 Database Configuration:")
print(f"   Host: {os.getenv('DB_HOST')}")
print(f"   Port: {os.getenv('DB_PORT')}")
print(f"   Database: {os.getenv('DB_NAME')}")
print(f"   User: {os.getenv('DB_USER')}")
print(f"   Password: {'*' * len(os.getenv('DB_PASSWORD', ''))}")

# Try to connect
print("\n🔍 Testing connection...")
try:
    from sqlalchemy import create_engine, text
    
    db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ Connection successful!")
        print(f"   PostgreSQL version: {version.split(',')[0]}")
        
        # Check if patient_encounters table exists
        print("\n🔍 Checking tables...")
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'patient_encounters';
        """))
        table_exists = result.fetchone()[0] > 0
        
        if table_exists:
            print("✅ patient_encounters table exists")
            
            # Check row count
            result = conn.execute(text("SELECT COUNT(*) FROM patient_encounters;"))
            row_count = result.fetchone()[0]
            print(f"   Records: {row_count}")
            
            if row_count == 0:
                print("\n⚠️  Table is EMPTY - No patient data loaded!")
                print("\n📝 To load data, run:")
                print("   python scripts/01_ingest_baseline_data.py")
            else:
                # Check unique patients
                result = conn.execute(text("SELECT COUNT(DISTINCT subject_id) FROM patient_encounters;"))
                patient_count = result.fetchone()[0]
                print(f"   Unique patients: {patient_count}")
                
                # Check if embeddings exist
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = 'patient_encounters' 
                    AND column_name = 'clinical_embedding';
                """))
                has_embeddings = result.fetchone()[0] > 0
                
                if has_embeddings:
                    result = conn.execute(text("""
                        SELECT COUNT(*) 
                        FROM patient_encounters 
                        WHERE clinical_embedding IS NOT NULL;
                    """))
                    embedded_count = result.fetchone()[0]
                    print(f"   Records with embeddings: {embedded_count}")
                    
                    if embedded_count == 0:
                        print("\n⚠️  No embeddings generated yet!")
                        print("\n📝 To generate embeddings, run:")
                        print("   python scripts/04_generate_embeddings.py")
                    else:
                        print("\n✅ Database is ready!")
                else:
                    print("\n⚠️  Embedding column doesn't exist!")
                    print("\n📝 To add embedding column, run:")
                    print("   python scripts/03_apply_vector_schema.py")
                    print("   python scripts/04_generate_embeddings.py")
        else:
            print("❌ patient_encounters table DOES NOT exist")
            print("\n📝 To create table and load data, run:")
            print("   python scripts/01_ingest_baseline_data.py")
        
except Exception as e:
    print(f"❌ Connection failed!")
    print(f"   Error: {str(e)}")
    
    if "Connection refused" in str(e):
        print("\n💡 PostgreSQL is not running!")
        print("\n📝 Solutions:")
        print("   1. Install PostgreSQL: https://www.postgresql.org/download/windows/")
        print("   2. OR use Docker: docker run -d --name postgres-ehr -e POSTGRES_PASSWORD=SecureEHR2026! -e POSTGRES_USER=fde_admin -e POSTGRES_DB=ehr_db -p 5432:5432 pgvector/pgvector:pg14")
        print("\nSee SETUP_DATABASE_WINDOWS.md for detailed instructions")
    elif "password authentication failed" in str(e):
        print("\n💡 Wrong password or user!")
        print("   Check your .env file credentials")
    elif "database" in str(e) and "does not exist" in str(e):
        print("\n💡 Database doesn't exist!")
        print("   Run: psql -U postgres -c \"CREATE DATABASE ehr_db;\"")

print("\n" + "=" * 60)
