from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class PractitionerProfile(Base):
    __tablename__ = "practitioner_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    profession = Column(String(100), nullable=True)        # Diyetisyen, Psikolog vs.
    license_number = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)

    experience_years = Column(Integer, nullable=True)
    specialties = Column(Text, nullable=True)              # örn JSON/string list
    session_duration_min = Column(Integer, nullable=True)  # varsayılan seans süresi

    user = relationship("User", back_populates="practitioner_profile")
