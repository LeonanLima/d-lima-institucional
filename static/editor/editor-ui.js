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
    const cd = m.cargas.find((c) => c.tipo === "distribuida" && c.elemento === selecionado.id);
    html += `<h3>Barra ${selecionado.id}</h3>
      <label>Tipo</label>
      <select id="p-tipo">${["viga","pilar","fundacao"].map((t)=>`<option ${t===selecionado.tipo?"selected":""}>${t}</option>`).join("")}</select>
      <div class="row"><div><label>bw (cm)</label><input id="p-bw" type="number" value="${selecionado.secao.bw}"></div>
      <div><label>h (cm)</label><input id="p-h" type="number" value="${selecionado.secao.h}"></div></div>
      <label>Carga distribuída (kN/m)</label><input id="p-cd" type="number" value="${cd ? cd.valor : ""}">`;
  }

  if (selecionado && selecionado.x !== undefined) {
    const v = m.vinculos.find((x) => x.no === selecionado.id) || { ux: false, uy: false, rz: false };
    const cn = m.cargas.find((c) => c.tipo === "nodal" && c.no === selecionado.id) || { fx: 0, fy: 0, mz: 0 };
    const chk = (k) => (v[k] ? "checked" : "");
    html += `<h3>Nó ${selecionado.id}</h3>
      <div class="row"><div><label>x (m)</label><input id="p-nx" type="number" step="0.25" value="${selecionado.x}"></div>
      <div><label>y (m)</label><input id="p-ny" type="number" step="0.25" value="${selecionado.y}"></div></div>
      <label>Vínculo (apoio)</label>
      <div class="row" style="align-items:center">
        <label style="font-weight:normal"><input type="checkbox" id="p-ux" ${chk("ux")} style="width:auto"> ux</label>
        <label style="font-weight:normal"><input type="checkbox" id="p-uy" ${chk("uy")} style="width:auto"> uy</label>
        <label style="font-weight:normal"><input type="checkbox" id="p-rz" ${chk("rz")} style="width:auto"> rz</label>
      </div>
      <label>Cargas nodais</label>
      <div class="row"><div><label style="font-weight:normal">Fx (kN)</label><input id="p-fx" type="number" value="${cn.fx}"></div>
      <div><label style="font-weight:normal">Fy (kN)</label><input id="p-fy" type="number" value="${cn.fy}"></div>
      <div><label style="font-weight:normal">Mz (kN·m)</label><input id="p-mz" type="number" value="${cn.mz}"></div></div>`;
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
  on("#p-cd", "change", (e) => cbs.aoSetCargaDistribuida(e.target.value === "" ? null : +e.target.value));
  on("#p-nx", "change", (e) => cbs.aoEditarNo({ x: +e.target.value }));
  on("#p-ny", "change", (e) => cbs.aoEditarNo({ y: +e.target.value }));
  const lerVinculo = () => cbs.aoSetVinculo({
    ux: painelEl.querySelector("#p-ux").checked,
    uy: painelEl.querySelector("#p-uy").checked,
    rz: painelEl.querySelector("#p-rz").checked,
  });
  ["#p-ux", "#p-uy", "#p-rz"].forEach((id) => on(id, "change", lerVinculo));
  const lerCargaNodal = () => cbs.aoSetCargaNodal({
    fx: +painelEl.querySelector("#p-fx").value,
    fy: +painelEl.querySelector("#p-fy").value,
    mz: +painelEl.querySelector("#p-mz").value,
  });
  ["#p-fx", "#p-fy", "#p-mz"].forEach((id) => on(id, "change", lerCargaNodal));
  on("#p-export", "click", () => cbs.aoExportar());
  on("#p-import", "click", () => painelEl.querySelector("#p-file").click());
  on("#p-file", "change", (e) => cbs.aoImportar(e.target.files[0]));
  on("#p-calc", "click", () => cbs.aoCalcular());
  on("#p-rel", "click", () => cbs.aoAbrirRelatorio());
}
