import { useState, useEffect } from "react";

export default function Filters({ onChange }) {
  const [start, setStart] = useState("2025-09-01");
  const [end, setEnd] = useState("2025-09-30");
  const [topK, setTopK] = useState(10);
  const [query, setQuery] = useState("");
  const [normalize, setNormalize] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => onChange({ start, end, topK, query, normalize }), 300);
    return () => clearTimeout(t);
  }, [start, end, topK, query, normalize]);

  return (
    <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(6, minmax(0,1fr))", alignItems: "end" }}>
      <div><label>Başlangıç</label><input type="date" value={start} onChange={e=>setStart(e.target.value)} /></div>
      <div><label>Bitiş</label><input type="date" value={end} onChange={e=>setEnd(e.target.value)} /></div>
      <div><label>Top-K</label><input type="number" min={1} max={100} value={topK} onChange={e=>setTopK(parseInt(e.target.value||"1"))} /></div>
      <div style={{ gridColumn: "span 2" }}><label>Ürün Ara</label><input placeholder="Ürün adı..." value={query} onChange={e=>setQuery(e.target.value)} /></div>
      <div><label>Normalize</label><br/><input type="checkbox" checked={normalize} onChange={e=>setNormalize(e.target.checked)} /></div>
    </div>
  );
}
