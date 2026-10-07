from db import db
from datetime import datetime, timezone

class LeadModel(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))

    # Relationsihps
    customer = db.relationship("CustomerModel", back_populates="lead")