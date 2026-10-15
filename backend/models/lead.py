from db import db
from datetime import datetime, timezone

from constants.lead_choices import PURCHASE_TIME_HORIZON_CHOICES


class LeadModel(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    budget = db.Column(db.Float, nullable=False)
    customer_comments = db.Column(db.String(500), nullable=True)
    purchase_time_horizon = db.Column(
        db.Enum(
            *PURCHASE_TIME_HORIZON_CHOICES,
            name="purchase_time_horizon",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )

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