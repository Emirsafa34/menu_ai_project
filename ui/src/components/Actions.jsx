import { exportRanking, reportRanking } from "../lib/api";

export default function Actions({ start, end, topK, normalize }) {
  const download = async (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
  };

  const onCsv = async () => {
    const { data } = await exportRanking({ start_date: start, end_date: end, top_k: topK });
    alert(data?.saved ? `Sunucuda kaydedildi: ${data.file}` : "CSV üretilemedi");
  };

  const onPdf = async () => {
    const res = await reportRanking({ start_date: start, end_date: end, top_k: topK, normalize });
    const dt = new Date().toISOString().slice(0,19).replace(/[:T]/g,"");
    await download(new Blob([res.data], { type: "application/pdf" }), `ranking_${dt}.pdf`);
  };

  return (
    <div style={{ display: "flex", gap: 8 }}>
      <button onClick={onCsv}>CSV Kaydet</button>
      <button onClick={onPdf}>PDF İndir</button>
    </div>
  );
}
