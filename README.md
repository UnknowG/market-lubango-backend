# 🛒 Sistema E-commerce - API REST

> Plataforma completa de e-commerce com marketplace multi-vendedor, desenvolvida em Django REST Framework para o mercado angolano.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14+-red.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-Proprietário-yellow.svg)]()

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Documentação da API](#-documentação-da-api)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Testes](#-testes)
- [Contribuição](#-contribuição)

---

## 🎯 Sobre o Projeto

Sistema de e-commerce completo desenvolvido para o mercado angolano, suportando múltiplos vendedores (marketplace), com sistema de pagamento integrado (simulado) para Kwanza (AOA), gestão de estoque, avaliações, e funcionalidades completas de carrinho de compras.

### Características Principais

- 🏪 **Marketplace Multi-Vendedor**: Cada vendedor possui sua própria loja
- 💰 **Pagamento em AOA**: Sistema de pagamento adaptado para Kwanza
- 📦 **Gestão de Estoque**: Controle automático de inventário
- ⭐ **Sistema de Avaliações**: Reviews e ratings de produtos
- 🛒 **Carrinho Persistente**: Carrinho salvo entre sessões
- 📱 **API RESTful**: Totalmente compatível com frontend moderno
- 🔐 **Autenticação JWT**: Segurança robusta com tokens
- 📚 **Documentação Automática**: Swagger UI e ReDoc integrados

---

## ✨ Funcionalidades

### Para Compradores

- ✅ Registro e autenticação de usuários
- ✅ Navegação e busca de produtos
- ✅ Carrinho de compras persistente
- ✅ Finalização de pedidos
- ✅ Histórico de compras
- ✅ Sistema de avaliações
- ✅ Lista de desejos
- ✅ Perfil de usuário

### Para Vendedores

- ✅ Criação e gestão de loja
- ✅ CRUD de produtos
- ✅ Gestão de estoque
- ✅ Visualização de pedidos
- ✅ Atualização de status de pedidos
- ✅ Acompanhamento de avaliações

### Para Administradores

- ✅ Aprovação de vendedores
- ✅ Gestão de usuários
- ✅ Moderação de conteúdo
- ✅ Painel administrativo Django

---

## 🚀 Tecnologias

### Backend

- **Django 4.2** - Framework web Python
- **Django REST Framework** - API REST
- **SimpleJWT** - Autenticação JWT
- **DRF Spectacular** - Documentação OpenAPI/Swagger
- **Django CORS Headers** - Suporte CORS

### Banco de Dados

- **SQLite** (Desenvolvimento)
- **PostgreSQL** (Recomendado para Produção)

### Ferramentas de Desenvolvimento

- **Python 3.8+**
- **pip** - Gerenciador de pacotes
- **python-dotenv** - Variáveis de ambiente

---

## 📥 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Passo a Passo

1. **Clone o repositório**

```bash
git clone https://github.com/Emicy963/ecommerce-api.git
cd ecommerce-api
```

2. **Crie um ambiente virtual**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**

```bash
# Edite o .env com suas configurações
nano .env  # ou use seu editor preferido
```

5. **Execute as migrações**

```bash
python manage.py migrate
```

6. **Crie um superusuário**

```bash
python manage.py createsuperuser
```

7. **Carregue dados de exemplo (opcional)**

```bash
python manage.py loaddata fixtures.json
```

8. **Inicie o servidor**

```bash
python manage.py runserver
```

✅ Servidor rodando em: `http://localhost:8000`

---

## ⚙️ Configuração

### Arquivo `.env`

Crie um arquivo `.env` na raiz do projeto:

```env
# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Banco de Dados (PostgreSQL - Produção)
# DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce

# Email (Opcional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=seu-email@gmail.com
# EMAIL_HOST_PASSWORD=sua-senha-app

# Pagamento
TESTING=True  # Modo simulação
```

### Configurações Importantes

#### JWT Token

- **Expiração Access Token**: 1 hora
- **Expiração Refresh Token**: 7 dias
- **Blacklist**: Ativado (logout invalida tokens)

#### CORS

- Configure `CORS_ALLOWED_ORIGINS` com os domínios do seu frontend
- Em produção, desabilite `CORS_ALLOW_ALL_ORIGINS`

#### Moeda

- Sistema configurado para **Kwanza (AOA)**
- Símbolo: **Kz**

---

## 📚 Documentação da API

### Acessar Documentação

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema JSON**: http://localhost:8000/api/schema/

### Endpoints Principais

#### Autenticação

```
POST   /api/v1/auth/register/          - Registrar usuário
POST   /api/v1/auth/token/              - Login (obter tokens)
POST   /api/v1/auth/token/refresh/      - Renovar token
POST   /api/v1/auth/logout/             - Logout
GET    /api/v1/auth/profile/            - Perfil do usuário
```

#### Produtos

```
GET    /api/v1/products/                - Listar produtos
GET    /api/v1/products/{slug}/         - Detalhes do produto
GET    /api/v1/products/search/         - Buscar produtos
GET    /api/v1/products/categories/     - Listar categorias
POST   /api/v1/products/seller/create/  - Criar produto (vendedor)
```

#### Carrinho

```
POST   /api/v1/cart/create/             - Criar carrinho
GET    /api/v1/cart/{code}/             - Obter carrinho
POST   /api/v1/cart/add/                - Adicionar item
PUT    /api/v1/cart/update/             - Atualizar quantidade
DELETE /api/v1/cart/item/{id}/          - Remover item
```

#### Pedidos

```
POST   /api/v1/orders/create/           - Criar pedido
GET    /api/v1/orders/                  - Listar pedidos
GET    /api/v1/orders/{number}/         - Detalhes do pedido
POST   /api/v1/orders/{number}/refund/  - Solicitar reembolso
```

#### Reviews

```
POST   /api/v1/reviews/add/             - Adicionar avaliação
GET    /api/v1/reviews/product/{id}/    - Reviews do produto
GET    /api/v1/reviews/user/            - Minhas avaliações
PUT    /api/v1/reviews/{id}/            - Atualizar avaliação
DELETE /api/v1/reviews/{id}/delete/     - Deletar avaliação
```

#### Wishlist

```
GET    /api/v1/wishlist/                - Minha lista de desejos
POST   /api/v1/wishlist/add/            - Adicionar/remover item
DELETE /api/v1/wishlist/{id}/           - Remover item
```

### Exemplo de Uso

#### 1. Registrar Usuário

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao",
    "email": "joao@example.com",
    "password": "Senha@123",
    "confirm_password": "Senha@123",
    "first_name": "João",
    "last_name": "Silva",
    "user_type": "buyer"
  }'
```

#### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao",
    "password": "Senha@123"
  }'
```

**Resposta:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "joao@example.com",
    "name": "João Silva",
    "user_type": "buyer"
  }
}
```

#### 3. Usar Token em Requisições

```bash
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 📁 Estrutura do Projeto

