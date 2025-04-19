import json
from education.config import CREDENTIALS


def load_token():
    """Carrega o token de acesso armazenado."""
    if CREDENTIALS.exists():
        with open(CREDENTIALS, "r") as f:
            credentials = json.load(f)
            return credentials.get("accessToken")
    return None


def save_token(token):
    """Salva o token de acesso no arquivo de credenciais."""
    with open(CREDENTIALS, "w") as f:
        json.dump({"accessToken": token}, f, indent=4)


def authenticate(client):
    """Autentica o usuário e retorna o token de acesso."""
    access_token = load_token()
    if not access_token:
        login_response = client.login()
        access_token = client.persist_access_token(
            login_response.get('accessToken')
        ).get('accessToken')
        save_token(access_token)
    return access_token


def check_credentials(username, password):
    """Verifica se as credenciais do usuário estão presentes."""
    return bool(username and password)
