import ScoreBar from "./ScoreBar";

export default function RankingTable({ rows, query, normalize }) {
  const q = (query||"").trim().toLowerCase();
  const data = rows.filter(r => !q || (r.name||"").toLowerCase().includes(q));
  return (
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr>
          <th>#</th><th>Ürün</th><th>Fiyat</th><th>Marj</th><th>Skor</th>{normalize ? <th>Skor(0–100)</th> : null}
        </tr>
      </thead>
      <tbody>
        {data.map((r) => (
          <tr key={r.product_id} style={{ borderTop: "1px solid #eee" }}>
            <td>{r.rank}</td>
            <td>{r.name}</td>
            <td>{Number(r.price).toFixed(2)}</td>
            <td>{Number(r.margin).toFixed(2)}</td>
            <td><ScoreBar value={r.score} norm={normalize ? r.score_norm : undefined}/></td>
            {normalize ? <td>{Number(r.score_norm).toFixed(1)}</td> : null}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
