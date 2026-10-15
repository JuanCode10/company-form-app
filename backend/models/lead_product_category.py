from db import db

class LeadsProductCategories(db.Model):
    __tablename__ = "leads_product_categories"

    id = db.Column(db.Integer, primary_key=True)

    # Many-to-many map
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"))
    product_category_id = db.Column(db.Integer, db.ForeignKey("product_categories.id"))