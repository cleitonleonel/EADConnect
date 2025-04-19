import toml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CREDENTIALS_PATH = BASE_DIR / "credentials.toml"
CREDENTIALS = BASE_DIR / "credentials.json"

pdf_path = BASE_DIR / "src/pdfs"
json_path = BASE_DIR / "src/json"
logo_path = BASE_DIR / "src/img"
logo_file = logo_path / "logo.png"

for path in [pdf_path, json_path, logo_path]:
    path.mkdir(parents=True, exist_ok=True)


def load_credentials():
    if CREDENTIALS_PATH.exists():
        config = toml.load(CREDENTIALS_PATH)
        return (
            config.get("auth", {}).get("username"),
            config.get("auth", {}).get("password")
        )
    return None, None


def save_credentials(username, password):
    config = {
        "auth": {
            "username": username,
            "password": password
        }
    }
    with open(CREDENTIALS_PATH, "w") as f:
        toml.dump(config, f)
