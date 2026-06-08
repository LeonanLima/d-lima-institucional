# Landing MCMV Premium D'LIMA — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir uma landing page de conversão MCMV, com identidade premium verde+dourado, formulário que abre o WhatsApp, servida por Flask.

**Architecture:** Página única `templates/index.html` (Tailwind via CDN + Montserrat/Inter), servida por um `app.py` Flask mínimo (mesma estrutura do site institucional já publicado no Render). Form sem backend: monta mensagem e redireciona para `wa.me`. Verificação por `pytest` usando o test client do Flask, checando rota 200 e marcadores (`id`/strings) de cada seção. Assets reais (logo, fachada) copiados para `static/`.

**Tech Stack:** Python 3.13, Flask, pytest, Tailwind CSS (CDN), Lucide icons (CDN).

**Referências de markup/copy (já existem no PC, usar como fonte de verdade):**
- Padrão visual premium (cores, fontes, cards): `Downloads\d-lima-institucional-main (1)\...\templates\index.html`
- Copy MCMV + form→WhatsApp + faixas de renda: `Desktop\DLIMA\EMPRESA\MARKETING\COPY PARA DLIMA.HTML`

**Paleta:** `#0F120F` fundo · `#B89B5E` dourado (marca+CTA) · `#F9F8F6` claro · `#2D3A2C` texto · `#EFEBE0` bege.

---

## File Structure

```
d-lima-institucional/
├── app.py                 # Flask: rota / e /politica-privacidade
├── requirements.txt       # flask, pytest
├── templates/
│   ├── index.html         # landing (todas as seções)
│   └── privacidade.html   # política LGPD simples
├── static/
│   ├── minha-logo.png
│   └── fachada.png
└── tests/
    └── test_app.py        # test client: 200 + marcadores de seção
```

---

## Task 0: Scaffold Flask + assets + teste base

**Files:**
- Create: `app.py`, `requirements.txt`, `tests/test_app.py`, `templates/index.html`
- Copy: assets para `static/`

