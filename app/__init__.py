import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_restful import Api

NoctiWave = Flask(__name__)

# --- CHANGE 1: The database path MUST be in the /tmp folder ---
# Vercel's main filesystem is read-only. /tmp is the only writable folder.
db_directory = "/tmp/noctiwave.sqlite3"
# -------------------------------------------------------------

NoctiWave.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_directory
db = SQLAlchemy(NoctiWave)
enc = Bcrypt(NoctiWave)
api = Api(NoctiWave)

def app_creator():
    NoctiWave.config["SECRET_KEY"] = "@Emperor_Noctivagous"
    NoctiWave.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
    NoctiWave.config["UPLOAD_FOLDER"] = "app/static/img/profile"

    from flask import render_template, Blueprint
    from app.user.auth import auth_bp
    from app.user.dashboard import dashboard_bp
    from app.campaign.api import CampaignResource
    from app.ad_request.api import AdRequestResource, NegotiationResource
    from app.user.api import InfluencerResource, InfluencerSearch, SponsorResource

    @NoctiWave.route("/")
    def home():
        return redirect(url_for("auth.login"))
    
    NoctiWave.register_blueprint(auth_bp)
    NoctiWave.register_blueprint(dashboard_bp)

    api.add_resource(CampaignResource, "/api/campaign", "/api/campaign/<string:campaign_id>")
    api.add_resource(AdRequestResource, "/api/ad-request", "/api/ad-request/<int:ad_request_id>")
    api.add_resource(NegotiationResource, "/api/negotiation", "/api/negotiation/<int:negotiation_id>")
    api.add_resource(InfluencerResource, "/api/search_influencer", "/api/search_influencer/<string:username_or_name>")
    api.add_resource(InfluencerSearch, "/api/search_influencerid", "/api/search_influencerid/<int:influencer_id>")
    api.add_resource(SponsorResource, "/api/search_sponsor", "/api/search_sponsor/<int:sponsor_id>")

    # --- CHANGE 2: DELETED the NoctiWave.run() line ---
    # This line will crash Vercel. Vercel uses Gunicorn to run the app.
    # --------------------------------------------------

    return NoctiWave


def database_creator():
    from app.user.models import User, Notification
    from app.user.admin.models import Admin
    from app.user.sponsor.models import Sponsor
    from app.user.influencer.models import Influencer
    from app.campaign.models import Campaign
    from app.ad_request.models import AdRequest, Negotiation
    
    # We must also update the path check to just check for the file
    if not os.path.exists(db_directory):
        # We don't need to create folders anymore, just the database
        with NoctiWave.app_context():
            db.create_all()
            print("Database created and tables initialized. Let's Go!")
    else:
            print("Database already exists. Let's Go!")

# --- CHANGE 3: Added these lines at the end ---
# This runs your functions and creates the 'app' variable Vercel looks for.
app = app_creator()
database_creator()
# ----------------------------------------------
