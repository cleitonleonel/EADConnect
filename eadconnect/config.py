import toml
from pathlib import Path
from typing import Optional, Dict, Any

# Define os diretórios base do projeto
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Caminhos dos arquivos de configuração e credenciais
CONFIGURATIONS: Path = BASE_DIR / "configurations.toml"
CREDENTIALS: Path = BASE_DIR / "credentials.json"

# Caminhos para armazenamento de artefatos
pdf_path: Path = BASE_DIR / "src/pdfs"
json_path: Path = BASE_DIR / "src/json"
logo_path: Path = BASE_DIR / "src/img"
font_path: Path = BASE_DIR / "src/fonts"
logo_file: Path = logo_path / "logo.png"

# Cria os diretórios caso não existam
for path in [pdf_path, json_path, font_path, logo_path]:
    path.mkdir(parents=True, exist_ok=True)


def load_configurations() -> Optional[Dict[str, Any]]:
    """
    Carrega as configurações a partir do arquivo 'configurations.toml'.

    Retorna:
        Optional[Dict[str, Any]]: Um dicionário com as configurações caso o arquivo exista,
        ou None se o arquivo não for encontrado.
    """
    if CONFIGURATIONS.exists():
        config = toml.load(CONFIGURATIONS)
        return config

    return None


def save_credentials(username: str, password: str) -> None:
    """
    Salva as credenciais básicas (usuário e senha) no arquivo 'configurations.toml'.

    Args:
        username (str): Nome de usuário para autenticação.
        password (str): Senha para autenticação.
    """
    config = {
        "auth": {
            "username": username,
            "password": password
        }
    }
    with open(CONFIGURATIONS, "w", encoding="utf-8") as f:
        toml.dump(config, f)
