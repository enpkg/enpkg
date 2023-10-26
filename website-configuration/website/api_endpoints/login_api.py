"""API handling the Oauth authentications of the users using ORCID.

Implementative details
----------------------
The API is implemented using authlib's OAuth 2.0 framework.
"""
import os
from flask import redirect, jsonify
from flask_dance.contrib.orcid import make_orcid_blueprint, orcid
from ..application import app
from ..models import User
# from ..oauth import orcid  # Import your Authlib OAuth instance

blueprint = make_orcid_blueprint(
    client_id=os.environ.get("ORCID_CLIENT_ID"),
    client_secret=os.environ.get("ORCID_CLIENT_SECRET"),
    scope="openid profile",
    redirect_to="/login/orcid/callback",
)

app.register_blueprint(blueprint, url_prefix="/login/orcid")

@app.route('/login/orcid/callback')
def orcid_callback():
    """Internal route to handle the ORCID OAuth callback."""
    if not orcid.authorized:
        return redirect("/")
    
    # Retrieve the token from ORCID
    response = orcid.get('oauth/token')

    return jsonify(response.json())

    # Retrieve the ORCID ID of the authenticated user
    # resp = orcid.get('orcid', token=token)
    # orcid_id = resp.json().get('orcid')
    orcid_id = "0000-0002-1825-0097"

    _user = User.from_orcid(orcid_id)

    return redirect("/upload")

# Login route to initiate ORCID OAuth
# @app.route('/login/orcid', methods=['GET'])
# def orcid_login():
#     """Login route to initiate ORCID OAuth."""
#     return redirect("/login/orcid/callback")

# Logout route to clear the session
@app.route('/logout')
def logout():
    """Logout route to clear the session."""
    User.logout()
    return redirect("/")