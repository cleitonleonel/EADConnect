import os
from typing import Optional, Dict, Any, Union
import requests
from eadconnect.http.navigator import Browser
from eadconnect.endpoints import Endpoints


class EducationAPI(Browser, Endpoints):
    """
    Cliente principal para interação com a API da Plataforma de Educação (Grupo A).
    Fornece métodos para autenticação, consultas acadêmicas, financeiras e obtenção de conteúdo.
    """

    def __init__(
            self,
            institution: str = "faesa",
            username: Optional[str] = None,
            password: Optional[str] = None,
            *args,
            **kwargs
    ) -> None:
        """
        Inicializa a instância da API.

        Args:
            institution (str): Nome da instituição de ensino (ex: 'faesa'). Padrão é 'faesa'.
            username (Optional[str]): Nome de usuário para autenticação.
            password (Optional[str]): Senha para autenticação.
        """
        super().__init__(*args, **kwargs)
        self.institution: str = institution
        self.username: Optional[str] = username
        self.password: Optional[str] = password
        self.access_token: Optional[str] = None
        self.app_access_token: Optional[str] = None
        self.set_headers()

    @property
    def base_url(self) -> str:
        """Obtém a URL base da instituição."""
        return f'https://{self.institution.lower()}.grupoa.education'

    def _get_headers(self, auth_token: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Gera o dicionário de cabeçalhos para uma requisição específica.
        
        Args:
            auth_token (Optional[str]): Token de autorização a ser usado. 
                                      Se não fornecido, usa self.access_token.
            extra_headers (Optional[Dict[str, str]]): Cabeçalhos adicionais.
            
        Retorna:
            Dict[str, str]: Dicionário de cabeçalhos formatado.
        """
        headers = {
            'Referer': f"{self.base_url}/",
            'Accept': 'application/json',
            'Authorization': auth_token or self.access_token
        }
        if extra_headers:
            headers.update(extra_headers)
            
        # Filtra valores None para não enviar cabeçalhos vazios
        return {k: v for k, v in headers.items() if v is not None}

    def login(self) -> Union[Dict[str, Any], requests.Response]:
        """
        Realiza a autenticação inicial com usuário e senha.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Dicionário com dados do token ou a resposta em caso de falha.
        """
        headers = {'Referer': f"{self.base_url}/"}
        payload = {
            'username': self.username,
            'password': self.password,
            'applicationAlias': 'plataforma',
            'iesAlias': '107_1'
        }
        response = self.send_request(
            'POST',
            f'{self.URL_API}/{self.CLIENT_AUTH}/signin/tenants/{self.institution.lower()}',
            json=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def persist_access_token(self, access_token: str) -> Union[Dict[str, Any], requests.Response]:
        """
        Assume a permissão de estudante com o token temporário, gerando o token de acesso persistente.

        Args:
            access_token (str): Token primário obtido no processo de login.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Dados do token de estudante ou resposta de erro.
        """
        headers = self._get_headers(auth_token=access_token)
        payload = {
            'roleAlias': 'student',
            'applicationAlias': 'plataforma',
            'tenantAlias': f'{self.institution.lower()}',
            'iesAlias': '107_1'
        }
        response = self.send_request(
            'PUT',
            f'{self.URL_API}/{self.CLIENT_AUTH}/role/assume',
            json=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_messages(self, page: int = 1, items_per_page: int = 15) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém as mensagens da caixa de entrada do usuário.

        Args:
            page (int): Página atual da consulta.
            items_per_page (int): Quantidade de itens por página.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Dicionário com as mensagens.
        """
        headers = self._get_headers()
        payload = {
            'directory': 'inbox',
            'page': page,
            'perPage': items_per_page
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/v1/message/messages',
            params=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_notices(self, page: int = 1, items_per_page: int = 15) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém os avisos gerais postados para o usuário.

        Args:
            page (int): Página atual da consulta.
            items_per_page (int): Quantidade de itens por página.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Dicionário com os avisos.
        """
        headers = self._get_headers()
        payload = {
            'page': page,
            'perPage': items_per_page,
            'orderBy': 'postedAt:desc',
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/academic/notices-board',
            params=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_notifications(self, page: int = 1, items_per_page: int = 15) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém as notificações de sistema para o usuário.

        Args:
            page (int): Página atual da consulta.
            items_per_page (int): Quantidade de itens por página.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Dicionário com as notificações.
        """
        headers = self._get_headers(extra_headers={'x-api-key': '0vL60rGpwtadmgECP1yj09vGSfNIZ8iCh7Pzzl7e'})
        payload = {
            'deliveryMode': 'application',
            'page': page,
            'perPage': items_per_page
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/v1/notification-service/notifications',
            params=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_notices_board(self, course_id: int = 2326262, page: int = 1, items_per_page: int = 5) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém o quadro de avisos específico de um curso.

        Args:
            course_id (int): ID do curso acadêmico.
            page (int): Página atual da consulta.
            items_per_page (int): Quantidade de itens por página.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Quadro de avisos.
        """
        headers = self._get_headers()
        payload = {
            'isHighlight': True,
            'perPage': items_per_page,
            'page': page,
            'orderBy': 'sequence:asc'
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/academic/courses/{course_id}/notices-board',
            params=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def check_me(self, access_token: str) -> Union[Dict[str, Any], requests.Response]:
        """
        Verifica a validade de um token consultando o perfil do usuário.

        Args:
            access_token (str): Token a ser verificado.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Informações do perfil se válido, erro caso contrário.
        """
        headers = self._get_headers(auth_token=access_token)
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.USERS_INFO}/me',
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_me(self, access_token: Optional[str] = None) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém as informações do perfil do usuário autenticado.

        Args:
            access_token (Optional[str]): Token opcional (se não fornecido, usa o token da instância).

        Retorna:
            Union[Dict[str, Any], requests.Response]: Perfil do usuário.
        """
        headers = self._get_headers(auth_token=access_token)
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.USERS_INFO}/me',
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_periods(self) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém os períodos acadêmicos em que o usuário possui matrícula.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Lista de períodos acadêmicos.
        """
        headers = self._get_headers()
        payload = {
            'academicMainTypeName': 'course',
            'state': 'all'
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/academic/courses/period/me',
            params=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_my_courses(
            self,
            state: str = "all",
            period: int = 11903,
            page: int = 1,
            items_per_page: int = 20
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém a lista de cursos (disciplinas) em que o usuário está matriculado.

        Args:
            state (str): Estado do curso (ex: 'all', 'isActual').
            period (int): ID do período acadêmico.
            page (int): Página da consulta.
            items_per_page (int): Limite de itens por página.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Lista de cursos.
        """
        headers = self._get_headers()
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
            params=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_contents(self, course_id: int) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém a estrutura de conteúdos de uma disciplina (tópicos).

        Args:
            course_id (int): ID da disciplina.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Estrutura do conteúdo do curso.
        """
        headers = self._get_headers()
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V2}/content/academics-main/{course_id}/contents',
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_exercises(self, course_id: int, topic_id: int) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém os exercícios relacionados a um tópico de uma disciplina.

        Args:
            course_id (int): ID da disciplina.
            topic_id (int): ID do tópico.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Dados dos exercícios do tópico.
        """
        headers = self._get_headers()
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V2}/content/academics-main/{course_id}/topics/{topic_id}',
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_file_url(self, course_id: int, topic_id: int) -> Union[Dict[str, Any], requests.Response]:
        """
        Gera e obtém a URL de download (versão de impressão) de um conteúdo de tópico.

        Args:
            course_id (int): ID da disciplina.
            topic_id (int): ID do tópico.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Dados contendo a URL do arquivo para download.
        """
        headers = self._get_headers()
        payload = {
            "primaryColor": "#007cb0",
            "logoUrl": "https://bucket.safea.grupoa.education/ies/107_1/1596072479677_107_1_faesa_logo.png",
            "language": "pt_br"
        }
        response = self.send_request(
            'POST',
            f'{self.URL_API}/{self.PLATFORM_V1}/content/main-content/{course_id}/topic/{topic_id}/print',
            json=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_grades(self, course_id: int) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém as notas do aluno para uma determinada disciplina.

        Args:
            course_id (int): ID da disciplina.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Quadro de notas.
        """
        headers = self._get_headers()
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/grades/me/course/{course_id}',
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_appointment_type(self) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém os tipos de agendamentos/compromissos do calendário acadêmico.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Tipos de compromisso.
        """
        headers = self._get_headers()
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/calendar/appointment/type',
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_calendar(self, start_date: str, end_date: str) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém eventos do calendário acadêmico em um intervalo específico.

        Args:
            start_date (str): Data de início (YYYY-MM-DD).
            end_date (str): Data de fim (YYYY-MM-DD).

        Retorna:
            Union[Dict[str, Any], requests.Response]: Eventos do calendário.
        """
        headers = self._get_headers()
        payload = {
            'appointmentCategory': '1,2,5,6',
            'startDate': start_date,
            'endDate': end_date
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/calendar/appointment',
            params=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def auth_app_launcher(self) -> Union[Dict[str, Any], requests.Response]:
        """
        Autentica e gera um launcher de aplicação (necessário para acesso financeiro e serviços acadêmicos extras).

        Retorna:
            Union[Dict[str, Any], requests.Response]: Dados de redirecionamento contendo o token de aplicação.
        """
        headers = self._get_headers()
        params = {
            'appLauncher': False
        }
        payload = {
            'iesAlias': '107_1',
            'roleAlias': 'student',
            'tenantAlias': f'{self.institution.lower()}',
            'uuid': self.username
        }
        response = self.send_request(
            'POST',
            f'{self.URL_API}/{self.CLIENT_AUTH}/sso/applications/academic-services/url',
            params=params,
            json=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_my_info(self) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém informações complementares de perfil via serviços acadêmicos (BFF), como RA (Registro Acadêmico) e matrículas.
        Necessita do app_access_token pré-configurado.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Informações do aluno.
        """
        headers = self._get_headers(auth_token=self.app_access_token)
        response = self.send_request(
            'GET',
            f'{self.URL_API}/v1/academic-services/bff/my-informations',
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_debts(
            self,
            registration_number: Optional[str] = None,
            status: str = 'pending',
            page: int = 1,
            items_per_page: int = 10
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém os débitos financeiros do aluno.

        Args:
            registration_number (Optional[str]): Registro Acadêmico (RA).
            status (str): Filtro de status (ex: 'pending'). Padrão 'pending'.
            page (int): Página da consulta.
            items_per_page (int): Limite de itens por página.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Lista de débitos.
        """
        headers = self._get_headers(auth_token=self.app_access_token)
        payload = {
            'perPage': items_per_page,
            'page': page,
            'academicRecord': registration_number,
            'filterYear': '',
            'filterPeriod': '',
            'filterType': '',
            'filterStatusType': status,
            'checkfitForAgreement': True,
            'viewSlips': True,
            'order': 'DESC|ASC|ASC|ASC|ASC',
            'sortBy': 'warning_agreement|due_date|debt_number|competency_month|competency_year'
        }
        response = self.send_request(
            'GET',
            f'{self.URL_API}/v1/service-portal/financial/debts',
            params=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_contract_slip(self, contract_id: int) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém os dados do contrato/boleto associado a um débito.

        Args:
            contract_id (int): ID do contrato.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Informações do contrato/boleto.
        """
        headers = self._get_headers(auth_token=self.app_access_token)
        response = self.send_request(
            'GET',
            f'{self.URL_API}/v1/service-portal/financial/debts/{contract_id}',
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_payment_methods(self) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém os métodos de pagamento suportados na instituição.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Lista de métodos de pagamento disponíveis.
        """
        headers = self._get_headers(auth_token=self.app_access_token)
        response = self.send_request(
            'GET',
            f'{self.URL_API}/v1/service-portal/financial/payment/methods',
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def get_payment_settings(self) -> Union[Dict[str, Any], requests.Response]:
        """
        Obtém as configurações de limite, multas, e regras de parcelamento de débitos.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Configurações financeiras.
        """
        headers = self._get_headers(auth_token=self.app_access_token)
        response = self.send_request(
            'GET',
            f'{self.URL_API}/{self.PLATFORM_V1}/service-portal/financial/settings',
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def create_payment(self, registration_number: str, payment_data: dict) -> Union[Dict[str, Any], requests.Response]:
        """
        Cria uma intenção de pagamento (ex: geração de PIX ou cartão de crédito).

        Args:
            registration_number (str): Registro Acadêmico.
            payment_data (dict): Dados detalhados do débito e intenção de pagamento.

        Retorna:
            Union[Dict[str, Any], requests.Response]: Retorno do gerador de pagamento (ex: Chave PIX).
        """
        headers = self._get_headers(auth_token=self.app_access_token)
        payload = payment_data
        params = {
            'academicRecord': registration_number,
            'isAgreement': False
        }
        response = self.send_request(
            'POST',
            f'{self.URL_API}/v1/service-portal/financial/payment/charges/pix',
            params=params,
            json=payload,
            headers=headers
        )
        if response.ok:
            return response.json()

        return response

    def download_topic_file(self, url_file: str, path: str) -> requests.Response:
        """
        Efetua o download e salva um arquivo em disco através de stream.

        Args:
            url_file (str): URL de onde o arquivo deve ser baixado.
            path (str): Diretório local onde o arquivo deve ser salvo.

        Retorna:
            requests.Response: O objeto de resposta da requisição original.
        """
        headers = self._get_headers()

        with self.send_request(method='GET', url=url_file, stream=True, headers=headers) as response:
            response.raise_for_status()

            file_name = url_file.split('/')[-1]

            with open(os.path.join(path, file_name), "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        return response
