import toml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIGURATIONS = BASE_DIR / "configurations.toml"
CREDENTIALS = BASE_DIR / "credentials.json"

pdf_path = BASE_DIR / "src/pdfs"
json_path = BASE_DIR / "src/json"
logo_path = BASE_DIR / "src/img"
font_path = BASE_DIR / "src/fonts"
logo_file = logo_path / "logo.png"

for path in [pdf_path, json_path, font_path, logo_path]:
    path.mkdir(parents=True, exist_ok=True)


def load_configurations():
    if CONFIGURATIONS.exists():
        config = toml.load(CONFIGURATIONS)
        return config

    return None


def save_credentials(username, password):
    config = {
        "auth": {
            "username": username,
            "password": password
        }
    }
    with open(CONFIGURATIONS, "w") as f:
        toml.dump(config, f)
