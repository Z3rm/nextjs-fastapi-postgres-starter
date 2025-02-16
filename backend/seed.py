from sqlalchemy import select
from sqlalchemy.orm import Session
from db_engine import sync_engine
from models import User

def seed_user_if_needed():
    with Session(sync_engine) as session:
        with session.begin():
            existing_user = session.execute(select(User).where(User.name == "Zach")).scalars().first()
            if existing_user is not None:
                print("User 'Zach' already exists, skipping seeding")
                return
            print("Seeding user 'Zach'")
            session.add(User(name="Zach"))
            session.commit()
