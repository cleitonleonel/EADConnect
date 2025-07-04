from eadconnect.client import EducationAPI
from eadconnect.config import (
    load_configurations,
    save_credentials
)
from eadconnect.utils.auth import authenticate
from eadconnect.utils.file_manager import save_exercise_data
# from eadconnect.services.notifier import start_monitor

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

courses = [
    # {'title': 'Comunicação e Linguagem', 'id': 2273329, 'course_name': 'comunicacao_e_linguagem'},
    # {'title': 'Sistemas Operacionais', 'id': 2273383, 'course_name': 'sistemas_operacionais'},,
    # {'title': 'Arquitetura e Organização de Computadores', 'id': 2274882, 'course_name': 'arquitetura_organizacao_de_computadores'},
    # {'title': 'Empreendedorismo', 'id': 2274884, 'course_name': 'empreendedorismo'},
    {'title': 'Fundamentos de Redes de Computadores', 'id': 3187911, 'course_name': 'fundamentos_de_redes_de_computadores'},
    {'title': 'Gestão de Projetos', 'id': 3187728, 'course_name': 'gestao_de_projetos'},
]


async def grades_check():
    """Função para verificar as notas."""
    profile = client.get_me()
    user = profile.get('user', {})
    logger.info(f"👤 Perfil: {user['name']} ({user['email']})")
    logger.info("Bem vindo ao Education")
    logger.info("\n🔄 Extraindo dados dos cursos...\n")
    my_courses = client.get_my_courses()
    actual_courses = [
        course for course in my_courses.get('courses', {}) if course['status'] == 'isActual'
    ]
    for actual_course in actual_courses:
        logger.info(f"📚 {actual_course['name']} ({actual_course['id']})")
        my_grades = client.get_grades(course_id=actual_course['id'])
        logger.info("🔄 Extraindo dados das notas...")
        final_grade = my_grades.get('finalGrade', 'N/A')
        logger.info(f"📊 Nota Final: {final_grade['value']}")
        logger.info(f"{100 * '='}")
        await asyncio.sleep(2)


async def extract_data():
    logger.info("🔍 Extraindo dados dos cursos...")
    for course in courses:
        logger.info(f"\n📘 {course['title']}")
        topics = client.get_contents(course['id']).get('topics')
        # print(topics)
        children_list = [{'id': c['id'], 'title': c['title']} for c in topics[2]['children']]
        logger.info(f"🔍 {len(children_list)} tópicos encontrados.")

        for topic in children_list:
            logger.info(f"📝 Extraindo: {topic['title']}")
            data = client.get_exercises(course['id'], topic['id'])
            exercises = {
                'discipline': course['title'],
                'title': topic['title'],
                'content': data['topics'][4]['content']
            }
            # print(exercises)
            logger.info("🔄 Extraindo dados dos exercícios...")
            logger.info(f"📊 {len(data['topics'][4]['content'])} exercícios encontrados.")
            logger.info(f"💾 Salvando dados para o tópico: {topic['title']}")
            save_exercise_data(
                exercises,
                course['course_name'],
                topic['id']
            )
            await asyncio.sleep(2)


if __name__ == '__main__':
    config = load_configurations()
    username = config.get('auth', {}).get('username')
    password = config.get('auth', {}).get('password')
    if not username or not password:
        username = input("Usuário: ")
        password = input("Senha: ")
        save_credentials(username, password)

    print(username, password)
    client = EducationAPI("faesa", username, password)
    client.access_token = authenticate(client, 3)

    my_courses = client.get_my_courses()
    actual_courses = [
        course for course in my_courses.get('courses', {}) if course['status'] == 'isActual'
    ]
    print(actual_courses)
    for actual_course in actual_courses:
        logger.info(f"📚 {actual_course['name']} ({actual_course['id']})")

    # monitor_settings = config.get('monitor', {})
    # start_monitor(client, monitor_settings)

    """try:
        asyncio.run(extract_data())
    except KeyboardInterrupt:
        logging.info(
            'Bot interrupted by user.\n'
            'Disconnecting...'
        )"""