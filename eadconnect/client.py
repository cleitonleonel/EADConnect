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

    def progress(self, course_id: int, topic_id: int) -> bool:
        """
        Marca o progresso de um tópico como concluído, permitindo o avanço para o próximo conteúdo.
        Necessário o app_access_token para autenticação.
        Args:
            course_id (int): ID da disciplina.
            topic_id (int): ID do subtopico
        Retorna:
            bollean : Retorno da API indicando sucesso ou falha da operação.
        """
        payload = {}
        headers = self._get_headers(auth_token=self.app_access_token)
        response = self.send_request(
            'POST',
            f'{self.URL_API}/{self.PLATFORM_V2}/content/academics-main/{course_id}/topics/{topic_id}/progress',
            json=payload,
            headers=headers
        )
        if response.ok:
            return True

        return False

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

"""
curl 'https://api.plataforma.grupoa.education/v2/plataforma/content/academics-main/3902914/topics/61337315' \
  -H 'accept: application/json' \
  -H 'accept-language: pt-BR' \
  -H 'authorization: 559f2afa-f32e-4ba3-a069-991128b96e57' \
  -H 'cache-control: no-cache' \
  -H 'dnt: 1' \
  -H 'origin: https://faesa.grupoa.education' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://faesa.grupoa.education/' \
  -H 'sec-ch-ua: "Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36' \
  -H 'x-notice-expired-at: 177860463876110000000' \
  -H 'x-notice-show-modal: false' \
  -H 'x-notice-signature: 28b73d742cd68f910d9f8256d938ced7db09b18f0301d458f44d578ba7d15422' \
  -H 'x-user-timezone: America/Sao_Paulo'
"""

"""
curl 'https://api.plataforma.grupoa.education/v2/plataforma/content/academics-main/3902914/topics/61337385/quizzes' \
  -H 'accept: application/json' \
  -H 'accept-language: pt-BR' \
  -H 'authorization: 559f2afa-f32e-4ba3-a069-991128b96e57' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'dnt: 1' \
  -H 'origin: https://faesa.grupoa.education' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://faesa.grupoa.education/' \
  -H 'sec-ch-ua: "Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36' \
  -H 'x-user-timezone: America/Sao_Paulo' \
  --data-raw '{"questionId":25038913,"optionId":122117550}'
"""

"""
A cada envio o servidor retorna o estado atualizado da tentativa, incluindo as respostas e o progresso do quiz.
{
    "attempts": [
        {
            "attemptId": 32611002,
            "attemptNumber": 1,
            "createdAt": "2026-05-12 14:36:57.585965",
            "finishedAt": null,
            "correctionId": null,
            "grade": 0,
            "reason": null,
            "isAttemptValid": null,
            "hits": 0,
            "answers": [
                {
                    "quizAnswerId": 179636150,
                    "questionId": 25038909,
                    "optionId": 122117666,
                    "answeredAt": "2026-05-12 14:43:28.694463",
                    "cancelAt": null
                },
                {
                    "quizAnswerId": 179639762,
                    "questionId": 25038910,
                    "optionId": 122117547,
                    "answeredAt": "2026-05-12 14:45:57.938286",
                    "cancelAt": null
                },
                {
                    "quizAnswerId": 179640726,
                    "questionId": 25038911,
                    "optionId": 122117488,
                    "answeredAt": "2026-05-12 14:48:59.198946",
                    "cancelAt": null
                },
                {
                    "quizAnswerId": 179641104,
                    "questionId": 25038912,
                    "optionId": 122117609,
                    "answeredAt": "2026-05-12 14:50:10.956606"
                }
            ]
        }
    ]
}
"""

"""
curl 'https://api.plataforma.grupoa.education/v2/plataforma/content/academics-main/3902914/topics/61337385/quizzes/attempts' \
  -H 'accept: application/json' \
  -H 'accept-language: pt-BR' \
  -H 'authorization: 559f2afa-f32e-4ba3-a069-991128b96e57' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'dnt: 1' \
  -H 'origin: https://faesa.grupoa.education' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://faesa.grupoa.education/' \
  -H 'sec-ch-ua: "Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36' \
  -H 'x-user-timezone: America/Sao_Paulo' \
  --data-raw '{"attemptId":32611002}'
"""

