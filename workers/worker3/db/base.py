from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

metadata = MetaData(schema="poc")

Base = declarative_base(metadata=metadata)