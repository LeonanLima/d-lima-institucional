# Landing Page D'LIMA Engenharia — MCMV Premium

**Data:** 2026-06-08
**Projeto:** Site institucional / landing de conversão da D'LIMA Engenharia
**Repositório:** `d-lima-institucional`

---

## 1. Objetivo

Landing page de **conversão** para captar leads de financiamento habitacional
(Minha Casa Minha Vida) para a D'LIMA Engenharia, construtora chave-na-mão de
São Mateus/ES. O diferencial estratégico: tratar o público MCMV com uma
**apresentação premium**, posicionando a D'LIMA acima das construtoras populares
genéricas.

## 2. Decisões travadas (com o cliente)

| Decisão | Escolha |
|---|---|
| Público primário | **Financiamento / MCMV** ("sair do aluguel") |
| Identidade visual | **Verde-escuro + dourado premium** (a do site institucional) |
| Captura de lead | **Formulário → WhatsApp**, sem backend |
| Depoimentos fictícios | **NÃO usar.** Faixa de confiança honesta + "depoimentos em breve" |
| reCAPTCHA | **Não incluir** (form não tem backend a ser spammado) |
| GA4 / Pixel | **Slot pronto** no código; cliente cola o ID depois |
| Fatos do negócio (prazo, garantia, preço, área de atendimento) | **Placeholders editáveis** marcados claramente |

## 3. Stack & estrutura

Espelha o site institucional já publicado (deploy no Render conhecido pelo cliente):

```
d-lima-institucional/
├── app.py                 # Flask: serve index.html, lê PORT do ambiente
├── requirements.txt       # flask
├── templates/
│   └── index.html         # Página única (Tailwind via CDN)
├── static/
│   ├── minha-logo.png     # copiar de Desktop\DLIMA\EMPRESA\LOGO
│   ├── fachada.png        # copiar de MARKETING\Fachada D'LIMA Engenharia.png
│   └── (renders/placeholders de modelos)
└── docs/superpowers/specs/
```

- **Tailwind via CDN**, fontes Google **Montserrat** (títulos) + **Inter** (corpo).
- **Paleta:** `#0F120F` fundo escuro · `#B89B5E` dourado (marca + CTAs) ·
  `#F9F8F6` claro · `#2D3A2C` texto · `#EFEBE0` bege seções.
- Mobile-first, responsivo, meta de Lighthouse 90+.

## 4. Seções da página (ordem)

1. **Header fixo** — logo + botão "Fazer Simulação" (âncora p/ form).
2. **Hero** — fundo: render da fachada com overlay verde-escuro.
   Título *"Chegou a hora de sair do aluguel"*. Bullets: subsídio até R$ 55 mil ·
   use o FGTS na entrada · projeto moderno e bom acabamento.
   **Formulário de simulação**: Nome, WhatsApp, Faixa de renda (4 faixas MCMV).
   Ao enviar → monta mensagem estruturada e abre `wa.me/5528999646592`.
3. **Por que construir com a D'LIMA** — 4 cards: Burocracia Zero (cuidamos da
   Caixa) · Projeto Personalizado · **Engenheiro Civil responsável** (diferencial
   real) · Chave na mão.
4. **Como funciona** — 4 passos: Simulação → Aprovação do crédito →
   Projeto + Obra → Entrega das chaves.
5. **Subsídios & Faixas** — bloco educativo das faixas MCMV + CTA.
6. **Projetos / Modelos** — galeria: render real + placeholders de modelos
   modernos (cliente substitui por fotos reais depois).
7. **Prova social (honesta)** — faixa de confiança: "Engenheiro Civil registrado ·
   Especialista MCMV · Atende São Mateus e região" + bloco "Depoimentos em breve".
8. **FAQ** — quanto custa · quanto tempo · vocês financiam · tem garantia ·
   atendem fora de São Mateus. Respostas com **placeholders editáveis**.
9. **CTA final** — "Não deixe seu sonho para amanhã" + botão WhatsApp.
10. **Footer** — logo, Instagram (@leonan.dlima), Facebook, WhatsApp, copyright,
    link Política de Privacidade.
11. **WhatsApp flutuante** (canto inferior direito).

## 5. Dados confirmados

- WhatsApp: **5528999646592**
- Instagram: **@leonan.dlima**
- Facebook: perfil `61577458711721`
- E-mail profissional: **contato@dlimaengenharia.org**
- Domínio: **dlimaengenharia.org**
- Local: São Mateus, ES

## 6. SEO & técnico

- Meta tags (title, description) pt-BR.
- Open Graph + Twitter Card (logo/fachada como imagem).
- Schema.org `GeneralContractor` com endereço São Mateus/ES e telefone.
- Slot de GA4 e Meta Pixel comentado no `<head>`.
- Smooth scroll, lazy-load de imagens.
- Página `politica-privacidade` simples (padrão LGPD) — rota Flask extra.

## 7. Placeholders que o cliente preenche depois

`{{PRAZO_MEDIO}}` · `{{GARANTIA}}` · `{{FAIXA_PRECO}}` · `{{AREA_ATENDIMENTO}}` ·
`{{GA4_ID}}` · `{{META_PIXEL_ID}}` · fotos reais de obras/depoimentos.

## 8. Fora de escopo (YAGNI)

- Backend / banco de leads · reCAPTCHA · depoimentos fictícios · chatbot ·
  agendamento · múltiplas páginas além de privacidade.
