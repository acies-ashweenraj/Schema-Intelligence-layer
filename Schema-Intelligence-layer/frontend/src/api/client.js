import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
});

/* ===============================
   METADATA
================================ */

export async function generateMetadata(payload, output_dir = "logs") {
  const res = await api.post("/metadata/generate", { ...payload, output_dir });
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

export async function runHybridMapping(payload, output_dir = "logs") {
  const res = await api.post("/mapping/hybrid", { ...payload, output_dir });
  return res.data;
}

export function getMappingDownloadUrl(path) {
  return `http://localhost:8000/mapping/download?path=${encodeURIComponent(
    path
  )}`;
}

/* ===============================
   NL2SQL / CHAT
================================ */

export async function askQuestion(payload) {
  const res = await api.post("/nl2sql/chat", payload);
  return res.data;
}
