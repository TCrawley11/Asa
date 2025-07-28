from shutil import ExecError
from agents import function_tool
from fastmcp import Client
from fastmcp.client.auth import OAuth
import logging
import os
from dotenv import load_dotenv
from fastmcp.tools import FunctionTool

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

oauth = OAuth(mcp_url="http://localhost:8000/mcp")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Google calendar env stuff
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
TOKEN_FILE = os.getenv("TOKEN_FILE_PATH", ".gcp-saved-tokens.json")
SCOPES = [os.getenv("CALENDAR_SCOPES", "https://www.googleapis.com/auth/calendar")]
REDIRECT_PORT = int(os.getenv("OAUTH_CALLBACK_PORT", 8080))
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/oauth2callback"


@function_tool
def get_google_creds():
    helper = google_calendar_auth()
    creds = helper.get_creds()
    return creds.to_json() if creds else None


class google_calendar_auth:
    def get_creds():
        creds = None

        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            logger.error("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET")
            raise ValueError("Missing Google OAuth credentials in config")

        # Step 1. load exisiting tokens
        if os.path.exists(TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                logger.info("Loaded credentials from token file")
            except Exception as e:
                logger.warning(
                    f"Failed to load credentials from {TOKEN_FILE}: {
                        e
                    }. Attempting re-authentication"
                )

        # Step 2. Refreshing creds or initiate the auth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Credentials expired. Refreshing...")
                try:
                    creds.refresh(Request())
                    logger.info("Credentials refreshed successfully.")
                except Exception as e:
                    logger.error(
                        f"Failed to refresh credentials: {e}. Need to re-authenticate."
                    )
                    creds = None  # Force re-authentication
            else:
                logger.info(
                    "No valid credentials found or refresh failed. Starting OAuth flow..."
                )
                # use client_secret dict directly for Flow
                client_config = {
                    "installed": {
                        "client_id": GOOGLE_CLIENT_ID,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        # Add both for flexibility
                        "redirect_uris": ["http://localhost", REDIRECT_URI],
                    }
                }
                try:
                    # Use InstalledAppFlow instead of Flow
                    logger.info("Attempting authentication using InstalledAppFlow...")
                    flow_installed = InstalledAppFlow.from_client_config(
                        client_config=client_config,
                        scopes=SCOPES,
                        redirect_uri=REDIRECT_URI,  # Ensure this matches console setup
                    )
                    # This method should handle the server start, browser opening, and code retrieval.
                    creds = flow_installed.run_local_server(
                        port=REDIRECT_PORT,
                        authorization_prompt_message="Please visit this URL to authorize:\n{url}",
                        success_message="Authentication successful! You can close this window.",
                        open_browser=True,
                    )
                    logger.info("InstalledAppFlow completed.")

                except Exception as e:
                    logger.error(
                        f"Error during InstalledAppFlow execution: {e}", exc_info=True
                    )
                    creds = None  # Ensure creds is None on error

                if creds:
                    # Save the credentials for the next run
                    try:
                        with open(TOKEN_FILE, "w") as token_file:
                            token_file.write(creds.to_json())
                        logger.info(f"Credentials saved successfully to {TOKEN_FILE}")
                    except Exception as e:
                        logger.error(f"Failed to save credentials to {TOKEN_FILE}: {e}")
                else:
                    logger.error(
                        "OAuth flow using InstalledAppFlow did not result in valid credentials."
                    )
                    return None

        # Step 3. Final Check
        if not creds or not creds.valid:
            logger.error("Failed to obtain valid credentials after all steps.")
            return None

        logger.info("Successfully obtained valid credentials.")
        return creds


if __name__ == "__main__":
    auth_helper = google_calendar_auth()
    creds = auth_helper.get_creds()
    if not creds:
        print("Failed to obtain credentials.")
        exit(1)
    print("Obtained credentials!")
