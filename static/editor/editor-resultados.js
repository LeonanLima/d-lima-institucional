// Formatação pura do `resultado` de POST /api/estrutura para exibição.
// Sem DOM, sem canvas — testável em node --test.

const EPS = 0.05; // ignora componentes desprezíveis (kN / kN·m)

export function formatarNumero(v, casas = 1) {
  return Number(v).toFixed(casas).replace(".", ",");
}

// Reações por nó, ordenadas por id. `texto` p/ o painel, `label` compacto p/ o canvas.
export function formatarReacoes(reacoes) {
  return Object.keys(reacoes)
    .map((k) => ({ no: Number(k), ...reacoes[k] }))
    .sort((a, b) => a.no - b.no)
    .map((r) => {
      const partes = [];
      if (Math.abs(r.fx) >= EPS) partes.push(`Fx ${formatarNumero(r.fx)} kN`);
      if (Math.abs(r.fy) >= EPS) partes.push(`Fy ${formatarNumero(r.fy)} kN`);
      if (Math.abs(r.mz) >= EPS) partes.push(`Mz ${formatarNumero(r.mz)} kN·m`);
      const texto = partes.length ? partes.join(", ") : "≈ 0";
      const seta = r.fy > EPS ? "↑" : r.fy < -EPS ? "↓" : "";
      const label = Math.abs(r.fy) >= EPS
        ? `${seta} ${formatarNumero(Math.abs(r.fy))} kN` : "";
      return { no: r.no, fx: r.fx, fy: r.fy, mz: r.mz, texto, label };
    });
}

// Maior deslocamento de translação (mm) entre todos os nós.
export function deslocamentoMaximo(deslocamentos) {
  let melhor = null;
  for (const k of Object.keys(deslocamentos)) {
    const d = deslocamentos[k];
    const mag = Math.hypot(d.ux, d.uy); // mm
    if (melhor === null || mag > melhor.mag) melhor = { no: Number(k), mag };
  }
  if (melhor === null) return null;
  return { no: melhor.no, mm: melhor.mag,
           texto: `Nó ${melhor.no}: ${formatarNumero(melhor.mag, 2)} mm` };
}

// Resumo completo p/ o painel.
export function resumoResultado(resultado) {
  return {
    reacoes: formatarReacoes(resultado.reacoes || {}),
    deslocamentoMax: deslocamentoMaximo(resultado.deslocamentos || {}),
    avisos: resultado.avisos || [],
  };
}
