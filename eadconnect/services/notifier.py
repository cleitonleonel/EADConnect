import os
import json
import time
import schedule
import asyncio
import logging
from telethon import TelegramClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GradeMonitor:
    """
    Uma classe para monitorar alterações nas notas de um portal acadêmico
    e enviar notificações via Telegram.
    """

    def __init__(
            self,
            ead_session,
            api_id: int,
            api_hash: str,
            recipient: str,
            session_name: str = 'monitor_notas_session',
            cache_file: str = 'cache_notas.json',
            bot_token: str = None
    ):
        """
        Inicializa o monitor de notas.

        Args:
            ead_session: A sessão autenticada da API da faculdade.
            api_id (int): O seu API ID do Telegram.
            api_hash (str): O seu API Hash do Telegram.
            recipient (str): O destino das mensagens ('me', '@username', ou ID do chat).
            session_name (str, optional): Nome do arquivo de sessão do Telethon.
            cache_file (str, optional): Nome do arquivo para o cache de notas.
            bot_token (str, optional): Token do bot do Telegram (se necessário).
        """
        self.ead_session = ead_session
        self.chat_recipient = recipient
        self.arquivo_cache = cache_file
        self.bot_token = bot_token
        self.check_interval = 2  # Intervalo de verificação em minutos

        # Inicializa o cliente Telethon
        self.client = TelegramClient(session_name, api_id, api_hash)

    def _buscar_notas_api(self):
        """
        Busca as notas mais recentes da API da faculdade.
        Este é um método "privado" da classe.
        """
        logger.info("Buscando dados do perfil...")
        try:
            profile = self.ead_session.get_me()
            user = profile.get('user', {})
            logger.info(f"👤 Perfil: {user.get('name', 'N/A')} ({user.get('email', 'N/A')})")
            logger.info("🔄 Extraindo dados dos cursos...")

            my_courses = self.ead_session.get_my_courses()
            actual_courses = [
                course for course in my_courses.get('courses', []) if course.get('status') == 'isActual'
            ]

            if not actual_courses:
                logger.info("Nenhum curso atual encontrado.")
                return []

            grades_actual_list = []
            logger.info("🔄 Extraindo dados das notas...")
            for actual_course in actual_courses:
                course_name = actual_course.get('name', 'Disciplina Desconhecida').split(' (')[0]
                my_grades = self.ead_session.get_grades(course_id=actual_course['id'])
                final_grade = my_grades.get('finalGrade', {})
                grade_value = final_grade.get('value', 'N/A')

                grade_dict = {
                    "disciplina": course_name,
                    "nota": grade_value
                }
                grades_actual_list.append(grade_dict)
                time.sleep(2)  # Mantém o delay para não sobrecarregar a API

            return grades_actual_list

        except Exception as e:
            logger.info(f"❌ Erro ao buscar notas da API: {e}")
            return None

    def _carregar_cache(self):
        """Carrega as notas do cache local (arquivo JSON)."""
        if not os.path.exists(self.arquivo_cache):
            return {}
        try:
            with open(self.arquivo_cache, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.info(f"⚠️ Erro ao carregar o cache: {e}")
            return {}

    def _salvar_cache(self, notas):
        """Salva as notas mais recentes no cache local."""
        try:
            with open(self.arquivo_cache, 'w', encoding='utf-8') as f:
                json.dump(notas, f, ensure_ascii=False, indent=4)
        except IOError as e:
            logger.info(f"❌ Erro ao salvar o cache: {e}")

    async def _enviar_notificacao(self, disciplina, nota_antiga, nota_nova):
        """Envia uma mensagem formatada para o Telegram."""
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
            logger.info(f"✅ Notificação enviada para a disciplina: {disciplina}")
        except Exception as e:
            logger.info(f"❌ Falha ao enviar notificação: {e}")

    async def _verificar_e_notificar(self):
        """Compara notas atuais com o cache e notifica se houver mudança."""
        logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando verificação de notas...")

        notas_atuais_lista = self._buscar_notas_api()
        if notas_atuais_lista is None:
            logger.info("Verificação abortada devido a erro na API.")
            return

        notas_atuais_dict = {item['disciplina']: item['nota'] for item in notas_atuais_lista}
        notas_cache = self._carregar_cache()

        tasks_notificacao = []
        houve_mudanca = False

        for disciplina, nota_atual in notas_atuais_dict.items():
            nota_cache = notas_cache.get(disciplina, 0)

            if nota_cache != nota_atual:
                logger.info(f"🔄 Mudança detectada em '{disciplina}': de '{nota_cache}' para '{nota_atual}'")
                task = self._enviar_notificacao(disciplina, nota_cache, nota_atual)
                tasks_notificacao.append(task)
                houve_mudanca = True

        if tasks_notificacao:
            await asyncio.gather(*tasks_notificacao)

        if houve_mudanca:
            logger.info("💾 Atualizando o cache de notas...")
            self._salvar_cache(notas_atuais_dict)
        else:
            logger.info("👍 Nenhuma alteração nas notas.")
            response_message = await self.client.send_message(
                self.chat_recipient,
                message="👍 Nenhuma alteração nas notas.",
                parse_mode='markdown'
            )
            await asyncio.sleep(30)
            await self.client.delete_messages(
                self.chat_recipient,
                [response_message.id]
            )

    async def run(self):
        """
        Inicia a conexão com o Telegram e agenda a verificação periódica.
        Este é o método principal para iniciar o monitor.
        """
        try:
            logger.info(self.bot_token)
            await self.client.start(bot_token=self.bot_token)
            logger.info("✅ Cliente Telethon conectado. Monitor de notas iniciado.")

            await self._verificar_e_notificar()

            # Agenda a tarefa. O lambda garante que a corrotina seja agendada no loop de eventos
            schedule.every(self.check_interval).minutes.do(
                lambda: asyncio.create_task(self._verificar_e_notificar())
            )

            logger.info(f"🗓️ Verificação agendada a cada {self.check_interval} minutos. Pressione Ctrl+C para sair.")

            while True:
                schedule.run_pending()
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("\n🛑 Monitor encerrado pelo usuário.")
        except Exception as e:
            logger.info(f"❌ Ocorreu um erro crítico: {e}")
        finally:
            if self.client.is_connected():
                logger.info("🔌 Desconectando o cliente Telethon...")
                await self.client.disconnect()
                logger.info("Cliente desconectado.")


def start_monitor(ead_session, settings):
    """Função principal para configurar e rodar o monitor."""

    # Crie uma instância do monitor
    monitor = GradeMonitor(
        ead_session=ead_session,
        api_id=settings.get('telegram', {}).get('api_id'),
        api_hash=settings.get('telegram', {}).get('api_hash'),
        recipient=settings.get('telegram', {}).get('recipient_id'),
        session_name=settings.get('telegram', {}).get('session_name'),
        bot_token=settings.get('telegram', {}).get('bot_token')
    )
    monitor.check_interval = settings.get('interval', 2)  # Intervalo de verificação em horas

    try:
        # Execute o monitor
        asyncio.run(monitor.run())
    except KeyboardInterrupt:
        logging.info(
            'Bot interrupted by user.\n'
            'Disconnecting...'
        )
