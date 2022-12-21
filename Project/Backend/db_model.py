from sqlalchemy import MetaData, Column, Integer, String, DateTime, ForeignKey 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from datetime import datetime


metadata = MetaData()
Base = declarative_base(metadata = metadata)

# One feature set to have multiple children which represent sepparate features
class Feature_set(Base):
    __tablename__ = 'Feature_set_table'

    ID = Column(Integer, primary_key = True, nullable = False, unique = True, autoincrement = True)
    created = Column(DateTime, default = datetime.now())
    last_updated = Column(DateTime, default = datetime.now, onupdate = datetime.now)
    name = Column(String(30), unique = True)

    feature_children = relationship("Features", back_populates = "feature_set_parent")

class Features(Base):
    __tablename__ = 'Features_table'

    ID = Column(Integer, primary_key = True, nullable = False, unique = True, autoincrement = True)
    feature = Column(String(100), unique = True)

    feature_set_parent_id = Column(Integer, ForeignKey("Feature_set_table.ID"))
    feature_set_parent = relationship("Feature_set", back_populates = "feature_children")