```
ecommerce/
│
├── apps/
│   ├── accounts/           # Usuários, lojas e autenticação
│   │   ├── apps.py         # Configurações da app
│   │   ├── models.py       # CustomUser, Store
│   │   ├── serializers.py  # Serializers de usuário
│   │   ├── views.py        # Views de autenticação
│   │   └── urls.py         # Rotas de auth
│   │
│   ├── products/           # Produtos e categorias
│   │   ├── apps.py         # Configurações da app
│   │   ├── models.py       # Product, Category
│   │   ├── serializers.py  # Serializers de produto
│   │   ├── views.py        # CRUD de produtos
│   │   └── urls.py         # Rotas de produtos
│   │
│   ├── cart/               # Carrinho de compras
│   │   ├── apps.py         # Configurações da app
│   │   ├── models.py       # Cart, CartItem
│   │   ├── serializers.py  # Serializers de carrinho
│   │   ├── views.py        # Lógica do carrinho
│   │   └── urls.py         # Rotas de carrinho
│   │
│   ├── orders/             # Pedidos e pagamentos
│   │   ├── apps.py         # Configurações da app
│   │   ├── models.py       # Order, OrderItem, Payment
│   │   ├── serializers.py  # Serializers de pedido
│   │   ├── views.py        # Gestão de pedidos
│   │   ├── payments.py     # Sistema de pagamento
│   │   └── urls.py         # Rotas de pedidos
│   │
│   ├── reviews/            # Avaliações de produtos
│   │   ├── apps.py         # Configurações da app
│   │   ├── models.py       # Review, ProductRating
│   │   ├── serializers.py  # Serializers de reviews
│   │   ├── signals.py      # Atualização automática de rating
│   │   ├── views.py        # CRUD de reviews
│   │   └── urls.py         # Rotas de reviews
│   │
│   └── wishlist/           # Lista de desejos
│       ├── apps.py         # Configurações da app
│       ├── models.py       # Wishlist
│       ├── serializers.py  # Serializers de wishlist
│       ├── views.py        # Gestão de wishlist
│       └── urls.py         # Rotas de wishlist
│
├── ecommerce/              # Configurações do projeto
│   ├── settings.py         # Configurações Django
│   ├── urls.py             # URLs principais
│   └── wsgi.py             # WSGI para deploy
│
├── media/                  # Uploads de arquivos
├── static/                 # Arquivos estáticos
├── .env                    # Variáveis de ambiente (não versionar)
├── manage.py               # CLI do Django
├── requirements.txt        # Dependências Python
└── README.md               # Este arquivo
```

