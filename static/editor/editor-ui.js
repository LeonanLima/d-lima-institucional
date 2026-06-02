// Liga a toolbar e renderiza o painel de propriedades.
// `cbs` = { aoMudarModo, aoEditarElemento, aoEditarMaterial,
//           aoExportar, aoImportar, aoCalcular }

export function ligarToolbar(toolbarEl, cbs) {
  toolbarEl.querySelectorAll("button").forEach((b) => {
    b.addEventListener("click", () => {
      toolbarEl.querySelectorAll("button").forEach((x) => x.classList.remove("ativo"));
      b.classList.add("ativo");
      cbs.aoMudarModo(b.dataset.modo);
    });
  });
}

export function mostrarBanner(bannerEl, msgs) {
  if (!msgs || msgs.length === 0) { bannerEl.style.display = "none"; return; }
  bannerEl.innerHTML = Array.isArray(msgs) ? msgs.join("<br>") : msgs;
  bannerEl.style.display = "block";
  clearTimeout(bannerEl._t);
  bannerEl._t = setTimeout(() => { bannerEl.style.display = "none"; }, 6000);
}

export function renderPainel(painelEl, m, selecionado, cbs, resumo = null, relatorioId = null) {
  const mat = m.material;
  let html = `<h3>Material</h3>
    <label>fck (MPa)</label><input id="p-fck" type="number" value="${mat.fck}">
    <label>fyk (MPa)</label><input id="p-fyk" type="number" value="${mat.fyk}">
    <label>CAA</label><select id="p-caa">${[1,2,3,4].map((c)=>`<option ${c===mat.CAA?"selected":""}>${c}</option>`).join("")}</select>
    <label>Agregado</label>
    <select id="p-agr">${["basalto","granito","gnaisse","calcario","arenito"].map((a)=>`<option ${a===mat.agregado?"selected":""}>${a}</option>`).join("")}</select>`;

  if (selecionado && selecionado.secao) {
    html += `<h3>Barra ${selecionado.id}</h3>
      <label>Tipo</label>
      <select id="p-tipo">${["viga","pilar","fundacao"].map((t)=>`<option ${t===selecionado.tipo?"selected":""}>${t}</option>`).join("")}</select>
      <div class="row"><div><label>bw (cm)</label><input id="p-bw" type="number" value="${selecionado.secao.bw}"></div>
      <div><label>h (cm)</label><input id="p-h" type="number" value="${selecionado.secao.h}"></div></div>`;
  }

  if (resumo) {
    html += `<h3>Resultados</h3>`;
    if (resumo.deslocamentoMax)
      html += `<p><b>Desloc. máx:</b> ${resumo.deslocamentoMax.texto}</p>`;
    html += `<div style="font-size:12px;line-height:1.6">` +
      resumo.reacoes.map((r) => `<div>Nó ${r.no}: ${r.texto}</div>`).join("") +
      `</div>`;
    if (resumo.avisos && resumo.avisos.length)
      html += resumo.avisos.map((a) =>
        `<div style="color:#991b1b;margin-top:4px">⚠ ${a}</div>`).join("");
    if (relatorioId)
      html += `<button class="primary" id="p-rel" style="background:#0056b3;margin-top:8px">Ver relatório completo →</button>`;
  }

  html += `<h3>Arquivo</h3>
    <div class="row"><button id="p-export">Exportar</button><button id="p-import">Importar</button></div>
    <input id="p-file" type="file" accept="application/json" style="display:none">
    <button class="primary" id="p-calc">Calcular →</button>`;
  painelEl.innerHTML = html;

  const on = (id, ev, fn) => { const e = painelEl.querySelector(id); if (e) e.addEventListener(ev, fn); };
  on("#p-fck", "change", (e) => cbs.aoEditarMaterial({ fck: +e.target.value }));
  on("#p-fyk", "change", (e) => cbs.aoEditarMaterial({ fyk: +e.target.value }));
  on("#p-caa", "change", (e) => cbs.aoEditarMaterial({ CAA: +e.target.value }));
  on("#p-agr", "change", (e) => cbs.aoEditarMaterial({ agregado: e.target.value }));
  on("#p-tipo", "change", (e) => cbs.aoEditarElemento({ tipo: e.target.value }));
  on("#p-bw", "change", (e) => cbs.aoEditarElemento({ secao: { bw: +e.target.value } }));
  on("#p-h", "change", (e) => cbs.aoEditarElemento({ secao: { h: +e.target.value } }));
  on("#p-export", "click", () => cbs.aoExportar());
  on("#p-import", "click", () => painelEl.querySelector("#p-file").click());
  on("#p-file", "change", (e) => cbs.aoImportar(e.target.files[0]));
  on("#p-calc", "click", () => cbs.aoCalcular());
  on("#p-rel", "click", () => cbs.aoAbrirRelatorio());
}
