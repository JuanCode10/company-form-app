from flask  import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import db
from schemas import FormPayloadSchema, PlainCustomerSchema

blp = Blueprint("Leads", __name__, description="Lead requests receiver.")

@blp.route("/leads")
class Leads(MethodView):

    @blp.arguments(FormPayloadSchema)
    def post(self, form_payload):
        print("form_payload:", form_payload)
        
        return {"status": 200, "message": "Payload received"}