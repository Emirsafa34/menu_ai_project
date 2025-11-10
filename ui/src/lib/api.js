import axios from "axios";
const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE, timeout: 15000 });

export const getRanking = (params) => api.get("/ranking/", { params });
export const getRankingByDay = (params) => api.get("/ranking/by_day", { params });
export const exportRanking = (params) => api.get("/ranking/export", { params });
export const reportRanking = (params) => api.get("/ranking/report", { params, responseType: "blob" });

export default api;
