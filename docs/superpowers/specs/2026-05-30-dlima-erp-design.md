# D'LIMA Engenharia — Plataforma ERP
**Documento de Especificação**
**Data:** 30/05/2026
**Autor:** Leonan Lima da Silva — D'LIMA Engenharia
**Status:** Aprovado para implementação

---

## 1. Visão Geral

### 1.1 Problema
Leonan Lima da Silva, engenheiro civil proprietário da D'LIMA Engenharia (Nova Venécia/ES), realiza 1 a 3 orçamentos residenciais por mês. O processo atual usa o Sienge (caro, sem geração automática de PCI) e planilhas manuais. Cada orçamento consome horas de trabalho repetitivo em levantamento de quantitativos e preenchimento da PCI Caixa.

### 1.2 Solução
Plataforma web própria (PWA) que automatiza o ciclo completo:
**Dimensões do projeto → Quantitativos automáticos → Orçamento → PCI Caixa + PDF profissional**

### 1.3 Objetivo do MVP
Permitir que Leonan faça um orçamento completo com PCI em menos de 30 minutos, contra as horas atuais.

### 1.4 Identidade Visual
- Fundo: `#0F120F` (verde escuro D'LIMA)
- Dourado: `#B89B5E` (destaque D'LIMA)
- Tipografia: Montserrat (títulos) + Inter (corpo)
- Site institucional existente: mantido separado e intacto

---

## 2. Arquitetura

### 2.1 Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Frontend + Backend | Next.js 15 (App Router) | PWA nativa, offline, fullstack em um projeto |
| Banco de dados | Supabase PostgreSQL | Auth + DB + Storage gratuito, escala fácil |
| Autenticação | Supabase Auth | Login por e-mail, JWT automático |
| Armazenamento | Supabase Storage | Plantas, fotos, PDFs, documentos |
| Deploy | Vercel | CI/CD automático, CDN global, gratuito |
| PDF | React-PDF | Relatórios profissionais client-side |
| Takeoff Canvas | Fabric.js | Clique nos vértices sobre a planta |
| **Custo mensal inicial** | **R$ 0,00** | Todos os serviços em plano gratuito |

### 2.2 Diagrama de Arquitetura

```
Usuário (celular/desktop)
        │ HTTPS
        ▼
Next.js PWA (Vercel)
  ├── Interface React (dark/gold D'LIMA)
  ├── Service Workers (cache offline)
  ├── IndexedDB (dados locais na obra)
  └── API Routes
        ├── Geração de PDF profissional
        ├── Export Excel PCI Caixa
        └── Motor de quantitativos
              │
              ▼
        Supabase
          ├── PostgreSQL (dados)
          ├── Auth (login)
          └── Storage (arquivos)
```

### 2.3 PWA e Offline
- Service workers fazem cache das telas principais
- IndexedDB armazena rascunhos e medições localmente
- Sincronização automática quando a conexão é restaurada
- Ideal para uso na obra sem sinal de internet

### 2.4 Domínio
- Site institucional: `dlima.eng.br` (intacto)
- Plataforma ERP: `app.dlima.eng.br`

---

## 3. Módulos do Sistema

### FASE 1 — MVP (Semanas 1 a 8)

#### M1 — Autenticação e Perfil da Empresa
- Login por e-mail + senha (Supabase Auth)
- Perfil da empresa: nome, CNPJ, endereço, logo, e-mail, telefone
- Dados do Responsável Técnico: nome, CREA, dados para ART
- Configurações globais: BDI padrão, encargos sociais, CAA padrão

#### M2 — Clientes
- Cadastro: nome, CPF/CNPJ, telefone, e-mail, endereço completo
- Tipo: pessoa física ou jurídica
- Histórico de obras por cliente
- Busca e filtro

#### M3 — Obras / Projetos
- Criação vinculada ao cliente
- Status: `orçamento → aprovado → em andamento → entregue → cancelado`
- Campos: endereço da obra, nº ART, matrícula do imóvel
- Datas: início previsto, término previsto, entrega real
- Upload do projeto arquitetônico (PDF/imagem — referência)
- Hub central: acesso a todos os sub-módulos da obra

#### M4 — Takeoff Digital (CORE)

**Modo 1 — Manual**
- Digita dimensões cômodo a cômodo
- Nome do ambiente, comprimento, largura, pé-direito
- Tipo de piso, tipo de parede, número de aberturas

**Modo 2 — Takeoff Digital sobre a Planta**

*Etapa A — Upload e Calibração:*
1. Upload da planta baixa (PDF ou imagem)
2. Calibração de escala: clicar em 2 pontos de distância conhecida
3. Informar distância real → sistema calcula `px/metro`
4. Escala salva por planta (não precisa recalibrar)

*Etapa B — Antes de cada medição (formulário obrigatório):*
- **Nome do elemento** (ex: "Sala - Piso", "Fundação Bloco P1", "Viga V3")
- **Tipo de medição:**
  - `Linear (m)` — paredes, perímetros, vigas, tubulações
  - `Área (m²)` — pisos, tetos, revestimentos, formas
  - `Volume (m³)` — concreto, aterro, escavação

*Etapa C — Clique nos vértices:*
- Linear: clique 2 pontos → comprimento calculado com escala
- Área: clique N cantos → polígono fechado → área (Fórmula de Shoelace)
- Volume: clique cantos → m² → **pergunta automática de altura/espessura/profundidade** → m³

*Etapa D — Dados complementares por tipo:*
- **Concreto in loco:** pergunta o fck → exibe traço completo (ver M5-A)
- **Laje:** pergunta espessura
- **Fundação:** pergunta profundidade
- **Parede:** pergunta pé-direito
- **Pisos/revestimentos:** nenhuma pergunta adicional

*Resultado:* lista de medições nomeadas com valor calculado, pronta para o motor de quantitativos.

#### M5 — Motor de Quantitativos (CORE)

**M5-A — Concreto In Loco por fck:**

Quando o usuário selecionar "Concreto in loco" e informar o fck, o sistema exibe automaticamente:
- Traço em volume (cimento:areia:brita)
- Traço em massa
- Relação água/cimento
- Consumo por m³: cimento (kg e sacos), areia (m³), brita (m³), água (litros)
- Abatimento recomendado e classe de consistência
- Cobrimento mínimo por CAA

Tabela de referência (NBR 12655, CP II-E):

| fck | Traço (vol.) | a/c | Cimento (kg/m³) | Sacos/m³ |
|---|---|---|---|---|
| C15 | 1:3,0:4,0 | 0,80 | 280 | 5,6 |
| C20 | 1:2,5:3,5 | 0,68 | 320 | 6,4 |
| C25 | 1:1,8:2,8 | 0,55 | 360 | 7,2 |
| C30 | 1:1,5:2,5 | 0,48 | 400 | 8,0 |
| C35 | 1:1,2:2,0 | 0,42 | 440 | 8,8 |
| C40 | 1:1,0:1,8 | 0,38 | 480 | 9,6 |

**M5-B — Tabelas de composição por elemento:**

Para cada m² ou m³ de cada tipo de elemento, o sistema conhece os insumos necessários. Exemplos:

- `1 m² laje H12 (EPS)` → cimento, areia, brita, vigota 12M, EPS 12/27, malha soldada, escoramento
- `1 m² alvenaria bloco cerâmico 9cm` → blocos (27 un/m²), argamassa assentamento, tempo de pedreiro
- `1 m² piso porcelanato` → porcelanato, argamassa colante AC2, rejunte, espaçadores
- `1 m² revestimento cerâmico parede` → cerâmica, argamassa AC1, rejunte
- `1 m² reboco externo` → argamassa cal+cimento+areia (traço definido), tela metálica
- `1 m² telhado cerâmico colonial` → telhas (14 un/m²), caibros, ripas, cumeeira, pregos

**M5-C — Resultado dos quantitativos:**
- Lista completa de materiais com quantidade calculada e unidade
- Agrupada por categoria (estrutura, alvenaria, acabamentos...)
- Permite ajuste manual antes de gerar orçamento
- Versão salva e auditável

#### M6 — Banco de Preços

- Cadastro manual de materiais e serviços
- Campos: nome, unidade, preço unitário, categoria, observação (ex: "Loja Cassol"), data da última atualização
- Categorias: Serviços Preliminares | Fundação | Estrutura | Alvenaria | Cobertura | Impermeabilização | Revestimentos | Pisos | Esquadrias | Pintura | Instalações Elétricas | Instalações Hidrossanitárias | Louças e Metais | Mão de Obra
- Edição livre a qualquer momento
- **Regra:** alterações de preço NÃO afetam orçamentos já criados

#### M7 — Orçamento (CORE)

- Gerado automaticamente a partir dos quantitativos × preços cadastrados
- Agrupado por etapa de obra (26 etapas padrão)
- BDI configurável por orçamento (padrão do perfil ou personalizado)
- Versionamento: v1, v2, v3... com histórico
- Status: `rascunho → enviado → aprovado → reprovado → revisado`
- **Preço unitário congelado** no momento da criação do orçamento
- Validade configurável (padrão: 30 dias)
- Campo de observações por etapa e por item
- Comparação visual entre versões

#### M8 — Cronograma Físico-Financeiro

- Gerado automaticamente a partir do orçamento
- Distribuição percentual por etapa (baseada no histórico real)
- Diagrama de Gantt visual
- Desembolso mensal calculado
- Curva S (acumulado)
- Ajuste manual de datas por etapa
- Exportável como parte do relatório PDF

#### M9 — PCI Caixa Automática (CORE)

- Preenchimento automático com dados do orçamento + perfil da empresa
- Dados do proprietário puxados do cadastro do cliente
- Dados do RT (nome, CREA, ART) puxados do perfil da empresa
- Campo para número da ART (preenchido manualmente)
- Verificação do custo por m² vs. CUB/ES (alerta se muito fora)
- **Export Excel no formato oficial da Caixa Econômica Federal**
- Checklist de documentação necessária para protocolo

#### M10 — Relatório PDF Profissional

Conteúdo:
1. Capa com logo D'LIMA, nome da obra, cliente, data, número do orçamento
2. Memorial descritivo (gerado automaticamente + campo para personalizar)
3. Planilha orçamentária detalhada por etapa
4. Cronograma físico-financeiro (diagrama + tabela)
5. Dados do Responsável Técnico + espaço para assinatura

Opções de entrega:
- Download PDF
- Envio por e-mail direto do sistema
- Link compartilhável (com validade configurável)

---

### FASE 2 — Financeiro (Semanas 9 a 12)

#### M11 — Lançamentos Financeiros por Obra
- Entradas: recebimentos, medições Caixa, adiantamentos
- Saídas: materiais, mão de obra, honorários, impostos
- Comprovante em anexo (foto ou PDF)
- Status: pago / pendente / atrasado

#### M12 — Fluxo de Caixa
- Visão mensal por obra e consolidada
- Projeção de recebimentos futuros (base: cronograma)
- Saldo real vs. projetado
- Alerta de saldo negativo previsto

#### M13 — Dashboard Financeiro
- Faturamento mensal e anual
- Obras mais lucrativas
- Margem real vs. orçada por obra
- Custo por tipo de serviço

---

### FASE 3 — Campo (Semanas 13 a 16)

#### M14 — Diário de Obras
- Registro diário com fotos (câmera do celular, funciona offline)
- Campos: etapa executada, atividades, mão de obra presente, condição climática, ocorrências
- Relatório semanal automático para o cliente (PDF por e-mail)
- Galeria de fotos por etapa

#### M15 — Alertas e Prazos
- Prazo de entrega de obras chegando (3, 7, 15 dias antes)
- Vencimento de ART/CREA
- Orçamentos sem resposta do cliente (configurável: 7, 15, 30 dias)
- Datas de medição Caixa
- Notificações no sistema + e-mail

#### M16 — Gestão de Documentos
- Pasta por obra: projetos, contratos, ARTs, laudos, fotos
- Controle de versões de projeto
- Link compartilhável para o cliente (com senha opcional)
- Preview de PDF e imagens no navegador

---

### FASE 4 — Equipe e Técnico (quando escalar)

#### M17 — Colaboradores e Acessos
- Convite por e-mail
- Perfis: Admin / Engenheiro / Auxiliar de Campo / Financeiro
- Permissões granulares por módulo
- Log de atividades

#### M18 — Chat Interno
- Conversas por obra e canal geral
- Menções @colaborador
- Compartilhamento de arquivos no chat
- Histórico persistente

#### M19 — Dimensionamento Estrutural com IA
- Calculadoras integradas baseadas no curso do Prof. Matheus Carini
- Skills: eng-fundamentos, eng-cargas, eng-predim, eng-lajes, eng-vigas, eng-pilares, eng-detalhamento
- Memorial de cálculo gerado automaticamente (PDF)
- Vinculado ao projeto e ao orçamento

#### M20 — Viabilidade de Terrenos
- Checklist de análise (zoneamento, TO, CA, recuos, infraestrutura)
- Cálculo financeiro (custo × VGV)
- Relatório de viabilidade para o cliente

#### M21 — Funcionalidades Futuras Identificadas
- Gerador de contrato de obras (Word/PDF com dados do projeto)
- CUB automático (SINDUSCON-ES atualizado mensalmente)
- Histórico de evolução de preços de materiais
- App de vistoria (checklist fotográfico para fiscalização)
- Portal do cliente (acesso externo ao andamento da obra)

---

## 4. Banco de Dados

### 4.1 Tabelas por Grupo

**Grupo 1 — Identidade**
```sql
empresa (id, nome, cnpj, crea, endereco, logo_url, email,
         telefone, dados_rt, config_bdi, config_encargos)

-- Supabase Auth gerencia: usuarios (id, email, nome, avatar_url, perfil)
```

**Grupo 2 — Clientes e Obras**
```sql
clientes (id, nome, cpf_cnpj, telefone, email,
          logradouro, numero, complemento, bairro,
          cidade, estado, cep, tipo, observacoes,
          criado_em)

obras (id, nome, cliente_id, status, tipo,
       logradouro, numero, cidade, estado, cep,
       matricula_imovel, numero_art,
       data_inicio, data_previsao_fim, data_entrega_real,
       valor_contrato, valor_orcado, observacoes,
       criado_em, atualizado_em)

plantas_baixas (id, obra_id, arquivo_url, nome,
                escala_px_por_metro, ordem)

documentos (id, obra_id, nome, tipo, arquivo_url,
            categoria, criado_em)
```

**Grupo 3 — Takeoff e Quantitativos**
```sql
medicoes (id, obra_id, planta_id, nome,
          tipo_medicao, -- 'linear' | 'area' | 'volume'
          vertices,     -- JSON com coordenadas [{x,y}]
          valor_calculado, unidade,
          altura_informada,
          fck,          -- se concreto in loco
          categoria, acabamento,
          criado_em)

quantitativos (id, obra_id, medicao_id, material_id,
               descricao, quantidade_calculada, unidade,
               fck_referencia, traco_descricao,
               ajuste_manual, criado_em)
```

**Grupo 4 — Preços e Orçamento**
```sql
materiais (id, nome, unidade, preco_unitario,
           categoria, observacao, data_atualizacao)

orcamentos (id, obra_id, versao, data_emissao,
            validade_dias, bdi_pct, status,
            valor_total_sem_bdi, valor_total_com_bdi,
            observacoes, criado_em)

orcamento_itens (id, orcamento_id, material_id,
                 etapa, descricao, quantidade,
                 unidade, preco_unitario, -- congelado
                 total_item, ordem_exibicao)
```

**Grupo 5 — Cronograma e Financeiro**
```sql
cronograma_etapas (id, obra_id, nome_etapa,
                   percentual_obra, valor_etapa,
                   data_inicio_prevista, data_fim_prevista,
                   data_inicio_real, data_fim_real,
                   percentual_executado, ordem)

lancamentos_financeiros (id, obra_id, tipo, -- 'entrada'|'saida'
                         descricao, valor,
                         data_lancamento, data_vencimento,
                         status, categoria,
                         comprovante_url, criado_em)
```

**Grupo 6 — Diário e Chat**
```sql
diario_obras (id, obra_id, data_registro,
              etapa_executada, descricao_atividades,
              mao_obra_presente, -- JSON
              condicao_tempo, ocorrencias,
              fotos_urls) -- JSON array

mensagens_chat (id, obra_id, usuario_id,
                conteudo, arquivo_url, criado_em)
```

### 4.2 Regra de Negócio Crítica
> O campo `preco_unitario` em `orcamento_itens` é copiado e **congelado** no momento da criação do orçamento. Atualizações posteriores em `materiais.preco_unitario` não afetam orçamentos existentes. Histórico de preços preservado.

### 4.3 Storage Buckets (Supabase)
```
plantas/          ← imagens das plantas baixas
documentos/       ← ARTs, contratos, projetos PDF
diario-fotos/     ← fotos das obras (comprimidas)
relatorios/       ← PDFs gerados (orçamentos, PCI)
logos/            ← logo da empresa
```

---

## 5. UX e Telas Principais

### 5.1 Navegação
- **Desktop:** sidebar lateral fixa com ícones + labels
- **Mobile:** barra de navegação inferior com 5 ícones principais
- Identidade D'LIMA em todas as telas: dark/gold

### 5.2 Telas do MVP

| Tela | Descrição |
|---|---|
| Login | Autenticação com e-mail/senha, logo D'LIMA |
| Dashboard | Alertas ativos, obras recentes, métricas do mês |
| Clientes | Lista com busca + formulário de cadastro |
| Obras | Lista por status + detalhe (hub central) |
| Banco de Preços | Lista editável por categoria |
| Takeoff Digital | Canvas com planta + ferramentas de medição |
| Quantitativos | Lista gerada automaticamente + ajustes |
| Orçamento | Planilha detalhada por etapa + BDI + versões |
| Cronograma | Gantt interativo + desembolso mensal |
| PCI Caixa | Formulário preenchido + export Excel |
| Relatório PDF | Preview + botão de download/envio |

### 5.3 Fluxo Principal (MVP)
```
Nova Obra → Takeoff Digital → Quantitativos → Orçamento → PCI + PDF
   5 min        15 min          automático      automático   1 clique
```

### 5.4 Comportamento do Takeoff
**Antes de cada medição:**
1. Nome do elemento (obrigatório)
2. Tipo: linear / área / volume

**Durante a medição:**
- Vértices clicáveis sobre a planta
- Cálculo em tempo real com escala

**Após a medição:**
- Pergunta contextual por tipo de elemento:
  - Concreto → fck → exibe traço completo
  - Laje → espessura
  - Fundação → profundidade
  - Parede → pé-direito
  - Piso/revestimento → nenhuma pergunta

---

## 6. Concreto In Loco — Tabela de Traços

Referência: NBR 12655 | Cimento CP II-E 32

| fck | Traço volume | Traço massa | a/c | Cimento kg/m³ | Sacos/m³ | Areia m³ | Brita m³ | Água L |
|---|---|---|---|---|---|---|---|---|
| C15 | 1:3,0:4,0 | 1:3,3:4,4 | 0,80 | 280 | 5,6 | 0,84 | 0,89 | 224 |
| C20 | 1:2,5:3,5 | 1:2,8:3,9 | 0,68 | 320 | 6,4 | 0,80 | 0,85 | 218 |
| C25 | 1:1,8:2,8 | 1:2,0:3,0 | 0,55 | 360 | 7,2 | 0,72 | 0,75 | 198 |
| C30 | 1:1,5:2,5 | 1:1,7:2,7 | 0,48 | 400 | 8,0 | 0,68 | 0,71 | 192 |
| C35 | 1:1,2:2,0 | 1:1,4:2,2 | 0,42 | 440 | 8,8 | 0,65 | 0,68 | 185 |
| C40 | 1:1,0:1,8 | 1:1,2:2,0 | 0,38 | 480 | 9,6 | 0,62 | 0,65 | 182 |

---

## 7. Fases e Cronograma

### Fase 1 — MVP (8 semanas)
| Semana | Entrega |
|---|---|
| 1 | Setup Next.js + Supabase + layout D'LIMA + login |
| 2 | Clientes + Obras + Dashboard |
| 3 | Banco de preços (cadastro manual) |
| 4 | Takeoff Digital — upload + calibração + área |
| 5 | Takeoff Digital — linear + volume + fck + traço |
| 6 | Motor de quantitativos (composições por elemento) |
| 7 | Orçamento (geração + BDI + versionamento) |
| 8 | Cronograma + PCI Caixa + Relatório PDF |

### Fase 2 — Financeiro (4 semanas)
Lançamentos por obra, fluxo de caixa, dashboard financeiro.

### Fase 3 — Campo (4 semanas)
Diário de obras com fotos, alertas de prazos, gestão de documentos.

### Fase 4 — Equipe e Técnico (sob demanda)
Colaboradores, chat, dimensionamento estrutural, portal do cliente.

---

## 8. Custos e Infraestrutura

| Serviço | Plano | Limite gratuito | Custo inicial |
|---|---|---|---|
| Vercel | Hobby | Ilimitado para projetos pessoais | R$ 0 |
| Supabase | Free | 500MB DB + 1GB Storage + 50k usuários | R$ 0 |
| Domínio `app.dlima.eng.br` | Subdomínio | No próprio domínio | R$ 0 |
| **Total mensal** | | | **R$ 0,00** |

Escala paga apenas quando o negócio crescer e ultrapassar os limites gratuitos.

---

## 9. Decisões de Design

| Decisão | Escolha | Motivo |
|---|---|---|
| Multi-tenant? | Não (por enquanto) | Solo agora, escala depois sem reescrever |
| Offline first? | Sim (PWA + IndexedDB) | Uso na obra sem internet |
| Preços importados? | Não | Usuário cadastra manualmente das lojas |
| SINAPI integrado? | Não (fase 1) | Adiciona complexidade, preços manuais suficientes |
| App mobile nativo? | Não | PWA atende o caso de uso atual |
| Congelamento de preços | Sim | Integridade histórica dos orçamentos |
| Traço de concreto | Manual por fck (tabela) | Prático, sem necessidade de dosagem laboratorial |

---

## 10. Próximo Passo

Com este documento aprovado, o próximo passo é criar o **Plano de Implementação** detalhado da Fase 1 (Semanas 1 a 8), com tasks específicas por arquivo, componente e rota.

O projeto começa pelo setup do Next.js + Supabase e primeira tela de login com identidade D'LIMA já funcional e online.
