from db import db
from datetime import datetime, timezone

class ProductCategoryModel(db.Model):
    __tablename__ = "product_categories"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )

    # Many-to-many realtionship
    leads = db.relationship(
        "LeadModel",
        back_populates="product_categories",
        secondary="leads_product_categories"
    )
