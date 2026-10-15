from db import db
from datetime import datetime, timezone

class LeadModel(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"))
    sales_rep_id = db.Column(db.Integer, db.ForeignKey("sales_reps.id"))

    # Relationsihps
    customer = db.relationship("CustomerModel", back_populates="leads")
    store = db.relationship("StoreModel", back_populates="leads")
    sales_rep = db.relationship("SalesRepModel", back_populates="leads")

    # Many-to-many relationship
    product_categories = db.relationship(
        "ProductCategoryModel",
        back_populates="leads",
        secondary="leads_product_categories"
    )