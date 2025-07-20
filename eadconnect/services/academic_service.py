import logging
from eadconnect.client import EducationAPI

logging.basicConfig(level=logging.INFO)


class AcademicService:

    def __init__(self, client: 'EducationAPI'):
        self.client = client

    def get_active_periods(self):
        """Retrieve the active periods from the EducationAPI client."""
        response = self.client.get_periods()
        return response

    def get_active_period_id(self):
        """Get the ID of the current active period."""
        periods = self.get_active_periods()
        if not periods:
            logging.warning("No active periods found.")
            return None

        return periods[-1].get('id')

    def get_all_disciplines(self):
        """Retrieve the user's disciplines from the EducationAPI client."""
        my_courses = self.client.get_my_courses()
        return my_courses.get('courses', {})

    def get_active_disciplines(self, period_id: int = None):
        """Retrieve the active courses for the current period."""
        if not period_id:
            logging.warning("No active period ID found.")
            period_id = self.get_active_period_id()

        return self.get_disciplines(period_id)

    def get_disciplines(self, period_id: int, status: list = None):
        """Retrieve the courses for a specific period."""
        if status is None:
            status = ['isActual']
        if not period_id:
            logging.warning("No active period ID found.")
            return []

        data = self.client.get_my_courses(period=period_id)
        return [
            course for course in data.get('courses', [])
            if course.get('status') in status
        ]

    def get_grade_by_discipline_id(self, discipline_id: int):
        """Retrieve the grades for a specific discipline."""
        response = self.client.get_grades(discipline_id)

        if not response or not response.get('finalGrade'):
            logging.warning(f"No grades found for discipline ID: {discipline_id}")
            return {}

        return response

    def get_grades_by_course(self, courses: list):
        """Retrieve the final grades for each course."""
        grades = {}
        for course in courses:
            course_id = course.get("id")
            response = self.client.get_grades(course_id)
            grades[course["name"]] = response.get("finalGrade")

        return grades

    def detect_grade_changes(self, current_grades: dict, previous_grades: dict):
        """Detect changes in grades between current and previous grades."""
        changes = {}
        for name, current_grade in current_grades.items():
            previous_grade = previous_grades.get(name)
            if previous_grade != current_grade:
                changes[name] = {
                    "before": previous_grade,
                    "now": current_grade
                }

        return changes

    def get_messages(self, items_per_page: int = 15):
        """Retrieve the messages for the platform."""
        messages = self.client.get_messages(items_per_page=items_per_page)
        conversations = messages.get('conversations', [])
        if not conversations:
            logging.warning("No notifications found.")
            return []

        return [
            conversation.get('messages', [])[0] for conversation in conversations
        ]

    def get_calendar(self, start_date: str = None, end_date: str = None):
        """Retrieve the calendar for the platform."""
        calendar = self.client.get_calendar(start_date, end_date)
        if not calendar:
            logging.warning("No events found in the calendar.")
            return

        return calendar