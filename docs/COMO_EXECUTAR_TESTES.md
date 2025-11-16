# 🧪 Guia de Execução de Testes

> Como executar todos os testes e corrigir os problemas identificados

---

## 📋 Passo a Passo Completo

### Passo 1: Preparar Ambiente

```bash
# Ativar ambiente virtual
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# Instalar/atualizar dependências
pip install -r requirements.txt
```

### Passo 2: Configurar Banco de Dados

```bash
# Aplicar migrações
python manage.py migrate

# Criar dados de teste - ESCOLHA UMA OPÇÃO:

# OPÇÃO 1: Usando comando Django (RECOMENDADO)
python manage.py setup_test_data

# OPÇÃO 2: Script Python direto (da raiz do projeto)
python setup_test_data.py

# OPÇÃO 3: Via Django shell
python manage.py shell < setup_test_data.py
```

**💡 Dica:** Se der erro "No module named 'ecommerce'", use a OPÇÃO 1

**Saída esperada:**

```txt
====================================================
🔧 CONFIGURANDO DADOS DE TESTE
====================================================

📂 Criando categorias...
  ✅ Criado: Eletrônicos
  ✅ Criado: Roupas
  ✅ Criado: Livros
  ✅ Criado: Móveis

👤 Criando vendedor aprovado...
  ✅ Vendedor criado

🏪 Criando loja...
  ✅ Criada: Loja Tech Angola

📦 Criando produtos...
  ✅ Criado: Smartphone Samsung Galaxy A54 - 450000.0 Kz
  ✅ Criado: Laptop HP Pavilion - 850000.0 Kz
  ✅ Criado: Camisa Polo Masculina - 8500.0 Kz
  ✅ Criado: Livro: Python Para Iniciantes - 12000.0 Kz
  ✅ Criado: Mesa de Escritório - 45000.0 Kz

👥 Criando comprador...
  ✅ Comprador criado

🔑 Criando administrador...
  ✅ Administrador criado

====================================================
✅ DADOS DE TESTE CONFIGURADOS COM SUCESSO!
====================================================
```

### Passo 3: Iniciar Servidor

```bash
# Em um terminal separado
python manage.py runserver
```

### Passo 4: Executar Testes

```bash
# Em outro terminal (com .venv ativo)
python tests/test_api.py
```

**Saída esperada (todos passando):**

```txt
======================================================================
🚀 INICIANDO TESTES COMPLETOS DA API E-COMMERCE v2.0
======================================================================

### SEÇÃO 1: AUTENTICAÇÃO ###
🧪 Testando: Registrar Comprador
✅ Registrar Comprador - Status: 201

🧪 Testando: Registrar Vendedor
✅ Registrar Vendedor - Status: 201

🧪 Testando: Registrar Administrador
✅ Registrar Administrador - Status: 201

🧪 Testando: Login Comprador
✅ Login Comprador - Status: 200

🧪 Testando: Login Vendedor
✅ Login Vendedor - Status: 200

🧪 Testando: Login Administrador
✅ Login Administrador - Status: 200

### SEÇÃO 2: FUNCIONALIDADES DE ADMIN ###
🧪 Testando: Listar Vendedores Pendentes
✅ Listar Vendedores Pendentes - Status: 200

🧪 Testando: Aprovar Vendedor
✅ Aprovar Vendedor - Status: 200
✨ Vendedor aprovado! Agora pode criar produtos.

### SEÇÃO 3: GESTÃO DE LOJAS ###
🧪 Testando: Criar Loja
✅ Criar Loja - Status: 201

### SEÇÃO 4: PRODUTOS E CATEGORIAS ###
🧪 Testando: Criar Produto (Vendedor Aprovado)
✅ Criar Produto (Vendedor Aprovado) - Status: 201
📦 Produto criado: ID=6, Slug=produto-teste-1731796800

### SEÇÃO 5: CARRINHO DE COMPRAS ###
🧪 Testando: Criar Carrinho Anônimo
✅ Criar Carrinho Anônimo - Status: 201
🛒 Carrinho criado: ABC123XYZ45

🧪 Testando: Adicionar Produto ao Carrinho
✅ Adicionar Produto ao Carrinho - Status: 200

### SEÇÃO 6: PEDIDOS ###
🧪 Testando: Criar Pedido
✅ Criar Pedido - Status: 201
📦 Pedido criado: ORD-A1B2C3D4

### SEÇÃO 7: AVALIAÇÕES ###
🧪 Testando: Obter Reviews do Produto
✅ Obter Reviews do Produto - Status: 200

🧪 Testando: Adicionar Review
ℹ️  Review não criado (esperado - requer pedido entregue)

### SEÇÃO 8: LISTA DE DESEJOS ###
🧪 Testando: Obter Wishlist (vazia)
✅ Obter Wishlist (vazia) - Status: 200

🧪 Testando: Adicionar à Wishlist
✅ Adicionar à Wishlist - Status: 201
❤️  Produto adicionado à wishlist: ID=1

======================================================================
📊 RELATÓRIO FINAL DE TESTES
======================================================================

📈 Total de testes: 35
✅ Passou: 35
❌ Falhou: 0
📊 Taxa de sucesso: 100.0%

🎉 TODOS OS TESTES PASSARAM COM SUCESSO!
✨ Sistema funcionando perfeitamente!
======================================================================
```

