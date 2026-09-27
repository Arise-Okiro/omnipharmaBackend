import datetime
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models.schema import Tenant, User, Product, InventoryBatch

# Configure bcrypt password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed_database():
    db = SessionLocal()
    try:
        # Check if already seeded to prevent duplicate inserts
        if db.query(Tenant).first(): #--->By adding the check if db.query(Tenant).first(): return, the script was made idempotent
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding initial MedNova pharmacy data...")

        # 1. Seed Tenants (Store Outlets)
        store_1 = Tenant(name="MedNova Pharmacy - Banjara Hills", store_code="HYD-001", city="Hyderabad")
        store_2 = Tenant(name="MedNova Pharmacy - Hitec City", store_code="HYD-002", city="Hyderabad")
        db.add_all([store_1, store_2])
        db.flush()  # Flushes changes so store_1.id and store_2.id are generated

        # 2. Seed Users across roles (Password for all: 'password123')
        default_pw = hash_password("password123")
        users = [
            User(store_id=store_1.id, username="karthik_pharmacist", password_hash=default_pw, role="pharmacist"),
            User(store_id=store_1.id, username="inventory_manager_1", password_hash=default_pw, role="inventory_controller"),
            User(store_id=store_1.id, username="field_auditor", password_hash=default_pw, role="auditor"),
            User(store_id=store_1.id, username="head_office_admin", password_hash=default_pw, role="head_office"),
            # Another store's pharmacist to test isolation tomorrow
            User(store_id=store_2.id, username="rahul_pharmacist", password_hash=default_pw, role="pharmacist"),
        ]
        db.add_all(users)

        # 3. Seed Master Products (with active chemical molecules)
        p1 = Product(name="Dolo 650", category="Analgesics", composition="Paracetamol 650mg", base_price=30.50)
        p2 = Product(name="Crocin 650", category="Analgesics", composition="Paracetamol 650mg", base_price=32.00)
        p3 = Product(name="Augmentin 625 Duo", category="Antibiotics", composition="Amoxicillin + Clavulanic Acid", base_price=200.00)
        p4 = Product(name="Glycomet 500", category="Antidiabetic", composition="Metformin 500mg", base_price=45.00)
        db.add_all([p1, p2, p3, p4])
        db.flush()

        # 4. Seed Batches for Store 1 (Banjara Hills)
        today = datetime.date.today()
        batches = [
            # Dolo 650: Batch A expires soon (near-expiry), Batch B expires next year
            InventoryBatch(store_id=store_1.id, product_id=p1.id, batch_number="DOLO-B1", expiry_date=today + datetime.timedelta(days=45), quantity=50),
            InventoryBatch(store_id=store_1.id, product_id=p1.id, batch_number="DOLO-B2", expiry_date=today + datetime.timedelta(days=365), quantity=120),
            # Crocin 650 in stock (alternative to Dolo)
            InventoryBatch(store_id=store_1.id, product_id=p2.id, batch_number="CROC-B1", expiry_date=today + datetime.timedelta(days=180), quantity=80),
            # Augmentin
            InventoryBatch(store_id=store_1.id, product_id=p3.id, batch_number="AUG-B1", expiry_date=today + datetime.timedelta(days=90), quantity=25),
        ]
        db.add_all(batches)

        db.commit()
        print("Database seeded successfully with outlets, users, products, and inventory batches.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()