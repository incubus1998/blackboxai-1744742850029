import os
from oauthlib.oauth2 import WebApplicationClient
import requests

# Google OAuth2 configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-client-id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-client-secret")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

def get_google_provider_cfg():
    """Get Google's OAuth2 configuration"""
    try:
        return requests.get(GOOGLE_DISCOVERY_URL).json()
    except Exception as e:
        print(f"Error fetching Google provider config: {e}")
        return None

def init_oauth_client():
    """Initialize OAuth client"""
    if GOOGLE_CLIENT_ID == "your-client-id":
        print("Warning: Using development mode for Google OAuth")
        return None
    return WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_auth_url(client, request_base_url):
    """Get Google OAuth authorization URL"""
    try:
        # Get Google's provider configuration
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            return None

        # Get authorization endpoint
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Construct authorization URL
        # Adjust redirect_uri to include /login prefix to match blueprint url_prefix
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=request_base_url + "/login/callback/google",
            scope=["openid", "email", "profile"],
        )
        return request_uri
    except Exception as e:
        print(f"Error generating Google auth URL: {e}")
        return None

def get_google_token(client, request_base_url, code):
    """Get Google OAuth token"""
    try:
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            return None

        token_endpoint = google_provider_cfg["token_endpoint"]
        
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=code,
            redirect_url=request_base_url + "/login/callback/google",
            client_secret=GOOGLE_CLIENT_SECRET,
        )
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        return client.parse_request_body_response(token_response.text)
    except Exception as e:
        print(f"Error getting Google token: {e}")
        return None

def get_google_user_info(client, token):
    """Get Google user information"""
    try:
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            return None

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        if userinfo_response.json().get("email_verified"):
            return {
                "email": userinfo_response.json()["email"],
                "name": userinfo_response.json()["name"],
                "picture": userinfo_response.json().get("picture", ""),
            }
        return None
    except Exception as e:
        print(f"Error getting Google user info: {e}")
        return None
