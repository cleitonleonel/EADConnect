import logging
from typing import List, Dict, Any, Optional
from eadconnect.client import EducationAPI

# Configuração básica de log para o serviço
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AcademicService:
    """
    Serviço responsável por gerenciar operações acadêmicas de alto nível,
    como consulta de disciplinas, notas, períodos, notificações e mensagens.
    """

    def __init__(self, client: EducationAPI) -> None:
        """
        Inicializa o serviço acadêmico.

        Args:
            client (EducationAPI): Instância autenticada do cliente da API.
        """
        self.client: EducationAPI = client

    def get_active_periods(self) -> List[Dict[str, Any]]:
        """
        Recupera todos os períodos acadêmicos do usuário.

        Retorna:
            List[Dict[str, Any]]: Lista de períodos acadêmicos.
        """
        response = self.client.get_periods()
        return response if isinstance(response, list) else []

    def get_active_period_id(self) -> Optional[int]:
        """
        Obtém o ID do período acadêmico atual/ativo.

        Retorna:
            Optional[int]: ID do período ativo ou None se não encontrado.
        """
        periods = self.get_active_periods()
        if not periods:
            logger.warning("Nenhum período ativo encontrado.")
            return None

        # Assume-se que o último período da lista é o mais atual
        return periods[-1].get('id')

    def get_all_disciplines(self) -> List[Dict[str, Any]]:
        """
        Recupera todas as disciplinas do usuário.

        Retorna:
            List[Dict[str, Any]]: Lista de todas as disciplinas.
        """
        my_courses = self.client.get_my_courses()
        return my_courses.get('courses', []) if isinstance(my_courses, dict) else []

    def get_active_disciplines(self, period_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Recupera as disciplinas ativas para o período atual ou especificado.

        Args:
            period_id (Optional[int]): ID do período para filtrar. Se None, usa o período ativo.

        Retorna:
            List[Dict[str, Any]]: Lista de disciplinas ativas.
        """
        if not period_id:
            period_id = self.get_active_period_id()
            if not period_id:
                logger.warning("ID do período ativo não encontrado.")
                return []

        return self.get_disciplines(period_id)

    def get_disciplines(self, period_id: int, status: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Recupera as disciplinas de um período específico filtradas por status.

        Args:
            period_id (int): ID do período acadêmico.
            status (Optional[List[str]]): Lista de status permitidos (ex: ['isActual']). Padrão: ['isActual'].

        Retorna:
            List[Dict[str, Any]]: Lista de disciplinas que atendem aos critérios.
        """
        if status is None:
            status = ['isActual']
        
        if not period_id:
            logger.warning("ID do período não fornecido.")
            return []

        data = self.client.get_my_courses(period=period_id)
        if not isinstance(data, dict):
            return []

        return [
            course for course in data.get('courses', [])
            if course.get('status') in status
        ]

    def get_grade_by_discipline_id(self, discipline_id: int) -> Dict[str, Any]:
        """
        Recupera as notas de uma disciplina específica.

        Args:
            discipline_id (int): ID da disciplina.

        Retorna:
            Dict[str, Any]: Dicionário com dados das notas da disciplina.
        """
        response = self.client.get_grades(discipline_id)

        if not isinstance(response, dict) or not response.get('finalGrade'):
            logger.warning(f"Nenhuma nota encontrada para a disciplina ID: {discipline_id}")
            return {}

        return response

    def get_grades_by_course(self, courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Recupera as notas finais para uma lista de disciplinas.

        Args:
            courses (List[Dict[str, Any]]): Lista de dicionários de disciplinas contendo 'id' e 'name'.

        Retorna:
            Dict[str, Any]: Mapeamento de nome da disciplina para a nota final.
        """
        grades: Dict[str, Any] = {}
        for course in courses:
            course_id = course.get("id")
            if course_id:
                response = self.client.get_grades(course_id)
                if isinstance(response, dict):
                    grades[course.get("name", str(course_id))] = response.get("finalGrade")

        return grades

    def detect_grade_changes(self, current_grades: Dict[str, Any], previous_grades: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detecta alterações entre o conjunto atual de notas e um conjunto anterior (cache).

        Args:
            current_grades (Dict[str, Any]): Notas atuais obtidas da API.
            previous_grades (Dict[str, Any]): Notas anteriormente salvas.

        Retorna:
            Dict[str, Any]: Mapeamento das disciplinas que sofreram alteração.
        """
        changes: Dict[str, Any] = {}
        for name, current_grade in current_grades.items():
            previous_grade = previous_grades.get(name)
            if previous_grade != current_grade:
                changes[name] = {
                    "before": previous_grade,
                    "now": current_grade
                }

        return changes

    def get_messages(self, items_per_page: int = 15) -> List[Dict[str, Any]]:
        """
        Recupera as mensagens mais recentes da plataforma.

        Args:
            items_per_page (int): Quantidade de mensagens a buscar.

        Retorna:
            List[Dict[str, Any]]: Lista das mensagens mais recentes.
        """
        response = self.client.get_messages(items_per_page=items_per_page)
        if not isinstance(response, dict):
            return []
            
        conversations = response.get('conversations', [])
        if not conversations:
            logger.warning("Nenhuma mensagem encontrada.")
            return []

        # Retorna a mensagem mais recente de cada conversa
        return [
            conversation.get('messages', [])[0] 
            for conversation in conversations 
            if conversation.get('messages')
        ]

    def get_notifications(self, items_per_page: int = 5) -> List[Dict[str, Any]]:
        """
        Recupera as notificações do sistema.

        Args:
            items_per_page (int): Quantidade de notificações a buscar.

        Retorna:
            List[Dict[str, Any]]: Lista de notificações.
        """
        response = self.client.get_notifications(items_per_page=items_per_page)
        if not isinstance(response, dict):
            return []
            
        notifications = response.get('notifications', [])
        if not notifications:
            logger.warning("Nenhuma notificação encontrada.")
            return []

        return notifications

    def get_calendar(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Recupera o calendário de compromissos acadêmicos.

        Args:
            start_date (Optional[str]): Data inicial (YYYY-MM-DD).
            end_date (Optional[str]): Data final (YYYY-MM-DD).

        Retorna:
            List[Dict[str, Any]]: Lista de eventos do calendário.
        """
        response = self.client.get_calendar(start_date or "", end_date or "")
        return response if isinstance(response, list) else []