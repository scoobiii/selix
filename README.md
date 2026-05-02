
---

```markdown
# SELIX — A Selic Ideal do Brasil

**O que é isso?**  
É um programa que calcula a taxa de juros ideal para o Brasil usando matemática.

Hoje a Selic está em **14,50%**.  
O SELIX calcula que o ideal seria **9,48%**.

Isso economizaria **R$ 270 bilhões por ano** para o país.

---

## Como usar (super fácil)

### 1. Maneira mais fácil (não precisa instalar nada)

Clique neste botão e rode no navegador:

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)

- Clique em "Conectar"
- Clique em "Executar tudo" (ou pressione Ctrl + F9)
- Espere alguns segundos
- Pronto! Vai aparecer o resultado: **9,48%**

---

### 2. Para quem gosta de instalar (DevOps / Programadores)

```bash
# 1. Baixe o projeto
git clone https://github.com/scoobiii/selix.git
cd selix

# 2. Instale as ferramentas
pip install -r requirements.txt

# 3. Rode o cálculo
python src/selix/core.py
```

Pronto! O programa vai mostrar a Selic ideal.

---

### 3. Ver a prova matemática (opcional)

```bash
cd lean_proof

# Rode a prova simples
lake env lean SELIX_v4_simple.lean
```

Você vai ver vários `true` na tela — isso significa que a matemática está correta.

---

## O que o SELIX faz?

Ele responde a pergunta:  
**"Qual é a taxa de juros ideal para o Brasil agora?"**

Ele usa 4 regras importantes:
1. Não pode ser alta demais (senão o país perde nota de crédito)
2. O juro real não pode passar de 5%
3. Não pode prejudicar empresas que geram emprego
4. Tem que ser razoável comparado com outros países

A resposta que respeita todas essas regras é **9,48%**.

---

## Para Crianças e Curiosos

Imagine que o Brasil é uma grande casa.  
A Selic é como a taxa de aluguel que o governo paga pela dívida.

Hoje ele está pagando aluguel muito caro (14,50%).  
O SELIX mostra que poderia pagar menos (9,48%) sem quebrar as regras da casa.

Com o dinheiro economizado, daria para:
- Construir mais escolas
- Melhorar hospitais
- Ajudar empresas a crescer
- Sobrar dinheiro para outras coisas boas

---

## Como ajudar

- Rode o Colab e compartilhe o resultado
- Dê "Star" no projeto
- Conte para um professor, jornalista ou político
- Se você sabe programar, pode ajudar a melhorar o código

---

**Resumo em 1 linha:**

> O Brasil está pagando juros altos demais. A matemática mostra que dá para baixar para 9,48% de forma segura.

**Quer testar agora?**  
[Clique aqui e rode em 20 segundos →](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)

---

**Licença:** MIT (pode usar, copiar e melhorar livremente)

---
