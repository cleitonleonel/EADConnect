from education.client import EducationAPI
from education.config import (
    load_credentials,
    save_credentials
)
from education.utils.auth import authenticate
from education.utils.file_manager import save_exercise_data
import time

courses = [
    {'title': 'Comunicação e Linguagem', 'id': 2273329, 'course_name': 'sistemas_operacionais'},
    {'title': 'Sistemas Operacionais', 'id': 2273383, 'course_name': 'comunicacao_e_linguagem'},
    # {'title': 'Arquitetura e Organização de Computadores', 'id': 2274882,
    # 'course_name': 'arquitetura_organizacao_de_computadores'},
    # {'title': 'Empreendedorismo', 'id': 2274884, 'course_name': 'empreendedorismo'},
]

if __name__ == '__main__':
    username, password = load_credentials()
    if not username or not password:
        username = input("Usuário: ")
        password = input("Senha: ")
        save_credentials(username, password)

    client = EducationAPI("nome_da_unidade_de_ensino", username, password)
    client.access_token = authenticate(client)

    for course in courses:
        print(f"\n📘 {course['title']}")
        topics = client.get_contents(course['id']).get('topics')
        children_list = [{'id': c['id'], 'title': c['title']} for c in topics[2]['children']]
        print(f"🔍 {len(children_list)} tópicos encontrados.")

        for topic in children_list:
            print(f"📝 Extraindo: {topic['title']}")
            data = client.get_exercises(course['id'], topic['id'])
            exercises = {
                'discipline': course['title'],
                'title': topic['title'],
                'content': data['topics'][4]['content']
            }

            save_exercise_data(
                exercises,
                course['course_name'],
                topic['id']
            )

            time.sleep(2)
