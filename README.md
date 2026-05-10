<div align="center">
  <h1> 📚🔗 EADConnect </h1>
  <h3> Uma ponte entre você e a plataforma de EAD do Grupo A Educação! </h3>

  ![EADConnect](src/img/EADConnect.png)

  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.13-blue?logo=python&logoColor=white" alt="python">
  <img src="https://img.shields.io/badge/Poetry-Project-60A5FA?logo=poetry&logoColor=white" alt="poetry">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="license">
</div>

---

### ✨ **Descrição**

O **EADConnect** é uma biblioteca e interface automatizada desenvolvida em Python para interagir com a API da plataforma de educação a distância do Grupo A (utilizada por instituições como FAESA, entre outras). Ele permite automatizar a coleta de conteúdos, monitorar notas em tempo real e gerenciar informações acadêmicas e financeiras de forma programática.

💡 Ideal para estudantes que desejam centralizar seus estudos, desenvolvedores que buscam criar ferramentas educacionais ou para quem simplesmente quer organizar seus materiais offline.

---

### 🚀 **Recursos**

O **EADConnect** oferece um conjunto robusto de ferramentas para facilitar sua vida acadêmica:

- 🔐 **Autenticação Segura**: Gerenciamento completo de sessões e tokens (incluindo tokens de aplicação para serviços extras).
- 📥 **Extração de Conteúdo**: Baixe materiais de tópicos, exercícios e gere PDFs organizados automaticamente.
- 📊 **Monitoramento de Notas**: Script de monitoramento que envia notificações via **Telegram** assim que uma nova nota é postada.
- 💰 **Gestão Financeira**: Consulte débitos pendentes e gere dados para pagamento via PIX diretamente pela API.
- 📅 **Calendário & Comunicação**: Acesse eventos do calendário acadêmico, quadros de avisos e mensagens da caixa de entrada.
- 🏗️ **Arquitetura Modular**: Estrutura organizada em comandos (`commands`), serviços (`services`) e utilitários (`utils`).
- 🧪 **Extensível**: Baseado em um cliente HTTP customizado (`Browser`) pronto para novas integrações.

---

### 📦 **Instalação**

O projeto utiliza o **Poetry** para gerenciamento de dependências.

```bash
# Clone o repositório
git clone https://github.com/cleitonleonel/EADConnect.git
cd EADConnect

# Instale as dependências
poetry install

# Ative o ambiente virtual
poetry shell

# Execute o script principal
python main.py
```

---

### 🧭 **Estrutura do Projeto**

```text
EADConnect/
├── eadconnect/              # Pacote principal
│   ├── commands/            # Comandos de alto nível (Conteúdo, Notas, Financeiro, etc.)
│   ├── http/                # Cliente base e navegação
│   ├── services/            # Serviços (Monitoramento, Notificações)
│   ├── utils/               # Utilitários (PDF, Auth, File Manager)
│   ├── client.py            # Classe EducationAPI principal
│   ├── config.py            # Gerenciamento de configurações (TOML)
│   └── endpoints.py         # Mapeamento de URLs da API
├── src/                     # Assets e arquivos gerados
│   └── img/                 # Logos e banners
├── tests/                   # Suíte de testes
├── main.py                  # Entry point de demonstração
├── pyproject.toml           # Configurações do Poetry
└── README.md
```

---

### 🧪 **Exemplo de Uso**

Abaixo, um exemplo simplificado de como utilizar a `EducationAPI` para buscar notas:

```python
import asyncio
from eadconnect.client import EducationAPI
from eadconnect.utils.auth import authenticate

async def main():
    # Inicializa o cliente
    client = EducationAPI(institution="faesa", username="seu_usuario", password="sua_senha")
    
    # Autentica e obtém o token de acesso
    client.access_token = authenticate(client)
    
    # Lista cursos ativos e suas notas
    my_courses = client.get_my_courses()
    for course in my_courses.get('courses', []):
        if course.get('status') == 'isActual':
            grades = client.get_grades(course['id'])
            print(f"Disciplina: {course['name']} | Nota: {grades.get('finalGrade', {}).get('value')}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 🛠️ **Tecnologias Principais**

- **[Requests](https://requests.readthedocs.io/)**: Comunicação HTTP robusta.
- **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)**: Parsing de conteúdos HTML.
- **[Telethon](https://docs.telethon.dev/)**: Integração com a API do Telegram para notificações.
- **[fpdf2](https://py-pdf.github.io/fpdf2/)**: Geração de documentos PDF.
- **[Schedule](https://schedule.readthedocs.io/)**: Agendamento de tarefas periódicas.

---

### 🤝 **Contribuições**

Contribuições são o que fazem a comunidade open source um lugar incrível! Sinta-se à vontade para:
1. Dar um **Fork** no projeto.
2. Criar uma **Feature Branch** (`git checkout -b feature/AmazingFeature`).
3. Dar um **Commit** em suas mudanças (`git commit -m 'Add some AmazingFeature'`).
4. Dar um **Push** na Branch (`git push origin feature/AmazingFeature`).
5. Abrir um **Pull Request**.

---

### 📝 **Licença**

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

### 🧑‍💻 **Desenvolvedor**

Feito com 💙 por [Cleiton Leonel Creton](https://www.linkedin.com/in/cleiton-leonel-creton-331138167/)  
📫 [cleiton.leonel@gmail.com](mailto:cleiton.leonel@gmail.com)  
🐙 [GitHub](https://github.com/cleitonleonel) | 📱 [WhatsApp](https://wa.me/5527995772291?text=Ol%C3%A1%2C+vim+pelo+seu+projeto+EADConnect+e+gostaria+de+falar+com+voc%C3%AA!)
