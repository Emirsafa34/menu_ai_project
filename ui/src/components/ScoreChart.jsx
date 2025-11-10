import { ResponsiveContainer, BarChart, XAxis, YAxis, Tooltip, Bar } from "recharts";

export default function ScoreChart({ rows, normalize }) {
  const data = rows.map(r => ({ name: r.name, score: normalize && typeof r.score_norm === "number" ? r.score_norm : r.score }));
  return (
    <div style={{ height: 280 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-25} textAnchor="end" height={60}/>
          <YAxis/>
          <Tooltip/>
          <Bar dataKey="score" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
