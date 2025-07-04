from eadconnect.http.navigator import Browser
from eadconnect.endpoints import Endpoints


class EducationAPI(Browser, Endpoints):

    def __init__(
            self,
            institution: str = "faesa",
            username: str = None,
            password: str = None,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.institution = institution
        self.username = username
        self.password = password
        self.access_token = None
        self.set_headers()

    @property
    def base_url(self):
        return f'https://{self.institution.lower()}.grupoa.education'

    def login(self):
        self.headers.update({
            'Referer': f"{self.base_url}/"
        })
        payload = {
            'username': self.username,
            'password': self.password,
            'applicationAlias': 'plataforma',
            'iesAlias': '107_1'
        }
        response = self.send_request(
            'POST',
            f'{self.URL_API}/{self.CLIENT_AUTH}/signin/tenants/{self.institution.lower()}',
            json=payload
        )
        if response.ok:
            return response.json()

        return response

    def persist_access_token(self, access_token):
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Authorization': access_token
        })
        payload = {
            'roleAlias': 'student',
            'applicationAlias': 'plataforma',
            'tenantAlias': f'{self.institution.lower()}',
            'iesAlias': '107_1'
        }
        response = self.send_request(
            'PUT',
            f'{self.URL_API}/{self.CLIENT_AUTH}/role/assume',
            json=payload
        )
        if response.ok:
            return response.json()

        return response

    def get_messages(self, page=1, items_per_page=15):
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'Authorization': self.access_token
        })
        payload = {
            'directory': 'inbox',
            'page': page,
            'perPage': items_per_page
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/v1/message/messages',
            params=payload
        )
        if response.ok:
            return response.json()

        return response

    def get_notices(self, page=1, items_per_page=15):
        """Retrieve the notices for the user."""
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'Authorization': self.access_token
        })
        payload = {
            'page': page,
            'perPage': items_per_page,
            'orderBy': 'postedAt:desc',
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/academic/notices-board',
            params=payload
        )
        if response.ok:
            return response.json()

        return response

    def check_me(self, access_token):
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'Authorization': access_token
        })
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.USERS_INFO}/me'
        )
        if response.ok:
            return response.json()

        return response

    def get_me(self):
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'Authorization': self.access_token
        })
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.USERS_INFO}/me'
        )
        if response.ok:
            return response.json()

        return response

    def get_periods(self):
        """Retrieve the academic periods for the user."""
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'Authorization': self.access_token
        })
        payload = {
            'academicMainTypeName': 'course',
            'state': 'all'
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/academic/courses/period/me',
            params=payload
        )
        if response.ok:
            return response.json()

        return response

    def get_my_courses(self, state="all", period=11903, page=1, items_per_page=20):
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'Authorization': self.access_token
        })
        payload = {
            'state': state,
            'period': period,
            'page': page,
            'limit': items_per_page,
            'sort': 'asc',
            'sortBy': 'name',
            'type': 'courses'
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/academic/courses/me',
            params=payload
        )
        if response.ok:
            return response.json()

        return response

    def get_contents(self, course_id):
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'Authorization': self.access_token
        })
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V2}/content/academics-main/{course_id}/contents'
        )
        if response.ok:
            return response.json()

        return response

    def get_exercises(self, course_id, topic_id):
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'authorization': self.access_token
        })
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V2}/content/academics-main/{course_id}/topics/{topic_id}'
        )
        if response.ok:
            return response.json()

        return response

    def get_grades(self, course_id):
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'authorization': self.access_token
        })
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/grades/me/course/{course_id}'
        )
        if response.ok:
            return response.json()

        return response

    def get_appointment_type(self):
        """Retrieve the appointments for the user."""
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'Authorization': self.access_token
        })
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/calendar/appointment/type',
        )
        if response.ok:
            return response.json()

        return response

    def get_calendar(self, start_date, end_date):
        """Retrieve the academic calendar for a specific course."""
        self.headers.update({
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'authorization': self.access_token
        })
        payload = {
            'appointmentCategory': '1,5',
            'startDate': start_date,
            'endDate': end_date
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/calendar/appointment',
            params=payload
        )
        if response.ok:
            return response.json()

        return response
