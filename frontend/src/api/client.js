import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
});

/* ===============================
   METADATA
================================ */

export async function generateMetadata(payload) {
  const res = await api.post("/metadata/generate", payload);
  return res.data;
}

export function getMetadataDownloadUrl(path) {
  return `http://localhost:8000/metadata/download?path=${encodeURIComponent(
    path
  )}`;
}

/* ===============================
   MAPPING
================================ */

export async function runHybridMapping(payload) {
  const res = await api.post("/mapping/hybrid", payload);
  return res.data;
}

export function getMappingDownloadUrl(path) {
  return `http://localhost:8000/mapping/download?path=${encodeURIComponent(
    path
  )}`;
}

/* ===============================
   CHATBOT
================================ */

export async function askQuestion(payload) {
  const res = await api.post("/nlp-rag/ask", payload);
  return res.data;
}
