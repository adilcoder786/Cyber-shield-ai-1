import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
});

// Normalize errors into a consistent, human-readable shape so every page
// can render error states the same way.
function normalizeError(error) {
  if (error.response) {
    const detail = error.response.data?.detail;
    if (Array.isArray(detail)) {
      return detail.map((d) => d.msg).join(", ");
    }
    if (typeof detail === "string") return detail;
    return `Request failed (${error.response.status})`;
  }
  if (error.request) {
    return "Could not reach the CyberShield AI backend. Is the API server running?";
  }
  return error.message || "Something went wrong.";
}

export async function scanUrl(url) {
  try {
    const { data } = await api.post("/api/scan/url", { url });
    return data;
  } catch (e) {
    throw new Error(normalizeError(e));
  }
}

export async function scanMessage(content, channel, sender) {
  try {
    const { data } = await api.post("/api/scan/message", { content, channel, sender: sender || null });
    return data;
  } catch (e) {
    throw new Error(normalizeError(e));
  }
}

export async function scanFile(file) {
  try {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.post("/api/scan/file", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  } catch (e) {
    throw new Error(normalizeError(e));
  }
}

export async function getHistory(params) {
  try {
    const { data } = await api.get("/api/history", { params });
    return data;
  } catch (e) {
    throw new Error(normalizeError(e));
  }
}

export async function deleteScan(id) {
  try {
    const { data } = await api.delete(`/api/history/${id}`);
    return data;
  } catch (e) {
    throw new Error(normalizeError(e));
  }
}

export async function getStats() {
  try {
    const { data } = await api.get("/api/stats/summary");
    return data;
  } catch (e) {
    throw new Error(normalizeError(e));
  }
}
