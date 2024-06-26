# ![logo](comunidade/static/logo_banklegra.jpg) [Banklegra](https://banklegra.onrender.com)
## Tecnologias Utilizadas
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Dropbox](https://img.shields.io/badge/Dropbox-%233B4D98.svg?style=for-the-badge&logo=Dropbox&logoColor=white)
![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![sqlachemy]()
## Descrição
Banklegra é um projeto desenvolvido para a disciplina de Tópicos Especiais 1. Ele utiliza diversas tecnologias para criar uma aplicação web robusta e funcional.

**Banklegra** é um protótipo de banco digital que oferece uma ampla gama de serviços financeiros, incluindo carteira digital, empréstimos e transferências entre usuários. Além disso, permite a alteração de perfil, postagem de feedbacks e venda de produtos através de um marketplace integrado.

## Funcionalidades

- **Sistema de Login Seguro**: Usuários devem confirmar um código enviado por email para completar o login, garantindo maior segurança.
- **Recuperação de Senha**: Permite aos usuários redefinir a senha em caso de perda ou esquecimento.
- **Carteira Digital**: extrato e transferências.
- **Empréstimos**: Solicitação, aprovação de empréstimos.
- **Transferências**: Transferência de dinheiro rápida e segura entre usuários do Banklegra.
- **Alteração de Perfil**: Atualize informações pessoais e preferências do usuário.
- **Feedback de Usuário**: Postagem de feedbacks para melhorar a experiência bancária.
- **Marketplace**: Venda e compra de produtos variados na plataforma.

## Imagens do projeto
![carteira](comunidade/static/imagens_readme/transferencia_.jpg)
![loja](comunidade/static/imagens_readme/loja.jpg)
![perfil](comunidade/static/imagens_readme/perfil.jpg)
![feedback](comunidade/static/imagens_readme/feedback.jpg)
![extrato](comunidade/static/imagens_readme/extrato.jpg)

## Instalação
Para instalar as dependências do projeto, abra o terminal, navegue até a pasta onde o projeto está salvo e execute:
```bash
pip install -r requirements.txt
```

## Configuração das Credenciais
Defina as credenciais em um arquivo `.env` na raiz do projeto:
```env
SENDER_EMAIL='email que enviará as mensagens'
PASSWORD_EMAIL='crie um app para obter a senha'
APP_SECRET_KEY='defina uma chave'
URL_DATABASE='url do banco de dados'
API_KEY_DROPBOX='api do dropbox'
```

### Como Obter as Credenciais
- [Obter a senha do email](https://youtu.be/N97q96BygUg)
- [URL do banco de dados](https://youtu.be/3MZ_e_pST8g)
- [API do Dropbox](https://youtu.be/cj7A-CjL-wI)
- [Importância do APP_SECRET_KEY](https://cursos.alura.com.br/forum/topico-para-que-serve-app-secret_key-115455#:~:text=Para%20encriptar%20os%20passwords%20dos,produ%C3%A7%C3%A3o%20escolha%20uma%20chave%20segura.)

## Executando o Projeto Localmente
Para rodar o projeto em sua máquina, abra o terminal, navegue até a pasta onde o projeto está salvo e execute:
```bash
flask --app main run
```
Sinta-se à vontade para contribuir ou reportar problemas!
