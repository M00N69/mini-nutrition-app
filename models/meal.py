from sqlalchemy import Column, Integer, String, Float
from database.database import Base

class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    calories = Column(Float)
    proteins = Column(Float)
    carbs = Column(Float)
    fats = Column(Float)
