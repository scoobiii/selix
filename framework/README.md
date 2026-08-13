# SELIX Framework — Integração Canônica

Este diretório contém as especificações para integrar o SELIX como uma **fonte de verdade** em qualquer stack tecnológica (React, Vue, Angular, Python, Node.js, etc.).

**Regra de Ouro:**
> Nenhum front-end ou back-end deve hardcodar números oficiais (`8.25`, `6.0`, `14.25`, `9.48`, `10.75`). A fonte única de verdade é o `selix-official.json` (ou a API `/v1/selic`).

## Como consumir

### 1. Via JSON público (estático)
```javascript
fetch('https://raw.githubusercontent.com/scoobiii/selix/main/public/selix-official.json')
  .then(res => res.json())
  .then(data => {
    console.log('Selic ideal:', data.selic_ideal);
  });
```

### 2. Via API dinâmica (Cloud Run)
```javascript
fetch('https://api.selix.com/v1/selic/snapshot')
  .then(res => res.json())
  .then(data => {
    console.log('Selic atual:', data.selic_atual);
  });
```

### 3. Via ticker viral (CDN)
```html
<script src="https://cdn.selix.com.br/ticker.js" data-theme="dark" data-size="md"></script>
```

## Estrutura de pastas

-  → Especificações de produto (ticker, WASM, etc.)
-  → Este diretório (guias de integração)
-  → Estratégia geral de produto

---

**Contato:**  (Bluesky)
