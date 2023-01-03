from sqlalchemy import MetaData, Column, Integer, String, DateTime, ForeignKey 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from datetime import datetime


metadata = MetaData()
Base = declarative_base(metadata = metadata)

# One feature set to have multiple children which represent sepparate features
class Feature_set(Base):
    __tablename__ = 'Feature_set_table'

    ID = Column(Integer, primary_key = True, unique = True, autoincrement = True)
    created = Column(DateTime, default = datetime.now)
    last_updated = Column(DateTime, default = datetime.now, onupdate = datetime.now)
    name = Column(String(30), unique = True)

    feature_children = relationship('Features', cascade='all,delete', backref='Feature_set_table', overlaps="Feature_set_table,feature_children")

class Features(Base):
    __tablename__ = 'Features_table'

    ID = Column(Integer, primary_key = True, autoincrement = True)
    feature = Column(String(10000))

    parent_id = Column(Integer, ForeignKey('Feature_set_table.ID', ondelete='CASCADE'))
    parent = relationship('Feature_set', backref = backref('Features_table', cascade = 'all, delete', overlaps="Feature_set_table,feature_children"), overlaps="Feature_set_table,feature_children")