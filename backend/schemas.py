from marshmallow import Schema, fields, validate

PURCHASE_TIME_HORIZON_CHOICES = [
    "immediately",
    "within_one_month",
    "within_three_months",
    "within_six_months",
    "more_than_six_months",
]

STORE_CHOICES = [
    "la-mora",
    "san-sebastian",
]

# Plain Schemas
class PlainCustomerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    phone_number = fields.Str(required=True)
    created_at = fields.DateTime(format="iso", dump_only=True)
    updated_at = fields.DateTime(format="iso", dump_only=True)

# Regular Schemas
class FormPayloadSchema(Schema):
    customer = fields.Nested(PlainCustomerSchema(), required=True)
    store = fields.Str(required=True, validate=validate.OneOf(STORE_CHOICES))
    products = fields.List(fields.Str(), required=True)
    budget = fields.Int(required=True)
    purchase_time_horizon = fields.Str(
        required=True,
        validate=validate.OneOf(PURCHASE_TIME_HORIZON_CHOICES),
    )
    customer_comments = fields.Str(required=True)