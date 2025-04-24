from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from src.user_service.database import Base, engine


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

if __name__=="__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)