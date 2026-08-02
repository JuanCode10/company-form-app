# Import libraries
import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from db import db
import models # todo: code db models

# Import blueprints


# Create app code

def create_app(db_url=None):

    app = Flask(__name__)

    # App general config
    app.config["PROPAGATE_EXCEPTIONS"] = True # if exception occurs, propagate to main app for visibility
    app.config["API_TITLE"] = "Company Form REST API" # documentation title
    app.config["API_VERSION"] = "v1" # version of the API 
    app.config["OPENAPI_VERSION"] = "3.0.3" # standard for API documentation
    app.config["OPENAPI_URL_PREFIX"] = "/" # where the root of the api is
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui" # use swagger for API documentation 
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/" # load swagger code from here

    # SQLAlchemy config
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db") # database url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app) # initalize database

    api = Api(app)

    with app.app_context(): # create DB tables in case they don't exist
        db.create_all()

    # Register blueprints...
    #todo: code blueprints

    return app