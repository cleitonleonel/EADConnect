import json
import shutil
from pathlib import Path
from eadconnect.utils.pdf import PDF
from eadconnect.config import (
    pdf_path,
    json_path,
    logo_file
)


def ensure_dirs(*paths):
    """Cria diretórios se não existirem."""
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def save_json(data, output_dir, filename):
    """Salva um dicionário como JSON em uma pasta específica da disciplina."""
    file_path = output_dir / f"{filename}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return file_path


def create_json_directory(course_name):
    """Cria o diretório onde o PDF será salvo."""
    output_dir = json_path / course_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def create_pdf_directory(course_name):
    """Cria o diretório onde o PDF será salvo."""
    output_dir = pdf_path / course_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def zip_directory(directory):
    """Compacta um diretório em um arquivo .zip."""
    shutil.make_archive(
        base_name=directory.as_posix(),
        format='zip',
        root_dir=directory
    )


def zip_json_directory(directory):
    """Compacta um diretório de PDFs em um arquivo .zip."""
    zip_directory(directory)


def zip_pdf_directory(directory):
    """Compacta um diretório de PDFs em um arquivo .zip."""
    zip_directory(directory)


def save_exercise_data(exercises, title, filename):
    output_json = create_json_directory(title)
    save_json(
        exercises,
        output_json,
        filename
    )
    zip_json_directory(output_json)

    output_pdf = create_pdf_directory(title)
    pdf = PDF(
        exercises,
        output_pdf,
        logo_path=logo_file.as_posix()
    )
    pdf.create_document()
    zip_pdf_directory(output_pdf)
