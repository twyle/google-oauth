from json import dump, load
from os import mkdir, path
from typing import Any, Optional

from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import BaseModel, Field


class GoogleOAuth(BaseModel):
    secrets_file: str
    scopes: list[str] = Field(default_factory=list)
    api_service_name: str
    api_version: str
    credentials_dir: str
    credentials_file_name: Optional[str] = 'credentials.json'

    def credentials_to_dict(self, credentials: Credentials) -> dict:
        """Convert credentials to a dict."""
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
        }

    def create_default_credentials_path(self) -> str:
        """Create the default credentials directory."""
        current_user_home_dir = path.expanduser('~')
        if not path.exists(path.join(current_user_home_dir, self.credentials_dir)):
            mkdir(path.join(current_user_home_dir, self.credentials_dir))
        return path.join(current_user_home_dir, self.credentials_dir)

    def get_default_credentials_path(self) -> str:
        """Generate the default api token file location."""
        credentials_dir: str = self.create_default_credentials_path()
        credentials_file_path = path.join(credentials_dir, self.credentials_file_name)
        return credentials_file_path

    def get_credentials(self) -> Credentials:
        """Get the credentials."""
        credentials: Credentials = None
        credentials_path: str = self.get_default_credentials_path()
        try:
            with open(credentials_path, 'r', encoding='utf-8') as creds:
                credentials = Credentials(**load(creds))
        except FileNotFoundError:
            pass
        return credentials

    def generate_credentials_google_server(self) -> Credentials:
        flow = InstalledAppFlow.from_client_secrets_file(self.secrets_file, self.scopes)
        credentials = flow.run_local_server(port=0)
        return credentials

    def generate_credentials_google_console(self) -> Credentials:
        flow = Flow.from_client_secrets_file(
            self.secrets_file,
            scopes=self.scopes,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob',
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        print('Please go to this URL: {}'.format(auth_url))
        code = input('Enter the authorization code: ')
        flow.fetch_token(code=code)
        credentials: Credentials = flow.credentials
        return credentials

    def save_credentials(self, credentials: Credentials) -> None:
        credentials_dict = self.credentials_to_dict(credentials)
        credentials_path: str = self.get_default_credentials_path()
        with open(credentials_path, 'w', encoding='utf-8') as f:
            dump(credentials_dict, f)

    def credentials_expired(self, credentials: Credentials) -> bool:
        # youtube_client = self.get_youtube_client(credentials=credentials)
        # youtube_find_request = youtube_client.search().list(q='', part='id')
        # try:
        #     youtube_find_request.execute()
        # except RefreshError:
        #     return True
        # return False
        return False

    def get_oauth_client(self, credentials: Credentials) -> Any:
        oauth_client = build(
            self.api_service_name, self.api_version, credentials=credentials
        )
        return oauth_client

    def authenticate_google_server(self) -> Any:
        credentials: Credentials = self.get_credentials()
        if not credentials or self.credentials_expired(credentials=credentials):
            credentials = self.generate_credentials_google_server()
            self.save_credentials(credentials=credentials)
        oauth_client = self.get_oauth_client(credentials=credentials)
        return oauth_client

    def authenticate_google_console(self) -> Any:
        credentials: Credentials = self.get_credentials()
        if not credentials or self.credentials_expired(credentials=credentials):
            credentials = self.generate_credentials_google_console()
            self.save_credentials(credentials=credentials)
        oauth_client = self.get_oauth_client(credentials=credentials)
        return oauth_client
