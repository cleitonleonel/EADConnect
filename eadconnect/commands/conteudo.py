import os
import asyncio
import logging
from typing import List, Dict, Any
from eadconnect.client import EducationAPI
from eadconnect.utils.file_manager import save_exercise_data

logger = logging.getLogger(__name__)

CURSOS: List[Dict[str, Any]] = [
    # {'title': 'Comunicação e Linguagem', 'id': 2273329, 'course_name': 'comunicacao_e_linguagem'},
    # {'title': 'Sistemas Operacionais', 'id': 2273383, 'course_name': 'sistemas_operacionais'},
    # {'title': 'Arquitetura e Organização de Computadores', 'id': 2274882, 'course_name': 'arquitetura_organizacao_de_computadores'},
    # {'title': 'Empreendedorismo', 'id': 2274884, 'course_name': 'empreendedorismo'},
    # {'title': 'Fundamentos de Redes de Computadores', 'id': 3187911, 'course_name': 'fundamentos_de_redes_de_computadores'},
    # {'title': 'Gestão de Projetos', 'id': 3187728, 'course_name': 'gestao_de_projetos'},
    # {'title': 'Engenharia de Software I', 'id': 3188339, 'course_name': 'engenharia_de_software_i'},
    # {'title': 'Tópicos Especiais', 'id': 3188331, 'course_name': 'topicos_especiais'},
    # {'title': 'Estrutura de Dados', 'id': 3898590, 'course_name': 'estrutura_de_dados'},
    # {'title': 'Programação Orientada a Objetos', 'id': 3898587, 'course_name': 'programacao_orientada_a_objetos'},
    # {'title': 'Desenvolvimento para Dispositivo Móveis', 'id': 3902914, 'course_name': 'desenvolvimento_para_dispositivo_moveis'},
    # {'title': 'Engenharia de Software II', 'id': 3902912, 'course_name': 'engenharia_de_software_ii'},
    # {'title': 'Modelagem e Desenvolvimento de Dados', 'id': 4913821, 'course_name': 'modelagem_e_desenvolvimento_de_dados'},
    # {'title': 'Ferramentas de Desenvolvimento Web', 'id': 4913822, 'course_name': 'ferramentas_de_desenvolvimento_web'},
    {'title': 'Interface Humano-Computador', 'id': 4914478, 'course_name': 'interface_humano_computador'},
    {'title': 'Arquitetura de Sistemas', 'id': 4914479, 'course_name': 'arquitetura_de_sistemas'},
    # {'title': '', 'id': 39, 'course_name': ''},
    # {'title': '', 'id': 39, 'course_name': ''}
    # {'title': '', 'id': 39, 'course_name': ''},
    # {'title': '', 'id': 39, 'course_name': ''}
]



async def extrair_conteudo(client: EducationAPI, courses: List[Dict[str, Any]], download_type: str = "ALL") -> None:
    """
    Extrai e faz download dos conteúdos dos tópicos dos cursos especificados.
    
    Args:
        client (EducationAPI): Instância autenticada do cliente da API.
        courses (List[Dict[str, Any]]): Lista de dicionários contendo informações dos cursos.
        download_type (str): Define o tipo de download a ser realizado.
        Padrão é "ALL" para baixar todos os arquivos.
    """
    logger.info("🔍 Extraindo dados dos cursos...")
    for course in courses:
        topics = client.get_contents(course['id']).get('topics', [])
        if not topics or len(topics) <= 2:
            logger.warning(f"⚠️ Tópicos não encontrados para o curso: {course['title']}")
            continue

        children_list = [{'id': c['id'], 'title': c['title']} for c in topics[2].get('children', [])]
        logger.info(f"🔍 {len(children_list)} tópicos encontrados para {course['title']}.")

        for topic in children_list:
            logger.info(f"📝 Extraindo: {topic['title']}")

            if download_type in ["TOPICS", "ALL"]:
                download_path = f"src/topics/{course['course_name']}/{topic['title'].capitalize().replace(' ', '_')}"
                os.makedirs(download_path, exist_ok=True)
                url_file_data = client.get_file_url(course['id'], topic['id'])
                url_file = url_file_data.get('file')
                print(f"📁 URL do arquivo: {url_file}")

                if not url_file:
                    continue

                client.download_topic_file(url_file, download_path)

            logger.info("🔄 Extraindo dados dos exercícios...")
            data = client.get_exercises(course['id'], topic['id'])
            sub_topics = data.get('topics', [])

            for sub_topic in sub_topics:
                if not sub_topic['viewed'] and sub_topic['title'] != "Exercícios":
                    progress_result = client.progress(course['id'], sub_topic['id'])
                    if progress_result:
                        print(f"📊 Progresso para {sub_topic['title']}")
                        await asyncio.sleep(5)

            if not data or len(sub_topics) <= 4:
                print(f"⚠️ Dados insuficientes para o tópico: {topic['title']}")
                continue

            exercises = {
                'discipline': course['title'],
                'title': topic['title'],
                'content': data['topics'][4].get('content', [])
            }

            #if not exercises['content'].get('questions')[0]['options'][0].get('isCorrect'):
            #    print(f"⚠️ Exercícios não encontrados ou formato inesperado para o tópico: {topic['title']}")
            #    continue

            logger.info(f"📊 {len(exercises['content'])} exercícios encontrados.")
            logger.info(f"💾 Salvando dados para o tópico: {topic['title']}")

            if download_type in ["EXERCISES", "ALL"]:
                save_exercise_data(exercises, course['course_name'], topic['id'])

            await asyncio.sleep(2)  # Pequena pausa para evitar sobrecarga na API
