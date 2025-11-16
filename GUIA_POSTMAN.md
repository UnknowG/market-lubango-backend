# 📮 Guia de Uso - Postman & Thunder Client

## Opção 1: Thunder Client (VS Code)

### Instalação

1. Abra o VS Code
2. Vá em Extensions (Ctrl+Shift+X)
3. Busque "Thunder Client"
4. Clique em "Install"

### Importar Coleção

1. Abra Thunder Client (ícone de raio na barra lateral)
2. Clique em "Collections"
3. Clique nos três pontos (...) → "Import"
4. Selecione o arquivo `thunder-collection.json`
5. A coleção "E-commerce API" aparecerá

### Configurar Ambiente

1. Em Thunder Client, clique em "Env"
2. Clique em "New Environment"
3. Nome: "Local"
4. Adicione variáveis:

```json
{
  "baseUrl": "http://localhost:8000",
  "accessToken": "",
  "refreshToken": "",
  "cartCode": "",
  "productSlug": "",
  "orderNumber": ""
}
```

### Usar a Coleção

1. Expanda a pasta "Auth"
2. Execute "Register User"
3. Execute "Login" - o token será salvo automaticamente
4. Use outros endpoints (já configurados com token)

---

## Opção 2: Postman

### Importar para Postman

#### Método 1: Importar JSON

1. Abra Postman
2. Clique em "Import" (canto superior esquerdo)
3. Arraste o arquivo `thunder-collection.json`
4. Clique em "Import"

#### Método 2: Converter para Postman Format

Se houver problemas, converta primeiro:

```bash
# Instalar ferramenta de conversão
npm install -g postman-collection-transformer

# Converter
postman-collection-transformer convert \
  -i thunder-collection.json \
  -o postman-collection.json \
  -j 2.1.0
```

### Configurar Variáveis de Ambiente Postman

