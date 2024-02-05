from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from sqlalchemy.orm import Session
from typing import Type, Generic, TypeVar, List 
from .models import Base, User  # Ensure you import all your model classes here as needed

server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')
driver = 'ODBC Driver 17 for SQL Server'
DATABASE_URL = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


T = TypeVar('T', bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db_session: Session, id: int) -> T:
        try:
            return db_session.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error as appropriate
            print(f"Error retrieving {self.model.__name__} by id: {e}")
            return None

    def get_all(self, db_session: Session) -> List[T]:
        try:
            return db_session.query(self.model).all()
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error
            print(f"Error retrieving all {self.model.__name__}: {e}")
            return []

    def create(self, db_session: Session, obj_in) -> T:
        try:
            obj = self.model(**obj_in)
            db_session.add(obj)
            db_session.commit()
            db_session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error
            print(f"Error creating {self.model.__name__}: {e}")
            return None

    def update(self, db_session: Session, obj: T, obj_in) -> T:
        try:
            for var, value in vars(obj_in).items():
                setattr(obj, var, value) if value else None
            db_session.commit()
            db_session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error
            print(f"Error updating {self.model.__name__}: {e}")
            return None

    def delete(self, db_session: Session, id: int) -> None:
        try:
            obj = db_session.query(self.model).get(id)
            if obj:
                db_session.delete(obj)
                db_session.commit()
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error
            print(f"Error deleting {self.model.__name__}: {e}")


# Extend the base repository for the User model
class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db_session: Session, email: str) -> User:
        return db_session.query(User).filter(User.EmailAddress == email).first()
