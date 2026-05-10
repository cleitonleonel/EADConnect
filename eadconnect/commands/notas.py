import asyncio
import logging
from eadconnect.client import EducationAPI

logger = logging.getLogger(__name__)


async def verificar_notas(client: EducationAPI) -> None:
    """
    Verifica as notas do usuário e exibe as notas finais dos cursos em andamento.
    
    Args:
        client (EducationAPI): Instância autenticada do cliente da API.
    """
    profile = client.get_me()
    user = profile.get('user', {})
    logger.info(f"👤 Perfil: {user.get('name')} ({user.get('email')})")
    logger.info("Bem vindo ao Education")
    logger.info("\n🔄 Extraindo dados dos cursos...\n")
    
    my_courses = client.get_my_courses()
    actual_courses = [
        course for course in my_courses.get('courses', []) if course.get('status') == 'isActual'
    ]
    
    for actual_course in actual_courses:
        logger.info(f"📚 {actual_course.get('name')} ({actual_course.get('id')})")
        my_grades = client.get_grades(course_id=actual_course.get('id'))
        logger.info("🔄 Extraindo dados das notas...")
        final_grade = my_grades.get('finalGrade', {})
        logger.info(f"📊 Nota Final: {final_grade.get('value', 'N/A')}")
        logger.info(f"{100 * '='}")
        await asyncio.sleep(2)


async def listar_notas_por_curso(client: EducationAPI) -> None:
    """
    Lista os cursos atuais do usuário e obtém detalhadamente as notas de cada um.
    
    Args:
        client (EducationAPI): Instância autenticada do cliente da API.
    """
    periods = client.get_periods()
    print("Períodos:", periods)

    my_courses = client.get_my_courses()
    print("Cursos:", my_courses)

    actual_courses = [
        course for course in my_courses.get('courses', []) if course.get('status') == 'isActual'
    ]
    print("Cursos atuais:", actual_courses)
    
    for actual_course in actual_courses:
        logger.info(f"📚 {actual_course.get('name')} ({actual_course.get('id')})")
        logger.info("🔄 Extraindo dados das notas...")
        await asyncio.sleep(1)
        my_grades = client.get_grades(course_id=actual_course.get('id'))
        print(my_grades)
