from education.http.navigator import Browser
from education.endpoints import Endpoints


class EducationAPI(Browser, Endpoints):

    def __init__(
            self,
            institution: str,
            username: str,
            password: str,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.institution = institution.lower()
        self.username = username
        self.password = password
        self.access_token = None
        self.set_headers()

    @property
    def base_url(self):
        return f'https://{self.institution}.grupoa.education'

    def login(self):
        self.headers['Referer'] = f"{self.base_url}/"
        payload = {
            'username': self.username,
            'password': self.password,
            'applicationAlias': 'plataforma',
            'iesAlias': '107_1'
        }
        response = self.send_request(
            'POST',
            f'{self.URL_API}/{self.CLIENT_AUTH}/signin/tenants/{self.institution}',
            json=payload
        )
        if response.ok:
            return response.json()

        return response

    def persist_access_token(self, access_token):
        self.headers['Authorization'] = access_token
        self.headers['Referer'] = f"{self.base_url}/"
        payload = {
            'roleAlias': 'student',
            'applicationAlias': 'plataforma',
            'tenantAlias': f'{self.institution}',
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
        self.headers['Referer'] = f"{self.base_url}/"
        self.headers['Accept'] = 'application/json'
        self.headers['Authorization'] = self.access_token
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

    def get_my_courses(self, state="all", period=11903, page=1, items_per_page=20):
        self.headers['Referer'] = f"{self.base_url}/"
        self.headers['Accept'] = 'application/json'
        self.headers['Authorization'] = self.access_token
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
            f'{self.URL_API}/{self.PLATFORM_V1}/courses/me',
            params=payload
        )
        if response.ok:
            return response.json()

        return response

    def get_contents(self, course_id):
        self.headers['Referer'] = f"{self.base_url}/"
        self.headers['Accept'] = 'application/json'
        self.headers['Authorization'] = self.access_token
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V2}/{course_id}/contents'
        )
        if response.ok:
            return response.json()

        return response

    def get_exercises(self, course_id, topic_id):
        self.headers['Referer'] = f"{self.base_url}/"
        self.headers['Accept'] = 'application/json'
        self.headers['authorization'] = self.access_token
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V2}/{course_id}/topics/{topic_id}'
        )
        if response.ok:
            return response.json()

        return response