---

## 🔍 Verificações Adicionais

### Verificar Banco de Dados

```bash
python manage.py shell
```

```python
from apps.accounts.models import CustomUser, Store
from apps.products.models import Product, Category

# Verificar usuários
print(f"Usuários: {CustomUser.objects.count()}")
print(f"Vendedores aprovados: {CustomUser.objects.filter(user_type='seller', is_approved_seller=True).count()}")

# Verificar produtos
print(f"Produtos: {Product.objects.count()}")
print(f"Categorias: {Category.objects.count()}")
print(f"Lojas: {Store.objects.count()}")
```

### Acessar Documentação API

Abra no navegador:

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **Admin Django**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

**Credenciais do admin:**

- Usuário: `admin_teste`
- Senha: `Test@123`

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'requests'"

```bash
pip install requests
```

### Erro: "django.db.utils.OperationalError: no such table"

```bash
python manage.py migrate
```

### Erro: "Connection refused"

```bash
# Certifique-se de que o servidor está rodando
python manage.py runserver
```

### Testes continuam falhando

```bash
# 1. Limpar banco de dados
python manage.py flush --no-input

# 2. Aplicar migrações
python manage.py migrate

# 3. Recriar dados de teste
python setup_test_data.py

# 4. Executar testes novamente
python test_api_completo.py
```

### Ver logs detalhados do servidor

O servidor mostra todas as requisições:

```txt
INFO "POST /api/v1/auth/register/ HTTP/1.1" 201 42
INFO "POST /api/v1/auth/token/ HTTP/1.1" 200 783
```

Se aparecer `WARNING` ou `ERROR`, verifique:

- URL correta
- Dados JSON válidos
- Token válido

---

## 📊 Métricas Esperadas

### Testes que devem passar (35 total)

**Autenticação (6):**

- ✅ Registrar Comprador
- ✅ Registrar Vendedor  
- ✅ Registrar Admin
- ✅ Login Comprador
- ✅ Login Vendedor
- ✅ Login Admin

**Admin (2):**

- ✅ Listar Vendedores Pendentes
- ✅ Aprovar Vendedor

**Lojas (3):**

- ✅ Criar Loja
- ✅ Obter Loja
- ✅ Atualizar Loja

**Produtos (6):**

- ✅ Listar Produtos
- ✅ Listar Categorias
- ✅ Buscar Produtos
- ✅ Criar Produto
- ✅ Obter Produto
- ✅ Atualizar Produto

**Carrinho (7):**

- ✅ Criar Carrinho Anônimo
- ✅ Obter Carrinho
- ✅ Adicionar ao Carrinho
- ✅ Criar Carrinho do Usuário
- ✅ Obter Carrinho do Usuário
- ✅ Mesclar Carrinhos
- ✅ Atualizar Quantidade

**Pedidos (3):**

- ✅ Criar Pedido
- ✅ Listar Pedidos
- ✅ Obter Detalhes

**Reviews (2):**

- ✅ Obter Reviews
- ℹ️  Adicionar Review (pode falhar - esperado)

**Wishlist (4):**

- ✅ Obter Wishlist
- ✅ Adicionar à Wishlist
- ✅ Remover da Wishlist
- ✅ Verificar Vazia

**Vendedor (2):**

- ✅ Listar Pedidos da Loja
- ✅ Atualizar Status do Pedido

---

## 🎯 Próximos Passos

Depois de todos os testes passarem:

1. ✅ Testar manualmente com Postman (seguir [GUIA_POSTMAN](GUIA_POSTMAN.md))
2. ✅ Acessar Swagger UI e testar interativamente
3. ✅ Executar testes unitários do Django: `python manage.py test`
4. ✅ Preparar para integração com frontend
5. ✅ Revisar documentação antes de entregar

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs do servidor
2. Execute `python manage.py check`
3. Consulte [MANUAL_TECNICO](MANUAL_TECNICO.md)
4. Revise a seção de troubleshooting acima

---

**🎉 Boa sorte com os testes!**
