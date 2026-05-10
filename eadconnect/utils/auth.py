import json
import logging
import time
from typing import Optional, Any
from eadconnect.config import CREDENTIALS
# Utilizado para tipagem apenas, para evitar erros de importação cíclica ou indisponível
from eadconnect.client import EducationAPI


def load_access_token() -> Optional[str]:
    """
    Carrega o token de acesso armazenado no arquivo local de credenciais.
    
    Retorna:
        Optional[str]: O token de acesso caso exista, senão None.
    """
    if CREDENTIALS.exists():
        with open(CREDENTIALS, "r", encoding="utf-8") as f:
            credentials = json.load(f)
            return credentials.get("accessToken")
    return None


def save_access_token(token: Optional[str]) -> None:
    """
    Salva o token de acesso de volta no arquivo local de credenciais.
    
    Args:
        token (Optional[str]): O token a ser salvo. Se None for passado, será salvo como null.
    """
    with open(CREDENTIALS, "w", encoding="utf-8") as f:
        json.dump({"accessToken": token}, f, indent=4)


def is_token_valid(client: EducationAPI, token: str) -> bool:
    """
    Verifica se o token é válido efetuando uma requisição ao endpoint de verificação do perfil (/me).
    
    Args:
        client (EducationAPI): Instância autenticada do cliente da API.
        token (str): Token a ser testado.
        
    Retorna:
        bool: True se o token é válido, False caso contrário.
    """
    try:
        response = client.check_me(token)
        # Se for um dicionário (a resposta JSON convertida), assume-se válido
        return isinstance(response, dict)
    except Exception:
        return False


def authenticate(client: EducationAPI, attempts: int = 5, auto_save: bool = True) -> Optional[str]:
    """
    Tenta autenticar com a API usando o token de acesso em cache; se inválido ou inexistente,
    refaz o fluxo de login usando o usuário e senha da instância de client fornecida.
    
    Args:
        client (EducationAPI): Instância com credenciais e sessão.
        attempts (int): Quantidade de tentativas permitidas de login em caso de falhas consecutivas.
        auto_save (bool): Se verdadeiro, salva automaticamente o token em cache se sucesso.
        
    Retorna:
        Optional[str]: Retorna o token validado se sucesso.
        
    Lança:
        Exception: Se o login falhar após o número de tentativas permitidas.
    """
    for attempt in range(attempts):
        access_token = load_access_token()
        
        # O token é válido?
        if access_token and is_token_valid(client, access_token):
            return access_token

        # O token está expirado ou vazio -> Tenta realizar o login
        if not access_token:
            login_response = client.login()

            if not isinstance(login_response, dict):
                logging.error("Erro ao fazer login: resposta inválida (credenciais incorretas ou problema de API).")
                return None

            primary_token = login_response.get('accessToken', '')
            assume_response = client.persist_access_token(primary_token)
            
            if isinstance(assume_response, dict):
                access_token = assume_response.get('accessToken')
            else:
                access_token = None

            if not access_token:
                raise Exception("Falha ao obter o token final de acesso (persist_access_token falhou).")

        # Salva o novo token
        if auto_save:
            save_access_token(access_token)

        # Verifica se obteve sucesso real
        if access_token and is_token_valid(client, access_token):
            return access_token

        # Se falhou por algum motivo desconhecido no fim do ciclo, limpa o token armazenado
        save_access_token(None)
        time.sleep(1)

    raise Exception(f"Falha na autenticação após {attempts} tentativas.")


def check_credentials(username: Optional[str], password: Optional[str]) -> bool:
    """
    Verifica se as credenciais mínimas básicas estão presentes.
    
    Args:
        username (Optional[str]): Nome de usuário.
        password (Optional[str]): Senha do usuário.
        
    Retorna:
        bool: True se ambos existirem e não forem vazios.
    """
    return bool(username and password)
