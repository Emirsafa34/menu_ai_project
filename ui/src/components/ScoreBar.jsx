export default function ScoreBar({ value, norm }) {
  const v = typeof norm === "number" ? norm : undefined;
  const width = v !== undefined ? `${Math.round(v)}%` : "0%";
  const bg = v !== undefined ? `linear-gradient(90deg, #4ade80 ${width}, #e5e7eb ${width})` : "#e5e7eb";
  return <div title={v !== undefined ? `${v.toFixed(0)} / 100` : value?.toFixed?.(3)} style={{ height: 10, borderRadius: 6, background: bg, minWidth: 120 }}/>;
}
