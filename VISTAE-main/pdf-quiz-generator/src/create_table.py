from db.database import Base, engine
from db import models  # import all models to register them with Base

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()