import asyncio
import logging

from eadconnect.client import EducationAPI
from eadconnect.config import (
    load_configurations,
    save_credentials
)
from eadconnect.utils.auth import authenticate
from eadconnect.commands.conteudo import CURSOS, extrair_conteudo

from eadconnect.commands.notas import verificar_notas, listar_notas_por_curso
from eadconnect.commands.financeiro import exibir_financeiro
from eadconnect.commands.comunicacao import (
    exibir_mensagens,
    exibir_notificacoes,
    exibir_calendario,
    exibir_avisos
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    config = load_configurations()

    # Gerenciamento de credenciais via fallback
    username = config.get('auth', {}).get('username')
    password = config.get('auth', {}).get('password')
    if not username or not password:
        username = input("Usuário: ")
        password = input("Senha: ")
        save_credentials(username, password)

    # Inicialização do cliente
    client = EducationAPI("faesa", username, password)

    try:
        # Tenta autenticar o cliente
        client.access_token = authenticate(client, attempts=3)
    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        exit(1)

    # Execução do script principal (modifique para a função desejada)
    try:
        asyncio.run(extrair_conteudo(client, CURSOS, download_topics=True))
        # asyncio.run(verificar_notas(client))
        # asyncio.run(exibir_financeiro(client))
        # asyncio.run(exibir_notificacoes(client))
        # asyncio.run(exibir_calendario(client))
        # asyncio.run(exibir_avisos(client))
        # asyncio.run(exibir_mensagens(client))
        # asyncio.run(listar_notas_por_curso(client))
    except KeyboardInterrupt:
        logger.info(
            '\nBot interrompido pelo usuário.\n'
            'Desconectando...'
        )
