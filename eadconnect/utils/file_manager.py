import json
import shutil
from pathlib import Path
from typing import Dict, Any, Union
from eadconnect.utils.pdf import PDF
from eadconnect.config import (
    pdf_path,
    json_path,
    logo_file
)


def ensure_dirs(*paths: Union[str, Path]) -> None:
    """
    Cria os diretórios solicitados caso eles não existam.
    
    Args:
        *paths (Union[str, Path]): Argumentos variáveis de caminhos a serem criados.
    """
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def save_json(data: Dict[str, Any], output_dir: Path, filename: str) -> Path:
    """
    Salva um dicionário como JSON em uma pasta específica do sistema de arquivos.
    
    Args:
        data (Dict[str, Any]): Dicionário com dados a serem salvos.
        output_dir (Path): O caminho do diretório destino.
        filename (str): Nome do arquivo, sem a extensão .json.
        
    Retorna:
        Path: Caminho do arquivo JSON recém-criado.
    """
    file_path = output_dir / f"{filename}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return file_path


def create_json_directory(course_name: str) -> Path:
    """
    Garante a existência e retorna o caminho do diretório JSON focado ao curso.
    
    Args:
        course_name (str): O nome/apelido do curso (ex: 'arquitetura').
        
    Retorna:
        Path: O diretório para abrigar arquivos JSON deste curso.
    """
    output_dir = json_path / course_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def create_pdf_directory(course_name: str) -> Path:
    """
    Garante a existência e retorna o caminho do diretório PDF focado ao curso.
    
    Args:
        course_name (str): O nome/apelido do curso.
        
    Retorna:
        Path: O diretório para abrigar arquivos PDF gerados deste curso.
    """
    output_dir = pdf_path / course_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def zip_directory(directory: Path) -> None:
    """
    Compacta o conteúdo inteiro de um diretório em um arquivo .zip no nível acima.
    
    Args:
        directory (Path): O diretório alvo a ser compactado.
    """
    shutil.make_archive(
        base_name=directory.as_posix(),
        format='zip',
        root_dir=directory
    )


def zip_json_directory(directory: Path) -> None:
    """
    Compacta um diretório JSON inteiro em um arquivo .zip.
    
    Args:
        directory (Path): Diretório alvo JSON.
    """
    zip_directory(directory)


def zip_pdf_directory(directory: Path) -> None:
    """
    Compacta um diretório PDF inteiro em um arquivo .zip.
    
    Args:
        directory (Path): Diretório alvo PDF.
    """
    zip_directory(directory)


def save_exercise_data(exercises: Dict[str, Any], title: str, filename: str) -> None:
    """
    Agrupa o salvamento de dados extraídos: em JSON e como documento PDF gerado dinamicamente,
    terminando por zippar ambos os diretórios criados.
    
    Args:
        exercises (Dict[str, Any]): Dados agregados do exercício a compor os arquivos.
        title (str): O título que será a base pro nome do diretório do curso.
        filename (str): Nome do arquivo final gerado (JSON e PDF base).
    """
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
