from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import BYTEA
import numpy as np
db = SQLAlchemy()

class Faces(db.Model):
    """
    Store faces
    """
    __tablename__ = 'faces'
    face_id = db.Column(db.Integer, primary_key = True)
    path = db.Column(db.String)
    name = db.Column(db.String)
    encoding = db.Column(BYTEA)
    num_faces = db.Column(db.Integer)

    def __init__(self, path, name, encoding, num_faces):
        self.path = path
        self.name = name
        self.encoding = encoding
        self.num_faces = num_faces

class MetaData(db.Model):
    __tablename__ = 'metadata'
    face_id = db.Column(db.Integer, db.ForeignKey('faces.face_id'), primary_key = True)
    version_number = db.Column(db.String)
    date = db.Column(db.String)
    location = db.Column(db.String)

    def __init__(self, face_id, version, date, location):
        self.face_id = face_id
        self.version_number = version
        self.date = date
        self.location = location