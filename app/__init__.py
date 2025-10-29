# /app/__init__.py

import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_restful import Api

# --- CONFIGURATION ---

NoctiWave = Flask(__name__)

# This is the path to Render's persistent disk
persistent_data_path = '/var/data'
db_file_path = os.path.join(persistent_data_path, 'noctiwave.sqlite3')

# Point SQLAlchemy to the new, permanent path
NoctiWave.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{db_file_path}'

# Initialize extensions
db = SQLAlchemy(NoctiWave)
enc = Bcrypt(NoctiWave)
api = Api(NoctiWave)

# --- APPLICATION FACTORY ---

def app_creator():
    NoctiWave.config["SECRET_KEY"] = "@Emperor_Noctivagous"
    NoctiWave.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
    
    # Also save uploads to the persistent disk
    persistent_upload_path = os.path.join(persistent_data_path, 'uploads')
    if not os.path.exists(persistent_upload_path):
        os.makedirs(persistent_upload_path, exist_ok=True)
    NoctiWave.config["UPLOAD_FOLDER"] = persistent_upload_path

    # Import blueprints and models here to avoid circular imports
    from flask import render_template
    from app.user.auth import auth_bp
    from app.user.dashboard import dashboard_bp
    from app.campaign.api import CampaignResource
    from app.ad_request.api import AdRequestResource, NegotiationResource
    from app.user.api import InfluencerResource, InfluencerSearch, SponsorResource

    # --- ROUTES & BLUEPRINTS ---
    @NoctiWave.route("/")
    def home():
        return redirect(url_for("auth_bp.login"))
    
    NoctiWave.register_blueprint(auth_bp)
    NoctiWave.register_blueprint(dashboard_bp)

    # --- API RESOURCES ---
    api.add_resource(CampaignResource, "/api/campaign", "/api/campaign/<string:campaign_id>")
    api.add_resource(AdRequestResource, "/api/ad-request", "/api/ad-request/<int:ad_request_id>")
    api.add_resource(NegotiationResource, "/api/negotiation", "/api/negotiation/<int:negotiation_id>")
    api.add_resource(InfluencerResource, "/api/search_influencer", "/api/search_influencer/<string:username_or_name>")
    api.add_resource(InfluencerSearch, "/api/search_influencerid", "/api/search_influencerid/<int:influencer_id>")
    api.add_resource(SponsorResource, "/api/search_sponsor", "/api/search_sponsor/<int:sponsor_id>")

    # DO NOT run the app here. Gunicorn will do it.
    # NoctiWave.run(debug=True, port=6969)  <-- THIS LINE WAS REMOVED

    return NoctiWave


# --- DATABASE CREATOR ---

def database_creator(app):
    # Import models
    from app.user.models import User, Notification
    from app.user.admin.models import Admin
    from app.user.sponsor.models import Sponsor
    from app.user.influencer.models import Influencer
    from app.campaign.models import Campaign
    from app.ad_request.models import AdRequest, Negotiation

    # Use the 'app' object that gets passed in from run.py
    with app.app_context():
        # Create the /var/data directory if it doesn't exist
        # This is the path from the top of the file
        if not os.path.exists(persistent_data_path):
            os.makedirs(persistent_data_path, exist_ok=True)
        
        # db.create_all() is safe to run.
        # It will only create tables that don't already exist.
        db.create_all()
        print("Database tables checked/created. Let's Go!")
