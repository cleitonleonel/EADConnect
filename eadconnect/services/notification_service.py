import os
import json
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional
from telethon import TelegramClient
from eadconnect.client import EducationAPI

# Configuração de logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GradeMonitor:
    """
    Monitor de notas que verifica periodicamente as alterações no portal acadêmico
    e envia notificações via Telegram em caso de mudanças.
    """

    def __init__(
            self,
            ead_session: EducationAPI,
            api_id: int,
            api_hash: str,
            recipient: str,
            session_name: str = 'monitor_notas_session',
            cache_file: str = 'cache_notas.json',
            bot_token: Optional[str] = None
    ) -> None:
        """
        Inicializa o monitor de notas.

        Args:
            ead_session (EducationAPI): Sessão autenticada da API educacional.
            api_id (int): API ID do Telegram (obtido em my.telegram.org).
            api_hash (str): API Hash do Telegram.
            recipient (str): Destinatário (username, chat ID ou 'me').
            session_name (str): Nome do arquivo de sessão do Telethon.
            cache_file (str): Nome do arquivo JSON para cache local das notas.
            bot_token (Optional[str]): Token do bot do Telegram, se usado via bot.
        """
        self.ead_session: EducationAPI = ead_session
        self.chat_recipient: str = recipient
        self.arquivo_cache: str = cache_file
        self.bot_token: Optional[str] = bot_token
        self.check_interval: int = 2  # Intervalo padrão em minutos

        # Inicializa o cliente Telethon
        self.client: TelegramClient = TelegramClient(session_name, api_id, api_hash)

    def _buscar_notas_api(self) -> Optional[List[Dict[str, Any]]]:
        """
        Busca as notas atuais de todas as disciplinas ativas via API.

        Retorna:
            Optional[List[Dict[str, Any]]]: Lista de notas ou None se houver erro.
        """
        logger.info("Buscando dados do perfil...")
        try:
            profile = self.ead_session.get_me()
            if not isinstance(profile, dict):
                return None
                
            user = profile.get('user', {})
            logger.info(f"👤 Perfil: {user.get('name', 'N/A')} ({user.get('email', 'N/A')})")
            
            logger.info("🔄 Extraindo dados dos cursos...")
            my_courses = self.ead_session.get_my_courses()
            if not isinstance(my_courses, dict):
                return None

            actual_courses = [
                course for course in my_courses.get('courses', []) 
                if course.get('status') == 'isActual'
            ]

            if not actual_courses:
                logger.info("Nenhum curso atual encontrado.")
                return []

            grades_actual_list: List[Dict[str, Any]] = []
            logger.info("🔄 Extraindo dados das notas...")
            for actual_course in actual_courses:
                course_name = actual_course.get('name', 'Disciplina Desconhecida').split(' (')[0]
                my_grades = self.ead_session.get_grades(course_id=actual_course['id'])
                
                if isinstance(my_grades, dict):
                    final_grade = my_grades.get('finalGrade', {})
                    grade_value = final_grade.get('value', 'N/A')

                    grades_actual_list.append({
                        "disciplina": course_name,
                        "nota": grade_value
                    })
                
                time.sleep(2)  # Delay para evitar rate limiting

            return grades_actual_list

        except Exception as e:
            logger.error(f"❌ Erro ao buscar notas da API: {e}")
            return None

    def _carregar_cache(self) -> Dict[str, Any]:
        """
        Carrega o estado anterior das notas do arquivo de cache.

        Retorna:
            Dict[str, Any]: Mapeamento de disciplina para nota.
        """
        if not os.path.exists(self.arquivo_cache):
            return {}
        try:
            with open(self.arquivo_cache, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"⚠️ Erro ao carregar o cache: {e}")
            return {}

    def _salvar_cache(self, notas: Dict[str, Any]) -> None:
        """
        Salva o estado atual das notas no arquivo de cache.

        Args:
            notas (Dict[str, Any]): Dicionário de notas a ser persistido.
        """
        try:
            with open(self.arquivo_cache, 'w', encoding='utf-8') as f:
                json.dump(notas, f, ensure_ascii=False, indent=4)
        except IOError as e:
            logger.error(f"❌ Erro ao salvar o cache: {e}")

    async def _enviar_notificacao(self, disciplina: str, nota_antiga: Any, nota_nova: Any) -> None:
        """
        Envia uma notificação formatada para o Telegram informando a mudança de nota.

        Args:
            disciplina (str): Nome da disciplina.
            nota_antiga (Any): Valor da nota anterior no cache.
            nota_nova (Any): Novo valor da nota obtido da API.
        """
        nota_antiga_str = str(nota_antiga) if nota_antiga is not None else "N/A"
        mensagem = (
            f"📢 **Nova nota disponível!** 📢\n\n"
            f"📄 **Disciplina:** {disciplina}\n"
            f"📊 **Nota Anterior:** `{nota_antiga_str}`\n"
            f"✅ **Nova Nota:** `{nota_nova}`\n\n"
            f"Boa sorte! 🍀"
        )
        try:
            await self.client.send_message(
                self.chat_recipient,
                message=mensagem,
                parse_mode='markdown'
            )
            logger.info(f"✅ Notificação enviada para: {disciplina}")
        except Exception as e:
            logger.error(f"❌ Falha ao enviar notificação: {e}")

    async def _verificar_e_notificar(self) -> None:
        """
        Lógica central de comparação: busca notas da API, compara com cache e notifica mudanças.

        O cache é atualizado por disciplina imediatamente após cada notificação bem-sucedida,
        evitando re-notificações em caso de falha parcial de I/O ao final do ciclo.
        """
        logger.info("Iniciando verificação de notas...")

        notas_atuais_lista = await asyncio.to_thread(self._buscar_notas_api)
        if notas_atuais_lista is None:
            logger.warning("Verificação abortada devido a erro na API.")
            return

        notas_atuais_dict = {item['disciplina']: item['nota'] for item in notas_atuais_lista}
        notas_cache = self._carregar_cache()

        houve_mudanca = False

        for disciplina, nota_atual in notas_atuais_dict.items():
            nota_cache = notas_cache.get(disciplina)

            # Notifica apenas se houver mudança real de valor
            if nota_cache != nota_atual:
                logger.info(f"🔄 Mudança em '{disciplina}': '{nota_cache}' -> '{nota_atual}'")
                await self._enviar_notificacao(disciplina, nota_cache, nota_atual)

                # Atualiza o cache desta disciplina imediatamente após a notificação,
                # evitando duplicação caso o processo seja interrompido no meio do ciclo.
                notas_cache[disciplina] = nota_atual
                self._salvar_cache(notas_cache)
                houve_mudanca = True

        if not houve_mudanca:
            logger.info("👍 Sem alterações.")

    async def run(self) -> None:
        """
        Inicia a conexão com o Telegram e o loop de monitoramento.

        Usa asyncio.sleep em vez de `schedule` para garantir execução sequencial:
        cada ciclo de verificação sempre termina antes do próximo iniciar,
        eliminando race conditions e o acúmulo de jobs duplicados no scheduler global.
        """
        try:
            await self.client.start(bot_token=self.bot_token)
            logger.info("✅ Monitor iniciado com sucesso.")

            while True:
                await self._verificar_e_notificar()
                logger.info(
                    f"⏳ Aguardando {self.check_interval} minuto(s) para próxima verificação..."
                )
                await asyncio.sleep(self.check_interval * 60)

        except KeyboardInterrupt:
            logger.info("\n🛑 Monitor parado pelo usuário.")
        except Exception as e:
            logger.error(f"❌ Erro crítico no monitor: {e}")
        finally:
            if self.client.is_connected():
                logger.info("🔌 Desconectando do Telegram...")
                await self.client.disconnect()


def start_monitor(ead_session: EducationAPI, settings: Dict[str, Any]) -> None:
    """
    Função de conveniência para instanciar e rodar o GradeMonitor.

    Args:
        ead_session (EducationAPI): Sessão autenticada.
        settings (Dict[str, Any]): Dicionário de configurações (Telegram, intervalo, etc).
    """
    tg_config = settings.get('telegram', {})
    monitor = GradeMonitor(
        ead_session=ead_session,
        api_id=tg_config.get('api_id', 0),
        api_hash=tg_config.get('api_hash', ''),
        recipient=tg_config.get('recipient_id', 'me'),
        session_name=tg_config.get('session_name', 'monitor_notas_session'),
        bot_token=tg_config.get('bot_token')
    )
    monitor.check_interval = settings.get('interval', 2)

    try:
        asyncio.run(monitor.run())
    except KeyboardInterrupt:
        logger.info('Bot interrompido.')
