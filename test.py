from oryks_google_oauth import GoogleOAuth, YouTubeScopes


client_secret_file: str = '/home/lyle/Professional Projects/youtube/client_secret.json'
api_service_name: str = 'youtube'
api_version: str = 'v3'
credentials_dir: str = '.youtube'
scopes: list[str] = [YouTubeScopes.youtube.value]
oauth: GoogleOAuth = GoogleOAuth(
    secrets_file=client_secret_file,
    scopes=scopes,
    api_service_name=api_service_name,
    api_version=api_version,
    credentials_dir=credentials_dir
)
youtube_client = oauth.authenticate_google_server()
youtube_find_request = youtube_client.search().list(q='python programming videos', part='id, snippet')
print(youtube_find_request.execute())