- [ ] **Step 1: Copiar assets reais para static/**

```bash
mkdir -p static templates tests
cp "/c/Users/leona/Desktop/DLIMA/EMPRESA/LOGO/minha logo.png" static/minha-logo.png
cp "/c/Users/leona/Desktop/DLIMA/EMPRESA/MARKETING/Fachada D'LIMA Engenharia.png" static/fachada.png
```

- [ ] **Step 2: requirements.txt**

```
flask
pytest
```

Instalar: `./.venv/Scripts/python.exe -m pip install -r requirements.txt`

- [ ] **Step 3: app.py**

```python
import os
from flask import Flask, render_template

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/politica-privacidade")
def privacidade():
    return render_template("privacidade.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
```

- [ ] **Step 4: Escrever teste que falha** — `tests/test_app.py`

```python
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index_ok(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "D'LIMA" in r.get_data(as_text=True)


def test_whatsapp_number_present(client):
    html = client.get("/").get_data(as_text=True)
    assert "5528999646592" in html
```

- [ ] **Step 5: Rodar teste — deve FALHAR** (template não existe)

Run: `./.venv/Scripts/python.exe -m pytest tests/test_app.py -q`
Expected: FAIL (TemplateNotFound: index.html)

- [ ] **Step 6: index.html mínimo** — só o esqueleto `<html>` com title "D'LIMA Engenharia" e o número `5528999646592` num link `wa.me` placeholder, para o teste passar.

- [ ] **Step 7: Rodar teste — deve PASSAR**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_app.py -q`
Expected: 2 passed

- [ ] **Step 8: Commit**

```bash
git add app.py requirements.txt tests/ templates/index.html static/
git commit -m "feat: scaffold Flask + teste base da landing"
```

---

## Task 1: Head, SEO, Tailwind config e layout base

**Files:** Modify `templates/index.html`, `tests/test_app.py`

- [ ] **Step 1: Adicionar asserts ao teste**

```python
def test_seo_and_fonts(client):
    html = client.get("/").get_data(as_text=True)
    assert 'property="og:title"' in html
    assert "GeneralContractor" in html          # Schema.org JSON-LD
    assert "Montserrat" in html                  # Google Fonts
    assert "GA4_ID" in html                      # slot analytics comentado
```

- [ ] **Step 2: Rodar — FALHA.** `pytest tests/test_app.py::test_seo_and_fonts -q`

- [ ] **Step 3: Implementar `<head>`** com:
  - `<title>D'LIMA Engenharia | Construa sua casa com o Minha Casa Minha Vida</title>`
  - meta description pt-BR sobre construção MCMV em São Mateus/ES.
  - Open Graph (`og:title`, `og:description`, `og:image` = `/static/fachada.png`, `og:type=website`) + Twitter Card.
  - Tailwind CDN + `tailwind.config` com cores `brand` (dark `#0F120F`, gold `#B89B5E`, cream `#F9F8F6`, sand `#EFEBE0`, text `#2D3A2C`) e fontes `heading: Montserrat`, `body: Inter`.
  - Google Fonts Montserrat + Inter; Lucide CDN.
  - JSON-LD `<script type="application/ld+json">` com `@type: GeneralContractor`, name, telephone `+5528999646592`, areaServed São Mateus ES, url dlimaengenharia.org.
  - Slot comentado: `<!-- GA4_ID: cole aqui --> <!-- META_PIXEL_ID: cole aqui -->`.
  - `<body class="bg-brand-cream text-brand-text font-body antialiased">`.

- [ ] **Step 4: Rodar — PASSA.** Todos os testes verdes.

- [ ] **Step 5: Commit** — `git commit -am "feat: head, SEO, Schema.org e config Tailwind"`

---

## Task 2: Header fixo + Hero com formulário → WhatsApp

**Files:** Modify `templates/index.html`, `tests/test_app.py`

- [ ] **Step 1: Asserts**

```python
def test_hero_form(client):
    html = client.get("/").get_data(as_text=True)
    assert 'id="simulacao"' in html
    assert "aluguel" in html.lower()
    assert 'id="leadForm"' in html
    assert "Faixa" in html or "renda" in html.lower()
```

- [ ] **Step 2: Rodar — FALHA.**

- [ ] **Step 3: Implementar Header + Hero.**
  - Header `sticky top-0 z-50` fundo `#0F120F`: logo (`/static/minha-logo.png`, h-12) à esquerda; botão dourado "Fazer Simulação" → `#simulacao`.
  - Hero: fundo `linear-gradient` escuro sobre `/static/fachada.png`. Grid 2 colunas (md):
    - Esquerda: badge "Minha Casa Minha Vida", H1 *"Chegou a hora de sair do aluguel"* (palavra "aluguel" em dourado), parágrafo, 3 bullets dourados (subsídio até R$ 55.000 · use o FGTS na entrada · projeto moderno e bom acabamento).
    - Direita: card branco `id="simulacao"` com `<form id="leadForm">`: Nome, WhatsApp, select Faixa de renda (4 faixas, copiar valores de `COPY PARA DLIMA.HTML` linhas 123-127), botão dourado "Quero minha simulação". `<div id="successMessage" class="hidden">`.
  - JS (reusar lógica de `COPY PARA DLIMA.HTML` linhas 231-265): no submit, `e.preventDefault()`, monta `mensagem` com nome+renda, `window.location.href = https://wa.me/5528999646592?text=...`, mostra successMessage.
  - Smooth scroll para âncoras `#`.

- [ ] **Step 4: Rodar — PASSA.**
- [ ] **Step 5: Commit** — `"feat: header fixo + hero com form WhatsApp"`

---

## Task 3: Diferenciais + Como funciona

**Files:** Modify `templates/index.html`, `tests/test_app.py`

- [ ] **Step 1: Asserts**

```python
def test_diferenciais_passos(client):
    html = client.get("/").get_data(as_text=True)
    assert "Burocracia Zero" in html
    assert "Engenheiro Civil" in html
    assert 'id="como-funciona"' in html
```

- [ ] **Step 2: Rodar — FALHA.**
- [ ] **Step 3: Implementar.**
  - Seção "Por que construir com a D'LIMA?" — 4 cards (grid md:4), ícones Lucide, hover dourado: **Burocracia Zero** (cuidamos da Caixa) · **Projeto Personalizado** · **Engenheiro Civil responsável** (diferencial real, ícone `hard-hat`/`ruler`) · **Chave na mão**.
  - Seção `id="como-funciona"` fundo `#EFEBE0` — 4 passos numerados: 1 Simulação · 2 Aprovação do crédito · 3 Projeto + Obra · 4 Entrega das chaves.
- [ ] **Step 4: Rodar — PASSA.**
- [ ] **Step 5: Commit** — `"feat: secao diferenciais + como funciona"`

---

## Task 4: Subsídios & Faixas + Projetos/Modelos

**Files:** Modify `templates/index.html`, `tests/test_app.py`

- [ ] **Step 1: Asserts**

```python
def test_subsidios_projetos(client):
    html = client.get("/").get_data(as_text=True)
    assert "Faixa" in html and "FGTS" in html
    assert 'id="projetos"' in html
```

- [ ] **Step 2: Rodar — FALHA.**
- [ ] **Step 3: Implementar.**
  - Bloco "Subsídios & Faixas" educativo: cards/linhas das 4 faixas de renda MCMV (mesmos valores do select) com o benefício de cada uma; CTA dourado "Descubra seu subsídio" → `#simulacao`.
  - Seção `id="projetos"` "Nossos Modelos": galeria grid (3 col md). 1ª imagem = `/static/fachada.png`; demais = placeholders com `<!-- TROCAR por render/foto real -->` e fundo `bg-brand-sand` + legenda "Modelo em breve". `loading="lazy"` nas imagens.
- [ ] **Step 4: Rodar — PASSA.**
- [ ] **Step 5: Commit** — `"feat: subsidios/faixas + galeria de modelos"`

---

## Task 5: Prova social honesta + FAQ

**Files:** Modify `templates/index.html`, `tests/test_app.py`

- [ ] **Step 1: Asserts**

```python
def test_provasocial_faq(client):
    html = client.get("/").get_data(as_text=True)
    assert "Engenheiro Civil registrado" in html
    assert 'id="faq"' in html
    assert "{{PRAZO_MEDIO}}" in html  # placeholder editavel presente
```

- [ ] **Step 2: Rodar — FALHA.**
- [ ] **Step 3: Implementar.**
  - Faixa de confiança (sem depoimentos fictícios): 3 selos — "Engenheiro Civil registrado" · "Especialista Minha Casa Minha Vida" · "Atende São Mateus e região". Abaixo, bloco discreto "Depoimentos de clientes em breve" com `<!-- inserir depoimentos reais aqui -->`.
  - Seção `id="faq"` (acordeão simples CSS/JS) com 5 perguntas; respostas usam placeholders literais para o cliente editar:
    - "Quanto custa?" → `{{FAIXA_PRECO}}`
    - "Quanto tempo leva?" → `{{PRAZO_MEDIO}}`
    - "Vocês financiam?" → texto MCMV/Caixa (sem placeholder)
    - "Tem garantia?" → `{{GARANTIA}}`
    - "Atendem fora de São Mateus?" → `{{AREA_ATENDIMENTO}}`
- [ ] **Step 4: Rodar — PASSA.**
- [ ] **Step 5: Commit** — `"feat: prova social honesta + FAQ com placeholders"`

---

## Task 6: CTA final + Footer + WhatsApp flutuante

**Files:** Modify `templates/index.html`, `tests/test_app.py`

- [ ] **Step 1: Asserts**

```python
def test_cta_footer(client):
    html = client.get("/").get_data(as_text=True)
    assert "leonan.dlima" in html                       # instagram
    assert "politica-privacidade" in html               # link footer
    assert 'id="whatsapp-float"' in html
```

- [ ] **Step 2: Rodar — FALHA.**
- [ ] **Step 3: Implementar.**
  - CTA final fundo `#0F120F`: "Não deixe seu sonho para amanhã" + botão dourado "Falar com um especialista" → `wa.me`.
  - Footer: logo, links Instagram (`https://www.instagram.com/leonan.dlima`), Facebook (`https://www.facebook.com/profile.php?id=61577458711721`), WhatsApp; copyright "© 2026 D'LIMA Engenharia"; link "Política de Privacidade" → `/politica-privacidade`.
  - Botão flutuante `id="whatsapp-float"` fixo inferior-direito (verde) → `wa.me` com texto pré-preenchido.
- [ ] **Step 4: Rodar — PASSA.**
- [ ] **Step 5: Commit** — `"feat: CTA final, footer e WhatsApp flutuante"`

---

## Task 7: Página de Política de Privacidade (LGPD)

**Files:** Create `templates/privacidade.html`; Modify `tests/test_app.py`

- [ ] **Step 1: Assert**

```python
def test_privacidade(client):
    r = client.get("/politica-privacidade")
    assert r.status_code == 200
    assert "Privacidade" in r.get_data(as_text=True)
```

- [ ] **Step 2: Rodar — FALHA.**
- [ ] **Step 3: Implementar `privacidade.html`** — página simples mesma identidade: explica que os dados do formulário (nome, telefone, renda) são usados só para contato via WhatsApp, não compartilhados; contato `contato@dlimaengenharia.org`; data; link de volta para `/`.
- [ ] **Step 4: Rodar — PASSA.**
- [ ] **Step 5: Commit** — `"feat: pagina de politica de privacidade LGPD"`

---

## Task 8: Verificação visual final

**Files:** nenhum (validação)

- [ ] **Step 1: Rodar suíte completa** — `./.venv/Scripts/python.exe -m pytest -q` → tudo verde.
- [ ] **Step 2: Subir o app** — `./.venv/Scripts/python.exe app.py` e abrir `http://localhost:10000`.
- [ ] **Step 3: Conferir manualmente**: responsividade mobile (DevTools), envio do form abre WhatsApp com mensagem correta, todos os links (IG/FB/WhatsApp/privacidade), imagens carregam.
- [ ] **Step 4: Checklist de placeholders** — confirmar que `{{PRAZO_MEDIO}}`, `{{GARANTIA}}`, `{{FAIXA_PRECO}}`, `{{AREA_ATENDIMENTO}}`, `GA4_ID`, `META_PIXEL_ID` estão visíveis/comentados para o cliente preencher.
- [ ] **Step 5: Commit final** (se houver ajustes) — `"chore: ajustes da verificacao visual"`

---

## Notas de deploy (pós-implementação)

Mesmo fluxo do site institucional no Render: `app.py` lê `PORT` do ambiente; start command `python app.py` (ou `gunicorn app:app`). Apontar `dlimaengenharia.org` para o serviço.
