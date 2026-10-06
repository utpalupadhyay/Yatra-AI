/**
 * Yatra AI — API Client
 * Communicates with FastAPI backend. API key is NEVER exposed here.
 */

// Dynamically use relative /api/v1 when served by backend (Vercel or local FastAPI),
// or localhost:8000 when opened via Live Server (port 5500/3000) or file://
const API_BASE = (window.location.protocol === "file:" || window.location.port === "5500" || window.location.port === "3000")
  ? "http://localhost:8000/api/v1"
  : "/api/v1";

const api = {

  async generateTrip(payload) {
    const res = await fetch(`${API_BASE}/trip/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error: ${res.status}`);
    }
    return res.json();
  },

  async replanTrip(payload) {
    const res = await fetch(`${API_BASE}/trip/replan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error: ${res.status}`);
    }
    return res.json();
  },

  async chat(payload) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error: ${res.status}`);
    }
    return res.json();
  },

  async getPackingList(payload) {
    const res = await fetch(`${API_BASE}/trip/packing`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error: ${res.status}`);
    }
    return res.json();
  },

  async optimizeBudget(params) {
    const url = new URL(`${API_BASE}/trip/optimize-budget`);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    const res = await fetch(url, { method: "POST" });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error: ${res.status}`);
    }
    return res.json();
  },

  async healthCheck() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      return res.ok;
    } catch {
      return false;
    }
  },
};
