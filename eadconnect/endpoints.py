class Endpoints:
    """
    Classe base para armazenar os endpoints utilizados pela API.
    Centraliza as URLs base e de serviços da plataforma do Grupo A.
    """
    URL_API: str = 'https://api.plataforma.grupoa.education'
    URL_CLIENT: str = 'v2/safea-client'
    CLIENT_AUTH: str = f'{URL_CLIENT}/auth'
    USERS_INFO: str = f'{URL_CLIENT}/users'
    PLATFORM_V1: str = 'v1/plataforma'
    PLATFORM_V2: str = 'v2/plataforma'
