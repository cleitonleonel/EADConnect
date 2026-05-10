import re
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from eadconnect.client import EducationAPI

logger = logging.getLogger(__name__)


async def exibir_mensagens(client: EducationAPI) -> None:
    """
    Busca as mensagens recentes do usuário e as formata para exibição no console.
    
    Args:
        client (EducationAPI): Instância autenticada do cliente da API.
    """
    notifications = client.get_messages(items_per_page=5)
    conversations = notifications.get('conversations', [])
    messages = [conversation.get('messages', [])[0] for conversation in conversations if conversation.get('messages')]
    
    for message in messages:
        content = message.get('content', '')
        content_text = BeautifulSoup(content, 'html.parser').get_text()
        match = re.search(r'https?://[^\s<>"]+', content_text)
        
        if match:
            link = match.group(0)
            content_text = content_text.replace(link, f'[Link]({link})').strip()

        print(f"📬 Mensagem: {content_text}")
        print(f"📅 Enviada em: {message.get('createdAt', 'Data não disponível')}")
        print(f"👤 De: {message.get('sender', {}).get('name', 'Desconhecido')}")
        print(f"{100 * '='}")


async def exibir_calendario(client: EducationAPI) -> None:
    """
    Obtém e exibe os eventos do calendário acadêmico dentro de um intervalo de datas.
    
    Args:
        client (EducationAPI): Instância autenticada do cliente da API.
    """
    # Exemplo de uso de datas fixas; idealmente pode ser injetado ou obtido via utils
    start_date, end_date = '2025-07-12', '2025-08-31'
    calendar = client.get_calendar(start_date, end_date)
    
    if not calendar:
        logger.warning("Nenhum evento encontrado no calendário.")
        return

    logger.info("📅 Eventos do Calendário Acadêmico:")
    for event in calendar:
        title = event.get('title', 'Sem título')
        start_date_str = event.get('startAt', 'Data não disponível')
        end_date_str = event.get('endAt', 'Data não disponível')
        description = event.get('description', '') or ''
        
        description_text = BeautifulSoup(description, 'html.parser').get_text()
        
        if start_date_str and start_date_str != 'Data não disponível':
            try:
                start_date_str = (
                    datetime
                    .strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
                    .strftime("%Y-%m-%d")
                )
            except ValueError:
                pass
                
        logger.info(f"📌 {title} - Início: {start_date_str}, Fim: {end_date_str}\n{description_text}")


async def exibir_avisos(client: EducationAPI) -> None:
    """
    Obtém e exibe os avisos acadêmicos disponíveis.
    
    Args:
        client (EducationAPI): Instância autenticada do cliente da API.
    """
    notices_response = client.get_notices()
    
    if not notices_response or not notices_response.get('notices'):
        logger.warning("Nenhuma notificação encontrada.")
        return

    logger.info("📢 Notificações:")
    for notice in notices_response.get('notices', []):
        title = notice.get('title', 'Sem título')
        content = notice.get('content', '')
        content_text = BeautifulSoup(content, 'html.parser').get_text()
        created_at = notice.get('createdAt', 'Data não disponível')
        logger.info(f"📰 {title} - {created_at}\n{content_text}\n{100 * '='}")


async def exibir_notificacoes(client: EducationAPI) -> None:
    """
    Obtém as notificações do sistema para o usuário e as imprime na tela.
    
    Args:
        client (EducationAPI): Instância autenticada do cliente da API.
    """
    notifications = client.get_notifications(items_per_page=5)
    
    if not notifications or not notifications.get('notifications'):
        logger.warning("Nenhuma notificação encontrada.")
        return

    logger.info("🔔 Notificações:")
    print(notifications)
    for notification in notifications.get('notifications', []):
        title = notification.get('title', 'Sem título')
        content = notification.get('content', '')
        content_text = BeautifulSoup(content, 'html.parser').get_text()
        created_at = notification.get('createdAt', 'Data não disponível')
        logger.info(f"📢 {title} - {content_text} (Criado em: {created_at})")
