from db import db
from datetime import datetime, timezone

class StoreModel(db.Model):
    __tablename__ = "stores"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # location string for now, possibly in future waze/google maps address
    location = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc)
    )
    udpated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )

    # Relationships
    leads = db.relationship("LeadModel", back_populates="store")
    sales_reps = db.relationship("SalesRepModel", back_populates="store")