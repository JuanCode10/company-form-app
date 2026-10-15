from db import db
from datetime import datetime, timezone

class SalesRepModel(db.Model):
    __tablename__ = "sales_reps"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    phone_number = db.Column(db.String(14), unique=True, nullable=True)
    email = db.Column(db.String(100), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), 
        nullable=False, 
        default=datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Foreign Keys
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"))

    # Relationships
    leads = db.relationship("LeadModel", back_populates="sales_rep")
    store = db.relationship("StoreModel", back_populates="sales_reps")