"""
A fim das respostas é enviado o id da tentativa e o servidor retorna o resultado da correção, incluindo a nota final e o feedback de cada questão.

{
    "topicId": 61337385,
    "quizTypeId": 1,
    "hasRetries": false,
    "hasDeadline": true,
    "instructions": "<p></p>",
    "numberRetries": 1,
    "retryTypeId": 1,
    "hasFeedback": false,
    "feedbackAt": null,
    "isForShuffle": false,
    "enrollmentQuizAttemptId": 32611002,
    "isCompleted": true,
    "enrollmentQuizId": 29519618,
    "hasGrade": false,
    "isForAutomaticallyDistributeGrade": false,
    "roundingPrecision": 2,
    "hasReleasedFeedback": true,
    "questions": [
        {
            "id": 25038909,
            "questionTypeId": 1,
            "enunciated": "<div class=\"question\"><p></p><p><strong>Ambientes integrados de desenvolvimento ajudam os programadores, disponibilizando funções como autocompletar e indicações de problema na sintaxe. </strong><br></p><p><strong>Entre os itens a seguir, quais são exemplos de IDEs?</strong></p><p></p></div>",
            "feedbackTypeId": 2,
            "feedback": "<p></p>",
            "hasFileUpload": false,
            "grade": 0,
            "options": [
                {
                    "id": 122117486,
                    "text": "<div class=\"question-option\"><p>Atom, iOS, IntelliJ e Android Studio.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>Atom, Xcode, IntelliJ e Android Studio são ambientes integrados de desenvolvimento, ou IDEs. iOS é um sistema operacional. Kotlin, TypeScript e Swift são linguagens de programação.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117546,
                    "text": "<div class=\"question-option\"><p> Atom, Xcode, Kotlin e Android Studio.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>Atom, Xcode, IntelliJ e Android Studio são ambientes integrados de desenvolvimento, ou IDEs. iOS é um sistema operacional. Kotlin, TypeScript e Swift são linguagens de programação.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117606,
                    "text": "<div class=\"question-option\"><p>Atom, Xcode, IntelliJ e TypeScript.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>Atom, Xcode, IntelliJ e Android Studio são ambientes integrados de desenvolvimento, ou IDEs. iOS é um sistema operacional. Kotlin, TypeScript e Swift são linguagens de programação.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117666,
                    "text": "<div class=\"question-option\"><p>Atom, Xcode, IntelliJ e Android Studio.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>Atom, Xcode, IntelliJ e Android Studio são ambientes integrados de desenvolvimento, ou IDEs. iOS é um sistema operacional. Kotlin, TypeScript e Swift são linguagens de programação.</p></div>",
                    "isCorrect": true
                },
                {
                    "id": 122117726,
                    "text": "<div class=\"question-option\"><p>Atom, Swift, IntelliJ e Android Studio.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>Atom, Xcode, IntelliJ e Android Studio são ambientes integrados de desenvolvimento, ou IDEs. iOS é um sistema operacional. Kotlin, TypeScript e Swift são linguagens de programação.</p></div>",
                    "isCorrect": false
                }
            ]
        },
        {
            "id": 25038910,
            "questionTypeId": 1,
            "enunciated": "<div class=\"question\"><p></p><p><strong>Duas abordagens se destacam quando se fala em desenvolvimento para aplicativos móveis: o desenvolvimento nativo e o híbrido.</strong></p><p><strong>Quanto ao desenvolvimento nativo, é correto afirmar que:</strong></p><p></p></div>",
            "feedbackTypeId": 2,
            "feedback": "<p></p>",
            "hasFileUpload": false,
            "grade": 0,
            "options": [
                {
                    "id": 122117607,
                    "text": "<div class=\"question-option\"><p>aplicações são desenvolvidas para rodar em qualquer sistema operacional.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>No desenvolvimento nativo, as aplicações são desenvolvidas para um sistema operacional específico, portanto, não rodam em qualquer sistema operacional. Além disso, elas podem acessar diretamente o GPS e o acelerômetro. Já no desenvolvimento híbrido, as aplicações utilizam uma <em>webview</em>, que abre um navegador para exibir conteúdo ao usuário.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117667,
                    "text": "<div class=\"question-option\"><p>o desempenho é inferior se comparado ao desenvolvimento híbrido.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>No desenvolvimento nativo, as aplicações são desenvolvidas para um sistema operacional específico, portanto, não rodam em qualquer sistema operacional. Além disso, elas podem acessar diretamente o GPS e o acelerômetro. Já no desenvolvimento híbrido, as aplicações utilizam uma <em>webview</em>, que abre um navegador para exibir conteúdo ao usuário.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117727,
                    "text": "<div class=\"question-option\"><p>utilizam uma <em>webview</em>, a qual abre um navegador para exibir conteúdo ao usuário.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>No desenvolvimento nativo, as aplicações são desenvolvidas para um sistema operacional específico, portanto, não rodam em qualquer sistema operacional. Além disso, elas podem acessar diretamente o GPS e o acelerômetro. Já no desenvolvimento híbrido, as aplicações utilizam uma <em>webview</em>, que abre um navegador para exibir conteúdo ao usuário.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117487,
                    "text": "<div class=\"question-option\"><p>as aplicações não podem acessar diretamente o GPS e o acelerômetro.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>No desenvolvimento nativo, as aplicações são desenvolvidas para um sistema operacional específico, portanto, não rodam em qualquer sistema operacional. Além disso, elas podem acessar diretamente o GPS e o acelerômetro. Já no desenvolvimento híbrido, as aplicações utilizam uma <em>webview</em>, que abre um navegador para exibir conteúdo ao usuário.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117547,
                    "text": "<div class=\"question-option\"><p>as aplicações são desenvolvidas para um sistema operacional específico.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>No desenvolvimento nativo, as aplicações são desenvolvidas para um sistema operacional específico, portanto, não rodam em qualquer sistema operacional. Além disso, elas podem acessar diretamente o GPS e o acelerômetro. Já no desenvolvimento híbrido, as aplicações utilizam uma <em>webview</em>, que abre um navegador para exibir conteúdo ao usuário.</p></div>",
                    "isCorrect": true
                }
            ]
        },
        {
            "id": 25038911,
            "questionTypeId": 1,
            "enunciated": "<div class=\"question\"><p></p><p><strong>Algumas linguagens de programação têm características mais específicas. Java e Kotlin, por exemplo, são linguagens estaticamente tipadas. </strong><br></p><p><strong>O que isso significa?</strong></p><p></p></div>",
            "feedbackTypeId": 2,
            "feedback": "<p></p>",
            "hasFileUpload": false,
            "grade": 0,
            "options": [
                {
                    "id": 122117548,
                    "text": "<div class=\"question-option\"><p>A declaração dos tipos de dados é opcional, não interferindo na compilação do código.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>A declaração dos tipos de dados é obrigatória e, caso não seja definida, o código pode não compilar. As categorias de dados a serem armazenados precisam ser explicitamente declaradas, e os tipos precisam ser explícitos. Existe uma quantidade relativamente grande de tipos possíveis, como os textuais e os numéricos, por exemplo. As linguagens que contêm apenas um tipo genérico, ou nenhum tipo de dados, são mais antigas, como o Fortran.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117488,
                    "text": "<div class=\"question-option\"><p>As categorias de dados a serem armazenados precisam ser explicitamente declaradas.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>A declaração dos tipos de dados é obrigatória e, caso não seja definida, o código pode não compilar. As categorias de dados a serem armazenados precisam ser explicitamente declaradas, e os tipos precisam ser explícitos. Existe uma quantidade relativamente grande de tipos possíveis, como os textuais e os numéricos, por exemplo. As linguagens que contêm apenas um tipo genérico, ou nenhum tipo de dados, são mais antigas, como o Fortran.</p></div>",
                    "isCorrect": true
                },
                {
                    "id": 122117608,
                    "text": "<div class=\"question-option\"><p>Os tipos de dados são implícitos, não sendo permitida a declaração estática.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>A declaração dos tipos de dados é obrigatória e, caso não seja definida, o código pode não compilar. As categorias de dados a serem armazenados precisam ser explicitamente declaradas, e os tipos precisam ser explícitos. Existe uma quantidade relativamente grande de tipos possíveis, como os textuais e os numéricos, por exemplo. As linguagens que contêm apenas um tipo genérico, ou nenhum tipo de dados, são mais antigas, como o Fortran.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117668,
                    "text": "<div class=\"question-option\"><p>Essas linguagens só trabalham com dados dos tipos textuais e numéricos.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>A declaração dos tipos de dados é obrigatória e, caso não seja definida, o código pode não compilar. As categorias de dados a serem armazenados precisam ser explicitamente declaradas, e os tipos precisam ser explícitos. Existe uma quantidade relativamente grande de tipos possíveis, como os textuais e os numéricos, por exemplo. As linguagens que contêm apenas um tipo genérico, ou nenhum tipo de dados, são mais antigas, como o Fortran.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117728,
                    "text": "<div class=\"question-option\"><p>Existe apenas um tipo genérico.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>A declaração dos tipos de dados é obrigatória e, caso não seja definida, o código pode não compilar. As categorias de dados a serem armazenados precisam ser explicitamente declaradas, e os tipos precisam ser explícitos. Existe uma quantidade relativamente grande de tipos possíveis, como os textuais e os numéricos, por exemplo. As linguagens que contêm apenas um tipo genérico, ou nenhum tipo de dados, são mais antigas, como o Fortran.</p></div>",
                    "isCorrect": false
                }
            ]
        },
        {
            "id": 25038912,
            "questionTypeId": 1,
            "enunciated": "<div class=\"question\"><p></p><p><strong>Algumas linguagens de programação são evoluções, outras adicionam funcionalidades, enquanto outras não apresentam muito em comum. </strong></p><p><strong>Qual a correlação entre o Java e o JavaScript?</strong></p><p></p></div>",
            "feedbackTypeId": 2,
            "feedback": "<p></p>",
            "hasFileUpload": false,
            "grade": 0,
            "options": [
                {
                    "id": 122117489,
                    "text": "<div class=\"question-option\"><p>O JavaScript é uma evolução do Java para aplicativos móveis.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>Embora ambas sejam linguagens de programação orientadas a objetos, JavaScript e Java não são correlacionadas, inexistindo a relação de superconjunto entre elas. Em relação ao Android, Java é mais voltado para desenvolvimento nativo, sendo também uma linguagem mais antiga que JavaScript.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117549,
                    "text": "<div class=\"question-option\"><p>Ambas são linguagens que possibilitam o desenvolvimento de aplicativos híbridos.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>Embora ambas sejam linguagens de programação orientadas a objetos, JavaScript e Java não são correlacionadas, inexistindo a relação de superconjunto entre elas. Em relação ao Android, Java é mais voltado para desenvolvimento nativo, sendo também uma linguagem mais antiga que JavaScript.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117609,
                    "text": "<div class=\"question-option\"><p>Ambas são linguagens de programação orientadas a objetos.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>Embora ambas sejam linguagens de programação orientadas a objetos, JavaScript e Java não são correlacionadas, inexistindo a relação de superconjunto entre elas. Em relação ao Android, Java é mais voltado para desenvolvimento nativo, sendo também uma linguagem mais antiga que JavaScript.</p></div>",
                    "isCorrect": true
                },
                {
                    "id": 122117669,
                    "text": "<div class=\"question-option\"><p>JavaScript é um superconjunto de Java, agregando funções ao Java.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>Embora ambas sejam linguagens de programação orientadas a objetos, JavaScript e Java não são correlacionadas, inexistindo a relação de superconjunto entre elas. Em relação ao Android, Java é mais voltado para desenvolvimento nativo, sendo também uma linguagem mais antiga que JavaScript.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117729,
                    "text": "<div class=\"question-option\"><p>Javascript é uma linguagem mais antiga e mais utilizada.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>Embora ambas sejam linguagens de programação orientadas a objetos, JavaScript e Java não são correlacionadas, inexistindo a relação de superconjunto entre elas. Em relação ao Android, Java é mais voltado para desenvolvimento nativo, sendo também uma linguagem mais antiga que JavaScript.</p></div>",
                    "isCorrect": false
                }
            ]
        },
        {
            "id": 25038913,
            "questionTypeId": 1,
            "enunciated": "<div class=\"question\"><p></p><p><strong>Diversos<em> plug-ins</em> e <em>frameworks</em> podem ser utilizados para apoiar o desenvolvimento para aplicativos móveis. </strong><br></p><p><strong>Qual deles pode ser utilizado para facilitar a instalação de outras bibliotecas e componentes?</strong></p><p></p></div>",
            "feedbackTypeId": 2,
            "feedback": "<p></p>",
            "hasFileUpload": false,
            "grade": 0,
            "options": [
                {
                    "id": 122117490,
                    "text": "<div class=\"question-option\"><p>Node.js.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>O Npm (Node Package Manager) é utilizado para ajudar na instalação de pacotes para o Node.js. O Node é um interpretador de JavaScript; e o Cordova, o Ionic e o Angular são <em>frameworks</em>.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117550,
                    "text": "<div class=\"question-option\"><p>Npm.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>O Npm (Node Package Manager) é utilizado para ajudar na instalação de pacotes para o Node.js. O Node é um interpretador de JavaScript; e o Cordova, o Ionic e o Angular são <em>frameworks</em>.</p></div>",
                    "isCorrect": true
                },
                {
                    "id": 122117610,
                    "text": "<div class=\"question-option\"><p>Apache Cordova.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>O Npm (Node Package Manager) é utilizado para ajudar na instalação de pacotes para o Node.js. O Node é um interpretador de JavaScript; e o Cordova, o Ionic e o Angular são <em>frameworks</em>.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117670,
                    "text": "<div class=\"question-option\"><p>Ionic.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>O Npm (Node Package Manager) é utilizado para ajudar na instalação de pacotes para o Node.js. O Node é um interpretador de JavaScript; e o Cordova, o Ionic e o Angular são <em>frameworks</em>.</p></div>",
                    "isCorrect": false
                },
                {
                    "id": 122117730,
                    "text": "<div class=\"question-option\"><p>Angular.</p></div>",
                    "feedback": "<div class=\"question-feedback\"><p>O Npm (Node Package Manager) é utilizado para ajudar na instalação de pacotes para o Node.js. O Node é um interpretador de JavaScript; e o Cordova, o Ionic e o Angular são <em>frameworks</em>.</p></div>",
                    "isCorrect": false
                }
            ]
        }
    ],
    "grade": "0.000",
    "attempts": [
        {
            "attemptId": 32611002,
            "attemptNumber": 1,
            "createdAt": "2026-05-12 14:36:57.585965",
            "finishedAt": "2026-05-12 14:51:58.410805",
            "correctionId": null,
            "grade": "0.000",
            "reason": null,
            "isAttemptValid": true,
            "hits": "5",
            "answers": [
                {
                    "quizAnswerId": 179636150,
                    "questionId": 25038909,
                    "optionId": 122117666,
                    "answeredAt": "2026-05-12 14:43:28.694463",
                    "isCorrect": true,
                    "cancelAt": null
                },
                {
                    "quizAnswerId": 179639762,
                    "questionId": 25038910,
                    "optionId": 122117547,
                    "answeredAt": "2026-05-12 14:45:57.938286",
                    "isCorrect": true,
                    "cancelAt": null
                },
                {
                    "quizAnswerId": 179640726,
                    "questionId": 25038911,
                    "optionId": 122117488,
                    "answeredAt": "2026-05-12 14:48:59.198946",
                    "isCorrect": true,
                    "cancelAt": null
                },
                {
                    "quizAnswerId": 179641104,
                    "questionId": 25038912,
                    "optionId": 122117609,
                    "answeredAt": "2026-05-12 14:50:10.956606",
                    "isCorrect": true,
                    "cancelAt": null
                },
                {
                    "quizAnswerId": 179641642,
                    "questionId": 25038913,
                    "optionId": 122117550,
                    "answeredAt": "2026-05-12 14:50:53.257886",
                    "isCorrect": true,
                    "cancelAt": null
                }
            ]
        }
    ],
    "hasCompletedAllAttempts": true
}
"""