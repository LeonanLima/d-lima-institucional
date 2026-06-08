# Deploy no Render — D'LIMA Engenharia

Landing page Flask servida em produção com **Gunicorn**. Arquivos já prontos:
`render.yaml` (Blueprint), `requirements.txt`, `.python-version`.

---

## Passo 1 — Subir o código para o GitHub

O Render faz deploy a partir de um repositório Git. Crie um repo no GitHub
(ex.: `d-lima-institucional`, pode ser privado) e conecte:

```bash
git remote add origin https://github.com/SEU_USUARIO/d-lima-institucional.git
git push -u origin main
```

> Se preferir, use o GitHub Desktop: "Add Local Repository" → aponte para esta
> pasta → "Publish repository".

## Passo 2 — Criar o serviço no Render

Opção A (recomendada — usa o `render.yaml` automaticamente):
1. Acesse https://dashboard.render.com → **New** → **Blueprint**.
2. Conecte sua conta GitHub e selecione o repositório.
3. O Render lê o `render.yaml` e já preenche tudo. Clique **Apply**.

Opção B (manual, sem Blueprint):
1. **New** → **Web Service** → conecte o repositório.
2. Preencha:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan:** Free
3. **Create Web Service**.

O Render instala as dependências e sobe o app. Em ~2 min você terá uma URL
tipo `https://dlima-engenharia.onrender.com`.

## Passo 3 — Apontar o domínio dlimaengenharia.org

1. No serviço → aba **Settings** → **Custom Domains** → **Add Custom Domain**.
2. Adicione `dlimaengenharia.org` e `www.dlimaengenharia.org`.
3. O Render mostra os registros DNS (um `A`/`ALIAS` para a raiz e um `CNAME`
   para o `www`). Configure-os no painel onde você registrou o domínio.
4. Aguarde a propagação (minutos a algumas horas). O SSL (HTTPS) é automático.

---

## Atualizar o site depois

Com `autoDeploy: true` (já no `render.yaml`), todo `git push` para a branch
`main` redeploya sozinho:

```bash
git add -A
git commit -m "sua alteração"
git push
```

## Observações

- **Free tier dorme:** após ~15 min sem acesso, o serviço "hiberna" e a 1ª
  visita seguinte demora ~30s para acordar. Para tráfego pago, considere o
  plano **Starter** (pago) para o site responder sempre na hora.
- **Variáveis (GA4/Pixel):** quando tiver os IDs, basta editar o `index.html`
  (slot comentado no `<head>`) e dar push.
- **Rodar testes localmente antes do push:**
  `./.venv/Scripts/python.exe -m pytest -q`
