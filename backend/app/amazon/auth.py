import os
import time
import logging
import requests
from requests_auth_aws_sigv4 import AWSSigV4
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("amazon.auth")

class AmazonAuthenticator:
    def __init__(self):
        self.lwa_client_id = os.getenv("LWA_CLIENT_ID")
        self.lwa_client_secret = os.getenv("LWA_CLIENT_SECRET")
        self.lwa_refresh_token = os.getenv("LWA_REFRESH_TOKEN")
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY")
        self.aws_secret_key = os.getenv("AWS_SECRET_KEY")
        self.aws_region = os.getenv("AWS_REGION", "eu-west-1")

        self._access_token = None
        self._token_expiry = 0

    def get_access_token(self) -> str:
        """
        Returns a valid LWA access token, refreshing it if necessary.
        """
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token

        logger.info("Requesting new LWA access token...")
        
        response = requests.post(
            "https://api.amazon.com/auth/o2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.lwa_refresh_token,
                "client_id": self.lwa_client_id,
                "client_secret": self.lwa_client_secret
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get LWA token: {response.text}")
            response.raise_for_status()
            
        data = response.json()
        self._access_token = data["access_token"]
        # Subtract 60 seconds as a safety buffer
        self._token_expiry = time.time() + data["expires_in"] - 60 
        
        logger.info("LWA access token successfully refreshed.")
        return self._access_token

    def get_sigv4_auth(self) -> AWSSigV4:
        """
        Returns the requests-auth-aws-sigv4 object for signing SP-API requests.
        """
        return AWSSigV4(
            "execute-api",
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region=self.aws_region
        )
