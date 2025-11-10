import { useEffect, useMemo, useState } from "react";
import api from "./api";
import "./styles.css";

import {
  ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend,
  PieChart, Pie, Cell,
} from "recharts";

function App() {
  const [startDate, setStartDate] = useState("2025-09-10");
  const [endDate, setEndDate] = useState("2025-09-20");
  const [topK, setTopK] = useState(10);
  const [normalize, setNormalize] = useState(true);
  const [q, setQ] = useState("");

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  const [selectedId, setSelectedId] = useState(null);
  const [series, setSeries] = useState([]);   // {date, score, score_norm}
  const [share, setShare] = useState([]);     // {product_id, name, sales_count}
  const [loadingSeries, setLoadingSeries] = useState(false);
  const [loadingShare, setLoadingShare] = useState(false);

  const fmtTL  = (v) => new Intl.NumberFormat("tr-TR",{style:"currency",currency:"TRY",maximumFractionDigits:0}).format(v);
  const fmtPct = (v) => `${(Number(v) * 100).toFixed(0)}%`;

  const normalizeSeries = (arr) => {
    if (!arr || arr.length === 0) return [];
    const vals = arr.map(d => Number(d.score)).filter(Number.isFinite);
    const min = Math.min(...vals);
    const max = Math.max(...vals);
    const denom = max - min || 1;
    return arr.map(d => ({
      ...d,
      score_norm: Math.round(((Number(d.score) - min) / denom) * 100 * 10) / 10, // 0–100, 1 ondalık
    }));
  };

  // ranking
  const fetchRanking = async () => {
    setLoading(true);
    try {
      const res = await api.get("/ranking/", {
        params: { start_date: startDate, end_date: endDate, top_k: topK, normalize },
      });
      const data = res.data || [];
      setRows(data);
      if (!selectedId && data.length > 0) setSelectedId(data[0].product_id);
    } catch {
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  // series
  const fetchSeries = async (pid) => {
    if (!pid) return;
    setLoadingSeries(true);
    try {
      const res = await api.get("/ranking/series", {
        params: { product_id: pid, start_date: startDate, end_date: endDate },
      });
      setSeries(normalizeSeries(res.data || []));
    } catch {
      setSeries([]);
    } finally {
      setLoadingSeries(false);
    }
  };

  // share
  const fetchShare = async () => {
    setLoadingShare(true);
    try {
      const res = await api.get("/ranking/share", {
        params: { start_date: startDate, end_date: endDate, top_k: topK },
      });
      setShare(res.data || []);
    } catch {
      setShare([]);
    } finally {
      setLoadingShare(false);
    }
  };

  const downloadCSV = async () => {
    try {
      const res = await api.get("/ranking/export", {
        params: { start_date: startDate, end_date: endDate, top_k: topK, normalize },
      });
      alert(`CSV hazırlandı: ${res.data.file}`);
    } catch {
      alert("CSV üretilemedi.");
    }
  };

  const downloadPDF = async () => {
    try {
      const res = await api.get("/ranking/report", {
        params: { start_date: startDate, end_date: endDate, top_k: topK, normalize },
        responseType: "blob",
      });
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${startDate}_${endDate}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      alert("PDF indirilemedi.");
    }
  };

  // ilk yük
  useEffect(() => {
    fetchRanking().then(fetchShare);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // parametre değişince
  useEffect(() => {
    fetchRanking();
    fetchShare();
    if (selectedId) fetchSeries(selectedId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startDate, endDate, topK, normalize]);

  // seçim değişince
  useEffect(() => {
    if (selectedId) fetchSeries(selectedId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId]);

  // filtre
  const filtered = useMemo(() => {
    if (!q) return rows;
    const s = q.toLowerCase();
    return rows.filter(r => (r.name || "").toLowerCase().includes(s));
  }, [rows, q]);

  // seçili ürün adı
  const selectedName = useMemo(() => {
    const r = rows.find(x => x.product_id === selectedId);
    return r?.name || "-";
  }, [rows, selectedId]);

  const PIE_COLORS = ["#2563eb","#f59e0b","#10b981","#ef4444","#8b5cf6","#14b8a6","#eab308","#22c55e","#f97316","#3b82f6"];

  return (
    <div className="container">
      <div className="h1">Menu AI – Ürün Sıralama <span className="badge">beta</span></div>

      {/* Controls */}
      <div className="panel controls">
        <div className="field">
          <label className="label">Başlangıç</label>
          <input className="input" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
        </div>
        <div className="field">
          <label className="label">Bitiş</label>
          <input className="input" type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
        </div>
        <div className="field sm">
          <label className="label">En İyi K</label>
          <input className="input" type="number" min={1} max={100} value={topK} onChange={e => setTopK(parseInt(e.target.value || 1))} />
        </div>
        <div className="field xs">
          <label className="label">Normalize</label>
          <label style={{display:"flex",alignItems:"center",gap:8}}>
            <input className="checkbox" type="checkbox" checked={normalize} onChange={e => setNormalize(e.target.checked)} />
          </label>
        </div>
        <div className="field" style={{gridColumn:"span 4"}}>
          <label className="label">Arama</label>
          <input className="input" placeholder="Ürün adı..." value={q} onChange={e => setQ(e.target.value)} />
        </div>
        <div className="right">
          <button className="btn" onClick={downloadCSV}>CSV</button>
          <button className="btn" onClick={downloadPDF}>PDF</button>
          <button className="btn primary" onClick={fetchRanking} disabled={loading}>
            {loading ? "Yükleniyor..." : "Yenile"}
          </button>
        </div>
      </div>

      {/* Table + Charts */}
      <div className="grid-2" style={{marginTop:12}}>
        {/* Table */}
        <div className="table-wrap card">
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Ürün</th>
                  <th style={{textAlign:"right"}}>Fiyat</th>
                  <th style={{textAlign:"right"}}>Marj</th>
                  <th style={{textAlign:"right"}}>Skor</th>
                  <th style={{textAlign:"right"}}>Skor(0–100)</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr><td colSpan={6} className="footerNote">Kayıt yok.</td></tr>
                ) : filtered.map(r => (
                  <tr
                    key={r.product_id}
                    className={r.product_id === selectedId ? "selected" : undefined}
                    onClick={() => setSelectedId(r.product_id)}
                    style={{ cursor: "pointer" }}
                  >
                    <td>{r.rank}</td>
                    <td>{r.name}</td>
                    <td className="num">{fmtTL(r.price)}</td>
                    <td className="num">{fmtPct(r.margin)}</td>
                    <td className="num">{Number(r.score).toFixed(4)}</td>
                    <td className="num">{r.score_norm ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Charts */}
        <div className="grid-2">
          <div className="chartCard">
            <div className="label" style={{marginBottom:8}}>Günlük Skor Serisi • {selectedName}</div>
            <div style={{ height: 260 }}>
              {loadingSeries ? (
                <div className="footerNote">Yükleniyor…</div>
              ) : series.length === 0 ? (
                <div className="footerNote">Veri yok.</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={series} margin={{left:8,right:8,top:8,bottom:8}}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" interval="preserveStartEnd" />
                    <YAxis />
                    <Tooltip formatter={(v, n) => [Number(v).toFixed(2), n === "score_norm" ? "score(0–100)" : "score"]} />
                    <Legend />
                    <Line type="monotone" dataKey={normalize ? "score_norm" : "score"} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className="chartCard">
            <div className="label" style={{marginBottom:8}}>Satış Payı (Adet) • {startDate} → {endDate}</div>
            <div style={{ height: 260 }}>
              {loadingShare ? (
                <div className="footerNote">Yükleniyor…</div>
              ) : share.length === 0 ? (
                <div className="footerNote">Veri yok.</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart margin={{ right: 100 }}>
                    <Pie
                      data={share}
                      dataKey="sales_count"
                      nameKey="name"
                      cx="35%"
                      cy="50%"
                      outerRadius={90}
                      label={false}         /* etiketleri kapat */
                      labelLine={false}
                    >
                      {share.map((_, i) => (
                        <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v, _n, p) => [v, p?.payload?.name]} />
                    <Legend layout="vertical" verticalAlign="middle" align="right" />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

export default App;
