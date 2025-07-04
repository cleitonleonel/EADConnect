import json
import time
from eadconnect.config import CREDENTIALS


def load_access_token() -> str | None:
    """Carrega o token de acesso armazenado no arquivo."""
    if CREDENTIALS.exists():
        with open(CREDENTIALS, "r") as f:
            credentials = json.load(f)
            return credentials.get("accessToken")
    return None


def save_access_token(token: str | None):
    """Salva o token de acesso no arquivo de credenciais."""
    with open(CREDENTIALS, "w") as f:
        json.dump({"accessToken": token}, f, indent=4)


def is_token_valid(client, token: str) -> bool:
    """Verifica se o token é válido consultando o endpoint /me."""
    try:
        return client.check_me(token)
    except Exception:
        return False


def authenticate(client, attempts: int = 5, auto_save: bool = True) -> str:
    """Autentica com a API usando o access_token armazenado ou refaz login se necessário."""
    for attempt in range(attempts):
        access_token = load_access_token()
        if access_token and is_token_valid(client, access_token):
            return access_token

        if not access_token:
            login_response = client.login()
            access_token = client.persist_access_token(
                login_response.get('accessToken')
            ).get('accessToken')

            if not access_token:
                raise Exception("Falha ao obter o token de acesso.")

        if auto_save:
            save_access_token(access_token)

        if is_token_valid(client, access_token):
            return access_token

        save_access_token(None)

        time.sleep(1)

    raise Exception("Falha na autenticação após múltiplas tentativas.")


def check_credentials(username: str | None, password: str | None) -> bool:
    """Verifica se as credenciais básicas estão presentes."""
    return bool(username and password)