1. Clique no ícone de olho (👁️) no canto superior direito
2. Clique em "Add" ao lado de "Environments"
3. Nome: `E-commerce Local`
4. Adicione as variáveis:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| baseUrl | [http://localhost:8000](http://localhost:8000) | [http://localhost:8000](http://localhost:8000) |
| accessToken | | |
| refreshToken | | |
| cartCode | | |
| productSlug | | |
| orderNumber | | |

5. Clique em "Save"
6. Selecione o ambiente no dropdown superior direito

### Automatizar Captura de Tokens

Para o endpoint "Login", adicione este script na aba "Tests":

```javascript
// Salvar tokens automaticamente após login
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("accessToken", response.access);
    pm.environment.set("refreshToken", response.refresh);
    console.log("Tokens salvos com sucesso!");
}
```

Para "Create Cart", adicione:

```javascript
// Salvar cart_code automaticamente
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.environment.set("cartCode", response.cart_code);
    console.log("Cart code salvo:", response.cart_code);
}
```

Para "Create Product", adicione:

```javascript
// Salvar slug do produto
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.environment.set("productSlug", response.slug);
    console.log("Product slug salvo:", response.slug);
}
```

---

## Fluxo de Testes Recomendado

### 1. Preparação

```bash
# Iniciar servidor
python manage.py runserver

# Em outro terminal, criar dados de teste
python manage.py shell
```

```python
# No shell Django
from apps.products.models import Category
from apps.accounts.models import CustomUser, Store

# Criar categoria
cat = Category.objects.create(name="Eletrônicos")

# Criar vendedor e loja
seller = CustomUser.objects.create_user(
    username="seller1",
    email="seller1@test.com",
    password="Test@123",
    user_type="seller",
    is_approved_seller=True
)

store = Store.objects.create(
    name="Loja Tech",
    owner=seller
)
```

### 2. Sequência de Testes

**A. Autenticação** (Pasta Auth)

1. ✅ Register User
2. ✅ Login (salva token automaticamente)
3. ✅ Get Profile (usa token)
4. ✅ Refresh Token
5. ✅ Logout

**B. Produtos** (Pasta Products)

1. ✅ List Products
2. ✅ List Categories
3. ✅ Search Products
4. ✅ Create Product (como vendedor)
5. ✅ Get Product Detail (copie o slug da resposta anterior)

**C. Carrinho** (Pasta Cart)

1. ✅ Create Cart (salva cart_code)
2. ✅ Add to Cart (use product_id da criação do produto)
3. ✅ Get Cart
4. ✅ Update Cart Item
5. ✅ Get User Cart

**D. Pedidos** (Pasta Orders)

1. ✅ Create Order (usa cart_code salvo)
2. ✅ List User Orders
3. ✅ Get Order Detail (copie order_number da resposta)

**E. Reviews** (Pasta Reviews)

1. ✅ Get Product Reviews
2. ✅ Add Review (requer pedido entregue)
3. ✅ Get User Reviews

**F. Wishlist** (Pasta Wishlist)

1. ✅ Get Wishlist
2. ✅ Add to Wishlist
3. ✅ Remove from Wishlist

---

## Dicas Importantes

### 🔐 Autenticação

- O token expira em 1 hora (configurável)
- Use "Refresh Token" para renovar sem fazer login novamente
- Endpoints protegidos retornam 401 se o token expirar

### 🐛 Troubleshooting

**Erro 401 Unauthorized:**

```md
Solução: Execute "Login" novamente para obter novo token
```

**Erro 404 Not Found:**

```md
Solução: Verifique se o servidor está rodando e a URL está correta
```

**Erro 400 Bad Request:**

```md
Solução: Verifique o formato do JSON no corpo da requisição
```

**Erro CORS:**

```md
Solução: Verifique CORS_ALLOWED_ORIGINS no settings.py
```

### 📊 Variáveis Úteis

Você pode usar variáveis em qualquer campo:

**URL:**

```md
{{baseUrl}}/api/v1/products/{{productSlug}}/
```

**Headers:**

```md
Authorization: Bearer {{accessToken}}
```

**Body:**

```json
{
  "cart_code": "{{cartCode}}",
  "product_id": 1
}
```

---

## Scripts Úteis Postman

### Pre-request Script (executado ANTES da requisição)

```javascript
// Verificar se tem token antes de fazer requisição
if (!pm.environment.get("accessToken")) {
    console.log("Token não encontrado. Execute Login primeiro!");
}

// Adicionar timestamp
pm.variables.set("timestamp", Date.now());
```

### Tests (executado APÓS a requisição)

```javascript
// Verificar status code
pm.test("Status code é 200", function () {
    pm.response.to.have.status(200);
});

// Verificar tempo de resposta
pm.test("Resposta em menos de 500ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Verificar estrutura da resposta
pm.test("Resposta contém access token", function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('access');
});
```

---

## Runner Collection (Executar todos os testes)

### Postman

1. Clique nos três pontos (...) na coleção
2. Selecione "Run collection"
3. Escolha os requests
4. Clique em "Run E-commerce API"

### Thunder Client

1. Clique com botão direito na coleção
2. Selecione "Run All"

---

## Exportar Resultados

### Postman

- Após rodar, clique em "Export Results"
- Salva como JSON ou HTML

### Thunder Client

- Resultados aparecem na aba "Activity"
- Pode copiar e colar em relatório

---

## 🎯 Checklist de Testes Manuais

- [ ] Registrar usuário (buyer e seller)
- [ ] Login com username
- [ ] Login com email
- [ ] Obter perfil
- [ ] Refresh token
- [ ] Logout
- [ ] Criar loja (seller)
- [ ] Criar produto (seller)
- [ ] Listar produtos
- [ ] Buscar produtos
- [ ] Criar carrinho
- [ ] Adicionar ao carrinho
- [ ] Atualizar quantidade
- [ ] Criar pedido
- [ ] Listar pedidos
- [ ] Adicionar à wishlist
- [ ] Adicionar review (requer pedido entregue)

**Total: 18 testes essenciais**
