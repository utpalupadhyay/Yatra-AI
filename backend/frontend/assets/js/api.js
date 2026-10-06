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
    const endpoint = (window.location.protocol === "file:" || window.location.port === "5500" || window.location.port === "3000")
      ? "http://localhost:8000/api/generate-trip"
      : "/api/generate-trip";

    let res;
    try {
      res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (networkErr) {
      throw new Error("Unable to connect to the AI service. Please try again.");
    }

    let data;
    try {
      data = await res.json();
    } catch (parseErr) {
      throw new Error("The AI returned an unexpected response.");
    }

    if (!res.ok) {
      const errMsg = data.error || data.detail || (
        res.status === 401 || res.status === 403
          ? "The AI API key is invalid or expired."
          : res.status === 429
          ? "The AI service is temporarily busy. Please try again."
          : `Server error (${res.status})`
      );
      throw new Error(errMsg);
    }

    if (data.error) {
      throw new Error(data.error);
    }

    if (!data.itinerary) {
      throw new Error("The AI returned an unexpected response.");
    }

    return data;
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
