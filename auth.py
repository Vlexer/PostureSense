from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = "your_secret_key"
oauth = OAuth(app)

# Google OAuth configuration
google = oauth.register(
    name="google",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "email profile"},
)

@app.route("/login")
def login():
    return google.authorize_redirect(url_for("authorize", _external=True))

@app.route("/authorize")
def authorize():
    token = google.authorize_access_token()
    user_info = google.get("userinfo").json()
    session["email"] = user_info["email"]  # Store the email in the session
    return redirect(url_for("index"))

@app.route("/")
def index():
    email = session.get("email", None)
    return f"Logged in as: {email}" if email else "You are not logged in."
