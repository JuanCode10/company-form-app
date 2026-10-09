from db import db
from datetime import datetime, timezone

class LeadModel(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"))

    # Relationsihps
    customer = db.relationship("CustomerModel", back_populates="leads")
    store = db.relationship("StoreModel", back_populates="leads")