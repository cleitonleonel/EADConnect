import json
import shutil
from pathlib import Path
from education.utils.pdf import PDF
from education.config import (
    pdf_path,
    json_path,
    logo_file
)


def ensure_dirs(*paths):
    """Cria diretórios se não existirem."""
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def save_json(data, course_name, filename):
    """Salva um dicionário como JSON em uma pasta específica da disciplina."""
    output_dir = json_path / course_name
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{filename}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return file_path


def create_pdf_directory(course_name):
    """Cria o diretório onde o PDF será salvo."""
    output_dir = pdf_path / course_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def zip_pdf_directory(directory):
    """Compacta um diretório de PDFs em um arquivo .zip."""
    shutil.make_archive(
        base_name=directory.as_posix(),
        format='zip',
        root_dir=directory
    )


def save_exercise_data(exercises, title, content):
    save_json(exercises, title, content)
    output_pdf = create_pdf_directory(title)
    pdf = PDF(
        exercises,
        output_pdf,
        logo_path=logo_file.as_posix()
    )
    pdf.create_document()
    zip_pdf_directory(output_pdf)
