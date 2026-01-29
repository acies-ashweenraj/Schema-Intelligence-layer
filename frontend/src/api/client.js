import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
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
<<<<<<< HEAD
/* ---------- KG ---------- */
export async function loadKG(payload) {
  const res = await api.post("/kg/load", payload);
  return res.data;
}

/* ---------- NLP RAG ---------- */
export async function initRAG(payload) {
  const res = await api.post("/nlp-rag/init", payload);
  return res.data;
}
=======

/* ===============================
   CHATBOT
================================ */
>>>>>>> 984335d882a8204dde6c63a7e2f0d97384f6f226

export async function askQuestion(payload) {
  const res = await api.post("/nlp-rag/ask", payload);
  return res.data;
<<<<<<< HEAD
}
=======
}
>>>>>>> 984335d882a8204dde6c63a7e2f0d97384f6f226