---

## 🧪 Testes

### Executar Todos os Testes

```bash
python manage.py test
```

### Testar App Específica

```bash
python manage.py test apps.accounts
python manage.py test apps.products
python manage.py test apps.cart
python manage.py test apps.orders
python manage.py test apps.reviews
python manage.py test apps.wishlist
```

### Cobertura de Testes

```bash
# Instalar coverage
pip install coverage

# Executar com cobertura
coverage run manage.py test
coverage report
coverage html  # Gera relatório HTML
```

### Testes Manuais

Use o script fornecido:

```bash
python test_api.py
```

Ou use Postman/Thunder Client (veja `GUIA_POSTMAN.md`)

---

## 🔒 Segurança

### Recomendações para Produção

- ✅ Altere `SECRET_KEY` para valor forte e único
- ✅ Defina `DEBUG=False`
- ✅ Configure `ALLOWED_HOSTS` corretamente
- ✅ Use HTTPS (SSL/TLS)
- ✅ Configure CORS adequadamente
- ✅ Use PostgreSQL ao invés de SQLite
- ✅ Configure backup automático do banco
- ✅ Implemente rate limiting
- ✅ Use servidor de arquivos (S3, Cloudinary)
- ✅ Configure logs e monitoramento

### Variáveis Sensíveis

**NUNCA** commite no Git:

- `.env`
- `db.sqlite3`
- `media/` (uploads de usuários)
- Chaves de API
- Credenciais de banco de dados

---

## 🚢 Deploy

### Preparação

```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Executar migrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

### Opções de Deploy

- **Heroku**: Rápido e fácil
- **DigitalOcean**: Droplets ou App Platform
- **AWS**: EC2 + RDS
- **Railway**: Moderno e simples
- **Render**: Gratuito para começar

Consulte `MANUAL_TECNICO.md` para instruções detalhadas.

---

## 📖 Documentação Adicional

- 📘 [Manual Técnico](MANUAL_TECNICO.md) - Arquitetura e funcionamento
- 📮 [Guia Postman](GUIA_POSTMAN.md) - Teste de endpoints

---

## 🤝 Contribuição

Este é um projeto proprietário desenvolvido para uso acadêmico. Contribuições não são aceitas publicamente.

---

## 📄 Licença

Consulte [LICENSE](LICENSE)

Este projeto é **confidencial** e de uso **exclusivo acadêmico**. A redistribuição, cópia ou uso comercial são estritamente proibidos sem autorização expressa.

---

## 👥 Autores

Desenvolvido por [Seu Nome] para [Cliente/Instituição].

---

## 📞 Suporte

Para questões técnicas ou suporte:

- **Email**: suporte@seudominio.ao
- **Documentação**: http://localhost:8000/api/docs/

---

## 🙏 Agradecimentos

- Django Software Foundation
- Django REST Framework
- Comunidade Python Angola

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**
