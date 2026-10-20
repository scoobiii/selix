import React, { useCallback, useEffect, useState } from "react";

const API_BASE = (import.meta.env.VITE_SELIX_API_URL || "").replace(/\/$/, "");

function formatPercent(value) {
  return typeof value === "number" && Number.isFinite(value)
    ? `${value.toFixed(2)}% a.a.`
    : "—";
}

export default function Dashboard() {
  const [snapshot, setSnapshot] = useState(null);
  const [state, setState] = useState("loading");
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/v1/selic/snapshot`, {
        cache: "no-store",
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Error(`API indisponível (HTTP ${response.status})`);
      }
      const data = await response.json();
      const valid =
        data?.status === "current" &&
        data?.selic_atual_serie === 432 &&
        data?.selic_atual_fonte === "BCB SGS 432" &&
        data?.provenance === "runtime:BCB SGS 432" &&
        typeof data?.selic_atual === "number" &&
        Number.isFinite(data.selic_atual) &&
        typeof data?.selic_atual_data_bcb === "string" &&
        data.selic_atual_data_bcb.length > 0;
      if (!valid) {
        throw new Error("Resposta sem proveniência oficial BCB SGS 432");
      }
      setSnapshot(data);
      setState("current");
      setError("");
    } catch (err) {
      // Do not keep showing the last successful rate as if it were current.
      setSnapshot(null);
      setState("unavailable");
      setError(err instanceof Error ? err.message : "Falha ao consultar SELIX");
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = window.setInterval(refresh, 60_000);
    return () => window.clearInterval(id);
  }, [refresh]);

  const current = state === "current" && snapshot;

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24, fontFamily: "system-ui, sans-serif", color: "#17202a" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
        <div>
          <h1 style={{ marginBottom: 4 }}>SELIX — Inteligência Econômica</h1>
          <p style={{ marginTop: 0, color: "#52606d" }}>Meta Selic observada no BCB; modelo ideal separado da taxa oficial.</p>
        </div>
        <button onClick={refresh} style={{ padding: "10px 14px", cursor: "pointer" }}>Atualizar agora</button>
      </header>

      <section aria-live="polite" style={{ marginTop: 20, padding: 16, border: "1px solid #d5dce3", borderRadius: 10 }}>
        <strong>Status: </strong>
        {state === "loading" ? "Consultando BCB…" : state === "current" ? "CURRENT — BCB SGS 432 validado" : "INDISPONÍVEL"}
        {state === "unavailable" && <p role="alert">{error}. Nenhuma taxa antiga é exibida como atual.</p>}
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: 14, marginTop: 18 }}>
        <article style={{ border: "1px solid #d5dce3", borderRadius: 10, padding: 18 }}>
          <h2 style={{ fontSize: 14, color: "#52606d" }}>Meta Selic oficial</h2>
          <p style={{ fontSize: 28, fontWeight: 700 }}>{current ? formatPercent(snapshot.selic_atual) : "—"}</p>
          <p>Observação BCB: {current ? snapshot.selic_atual_data_bcb : "—"}</p>
        </article>
        <article style={{ border: "1px solid #d5dce3", borderRadius: 10, padding: 18 }}>
          <h2 style={{ fontSize: 14, color: "#52606d" }}>Selic ideal (modelo)</h2>
          <p style={{ fontSize: 28, fontWeight: 700 }}>{current ? formatPercent(snapshot.selic_ideal) : "—"}</p>
          <p>Estimativa do modelo SELIX, não taxa oficial.</p>
        </article>
        <article style={{ border: "1px solid #d5dce3", borderRadius: 10, padding: 18 }}>
          <h2 style={{ fontSize: 14, color: "#52606d" }}>Diferencial do modelo</h2>
          <p style={{ fontSize: 28, fontWeight: 700 }}>{current ? `${snapshot.diferencial.toFixed(2)} p.p.` : "—"}</p>
          <p>Meta observada menos Selic ideal.</p>
        </article>
      </section>

      <footer style={{ marginTop: 22, fontSize: 13, color: "#52606d" }}>
        {current ? (
          <>
            Fonte: {snapshot.selic_atual_fonte} (série {snapshot.selic_atual_serie}) ·
            Consultado em: {snapshot.fetched_at} · Proveniência: {snapshot.provenance}
          </>
        ) : "Aguardando uma resposta oficial validada."}
        <p>O snapshot estático do repositório não é usado como fallback.</p>
      </footer>
    </main>
  );
}
