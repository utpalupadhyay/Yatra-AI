/**
 * Yatra AI — Main Application JavaScript
 * Orchestrates all UI interactions, state management, and AI feature calls.
 */

"use strict";

// ── App State ─────────────────────────────────────
let selectedInterests = [];

const state = {
  currentTrip: null,          // raw itinerary text from Gemma 4
  interactionId: null,        // Gemma 4 interaction ID
  chatConversationId: null,   // for multi-turn chat
  formData: null,             // last submitted form data
  latestTripRequest: null,    // stored request for retry
  language: "english",
  selectedInterests: [],      // mirror of selected interests array
};

let isGenerating = false;

// ── DOM Ready ─────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initParticles();
  initNavbar();
  initInterestChips();
  initBudgetCalculator();
  initChatTextarea();
  tripForm.addEventListener("submit", handleFormSubmit);

  // Check backend health on load
  api.healthCheck().then((ok) => {
    if (!ok) {
      console.warn("Backend not reachable. Ensure FastAPI is running on port 8000.");
    }
  });
});

// ══════════════════════════════════════════════════
//  INIT HELPERS
// ══════════════════════════════════════════════════

function initParticles() {
  const container = document.getElementById("particles");
  if (!container) return;
  for (let i = 0; i < 20; i++) {
    const p = document.createElement("div");
    p.className = "particle";
    const size = Math.random() * 6 + 2;
    p.style.cssText = `
      width:${size}px; height:${size}px;
      left:${Math.random() * 100}%;
      animation-duration:${Math.random() * 15 + 10}s;
      animation-delay:${Math.random() * -20}s;
    `;
    container.appendChild(p);
  }
}

function initNavbar() {
  const navbar = document.getElementById("navbar");
  window.addEventListener("scroll", () => {
    navbar.classList.toggle("scrolled", window.scrollY > 60);
  });
  document.getElementById("hamburger").addEventListener("click", () => {
    const links = document.querySelector(".nav-links");
    if (links) {
      links.style.display = links.style.display === "flex" ? "none" : "flex";
      links.style.flexDirection = "column";
      links.style.position = "absolute";
      links.style.top = "70px";
      links.style.right = "16px";
      links.style.background = "var(--bg2)";
      links.style.border = "1px solid var(--border)";
      links.style.borderRadius = "12px";
      links.style.padding = "16px";
      links.style.gap = "12px";
    }
  });
}

const toggleInterest = (interest) => {
  selectedInterests = selectedInterests.includes(interest)
    ? selectedInterests.filter((item) => item !== interest)
    : [...selectedInterests, interest];
  state.selectedInterests = selectedInterests;
  updateInterestsUI();
};

function updateInterestsUI() {
  document.querySelectorAll(".interest-chip").forEach((chip) => {
    const val = chip.getAttribute("data-interest") || chip.textContent.trim();
    const isSelected = selectedInterests.includes(val);
    chip.classList.toggle("selected", isSelected);
    chip.setAttribute("aria-pressed", isSelected ? "true" : "false");
  });
}

function initInterestChips() {
  document.querySelectorAll(".interest-chip").forEach((chip) => {
    chip.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const interest = chip.getAttribute("data-interest") || chip.textContent.trim();
      toggleInterest(interest);
    });
  });
}

function initBudgetCalculator() {
  const budgetInput = document.getElementById("budget");
  const travelersInput = document.getElementById("numTravelers");
  const perPersonEl = document.getElementById("budgetPerPerson");

  function updatePerPerson() {
    const b = parseFloat(budgetInput.value) || 0;
    const t = parseInt(travelersInput.value) || 1;
    if (b > 0) {
      perPersonEl.textContent = `≈ ₹${Math.round(b / t).toLocaleString("en-IN")} per person`;
    } else {
      perPersonEl.textContent = "";
    }
  }
  budgetInput.addEventListener("input", updatePerPerson);
  travelersInput.addEventListener("input", updatePerPerson);
}

function initChatTextarea() {
  const textarea = document.getElementById("chatInput");
  textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
  });
}

// ══════════════════════════════════════════════════
//  LANGUAGE
// ══════════════════════════════════════════════════

function setLanguage(lang) {
  state.language = lang;
  document.getElementById("btn-en").classList.toggle("active", lang === "english");
  document.getElementById("btn-hi").classList.toggle("active", lang === "hindi");
}

// ══════════════════════════════════════════════════
//  FORM: TRIP GENERATION
// ══════════════════════════════════════════════════

const tripForm = document.getElementById("tripForm");

function getFormData() {
  const from = document.getElementById("origin").value.trim();
  const destination = document.getElementById("destination").value.trim();
  const days = parseInt(document.getElementById("numDays").value);
  const travelers = parseInt(document.getElementById("numTravelers").value);
  const budget = parseFloat(document.getElementById("budget").value);
  const accommodation = document.getElementById("accommodation").value;
  const foodPreference = document.getElementById("foodPref").value;
  const specialRequests = document.getElementById("specialRequests").value.trim() || "";

  // Validation
  if (!from) { alert("Please enter your starting location."); return null; }
  if (!destination) { alert("Please enter your destination."); return null; }
  if (!days || days < 1) { alert("Please enter a valid number of days."); return null; }
  if (!budget || budget < 500) { alert("Budget must be at least ₹500."); return null; }
  if (!travelers || travelers < 1) { alert("Please enter the number of travelers."); return null; }

  // Clean object as specified in Requirement 2:
  const tripData = {
    from,
    destination,
    days,
    travelers,
    budget,
    interests: [...selectedInterests],
    accommodation,
    foodPreference,
    specialRequests,
    // compatibility properties
    origin: from,
    num_days: days,
    num_travelers: travelers,
    food_preference: foodPreference,
    special_requests: specialRequests || null,
    language: state.language || "english",
  };

  return tripData;
}

function formatErrorMessage(err) {
  const raw = (err && err.message) ? err.message : String(err || "");
  const lower = raw.toLowerCase();

  if (lower.includes("not configured") || lower.includes("gemma_api_key") || lower.includes("missing api key")) {
    return "AI service is not configured. Please add GEMMA_API_KEY to the server environment.";
  }
  if (lower.includes("invalid") || lower.includes("expired") || lower.includes("401") || lower.includes("403")) {
    return "The AI API key is invalid or expired.";
  }
  if (lower.includes("busy") || lower.includes("rate limit") || lower.includes("quota") || lower.includes("429")) {
    return "The AI service is temporarily busy. Please try again.";
  }
  if (lower.includes("unable to connect") || lower.includes("network") || lower.includes("failed to fetch")) {
    return "Unable to connect to the AI service. Please try again.";
  }
  if (lower.includes("unexpected response") || lower.includes("malformed")) {
    return "The AI returned an unexpected response.";
  }

  // Never return just "Something went wrong"
  if (raw.trim() === "" || raw === "Something went wrong" || raw === "Internal Server Error") {
    return "Unable to generate trip. Please verify server settings and try again.";
  }

  return raw;
}

async function executeGenerateTrip(tripData) {
  if (isGenerating) return; // Prevent duplicate requests
  isGenerating = true;

  state.formData = tripData;
  state.latestTripRequest = tripData;

  showLoading();
  startLoadingStepAnimation();

  try {
    const result = await api.generateTrip(tripData);
    if (result && result.success && result.itinerary) {
      state.currentTrip = result.itinerary;
      state.interactionId = result.interaction_id;
      showResult(result, tripData);
    } else {
      const err = (result && result.error) ? result.error : "The AI returned an unexpected response.";
      showError(formatErrorMessage(err));
    }
  } catch (err) {
    showError(formatErrorMessage(err));
  } finally {
    isGenerating = false;
    resetBtn();
  }
}

async function handleFormSubmit(e) {
  e.preventDefault();
  if (isGenerating) return;
  const data = getFormData();
  if (!data) return;
  await executeGenerateTrip(data);
}

// ══════════════════════════════════════════════════
//  OUTPUT STATE MANAGEMENT
// ══════════════════════════════════════════════════

function showLoading() {
  const btn = document.getElementById("generateBtn");
  btn.disabled = true;
  const btnText = btn.querySelector(".btn-text");
  const btnLoading = btn.querySelector(".btn-loading");
  if (btnText) btnText.style.display = "none";
  if (btnLoading) {
    btnLoading.style.display = "inline";
    btnLoading.innerHTML = '<span class="spinner"></span> Generating your AI trip...';
  }

  document.getElementById("outputEmpty").style.display = "none";
  document.getElementById("outputLoading").style.display = "flex";
  document.getElementById("outputLoading").style.flexDirection = "column";
  document.getElementById("outputError").style.display = "none";
  document.getElementById("outputResult").style.display = "none";

  const wrap = document.querySelector(".planner-output-wrap");
  wrap.style.alignItems = "center";
  wrap.style.justifyContent = "center";
}

function showError(message) {
  resetBtn();
  document.getElementById("outputLoading").style.display = "none";
  document.getElementById("outputError").style.display = "flex";
  document.getElementById("outputError").style.flexDirection = "column";
  document.getElementById("outputError").style.alignItems = "center";
  document.getElementById("errorMessage").textContent = message;

  const wrap = document.querySelector(".planner-output-wrap");
  wrap.style.alignItems = "center";
  wrap.style.justifyContent = "center";
}

function showResult(result, data) {
  resetBtn();
  document.getElementById("outputLoading").style.display = "none";
  document.getElementById("outputResult").style.display = "flex";
  document.getElementById("outputResult").style.flexDirection = "column";

  const wrap = document.querySelector(".planner-output-wrap");
  wrap.style.alignItems = "stretch";
  wrap.style.justifyContent = "flex-start";

  // Trip info header
  const fromCity = data.from || data.origin || "Origin";
  const toCity = data.destination || "Destination";
  const daysNum = data.days || data.num_days || 1;
  const travNum = data.travelers || data.num_travelers || 1;

  document.getElementById("resultTripInfo").textContent =
    `✈️ ${fromCity} → ${toCity} | ${daysNum} days | ₹${Number(data.budget).toLocaleString("en-IN")} | ${travNum} traveler(s)`;

  // Render itinerary markdown
  document.getElementById("itineraryContent").innerHTML = renderMarkdown(result.itinerary || "");

  // Reset other tabs
  document.getElementById("packingContent").innerHTML =
    '<p class="placeholder-text">Click "Generate Packing List" to get a personalized checklist powered by Gemma 4.</p>';
  document.getElementById("budgetContent").innerHTML =
    '<p class="placeholder-text">Click "Optimize My Budget" to get Gemma 4\'s smart budget recommendations.</p>';

  // Auto-scroll to result
  setTimeout(() => {
    document.getElementById("planner").scrollIntoView({ behavior: "smooth", block: "start" });
  }, 200);

  // Add chat context suggestion
  setTimeout(() => {
    document.getElementById("chatSection").scrollIntoView({ behavior: "smooth" });
  }, 1500);
}

async function retryGeneration() {
  if (state.latestTripRequest) {
    await executeGenerateTrip(state.latestTripRequest);
  } else if (state.formData) {
    await executeGenerateTrip(state.formData);
  }
}

function resetBtn() {
  const btn = document.getElementById("generateBtn");
  btn.disabled = false;
  btn.querySelector(".btn-text").style.display = "inline";
  btn.querySelector(".btn-loading").style.display = "none";
}

let loadingStepInterval = null;
function startLoadingStepAnimation() {
  const steps = ["ls1", "ls2", "ls3", "ls4"];
  let idx = 0;
  steps.forEach((id) => document.getElementById(id).classList.remove("active"));
  document.getElementById(steps[0]).classList.add("active");

  if (loadingStepInterval) clearInterval(loadingStepInterval);
  loadingStepInterval = setInterval(() => {
    document.getElementById(steps[idx]).classList.remove("active");
    idx = (idx + 1) % steps.length;
    document.getElementById(steps[idx]).classList.add("active");
  }, 2500);
}

// ══════════════════════════════════════════════════
//  TABS
// ══════════════════════════════════════════════════

function switchTab(name) {
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
  event.target.classList.add("active");
  document.getElementById(`tab-${name}`).classList.add("active");
}

// ══════════════════════════════════════════════════
//  PACKING LIST
// ══════════════════════════════════════════════════

async function generatePackingList() {
  if (!state.formData) {
    alert("Please generate a trip plan first!");
    return;
  }
  const btn = document.querySelector(".packing-actions .btn-sm");
  btn.disabled = true;
  btn.textContent = "⏳ Generating...";

  document.getElementById("packingContent").innerHTML =
    '<p class="placeholder-text">Gemma 4 is creating your packing list... 🎒</p>';

  try {
    const result = await api.getPackingList({
      destination: state.formData.destination,
      num_days: state.formData.num_days,
      interests: state.formData.interests,
      season: null,
      language: state.language,
    });
    if (result.success) {
      document.getElementById("packingContent").innerHTML = renderMarkdown(result.packing_list);
    } else {
      document.getElementById("packingContent").innerHTML =
        '<p style="color:var(--error)">Failed to generate packing list. Please try again.</p>';
    }
  } catch (err) {
    document.getElementById("packingContent").innerHTML =
      `<p style="color:var(--error)">${err.message}</p>`;
  } finally {
    btn.disabled = false;
    btn.textContent = "🎒 Regenerate Packing List";
  }
}

// ══════════════════════════════════════════════════
//  BUDGET OPTIMIZER
// ══════════════════════════════════════════════════

async function optimizeBudget() {
  if (!state.formData || !state.currentTrip) {
    alert("Please generate a trip plan first!");
    return;
  }
  const btn = document.querySelector(".budget-actions .btn-sm");
  btn.disabled = true;
  btn.textContent = "⏳ Analyzing...";

  document.getElementById("budgetContent").innerHTML =
    '<p class="placeholder-text">Gemma 4 is optimizing your budget... 💰</p>';

  try {
    const result = await api.optimizeBudget({
      destination: state.formData.destination,
      num_days: state.formData.num_days,
      budget: state.formData.budget,
      num_travelers: state.formData.num_travelers,
      current_plan: state.currentTrip.substring(0, 2000),
      language: state.language,
    });
    if (result.success) {
      document.getElementById("budgetContent").innerHTML = renderMarkdown(result.optimization);
    } else {
      document.getElementById("budgetContent").innerHTML =
        '<p style="color:var(--error)">Budget optimization failed. Please try again.</p>';
    }
  } catch (err) {
    document.getElementById("budgetContent").innerHTML =
      `<p style="color:var(--error)">${err.message}</p>`;
  } finally {
    btn.disabled = false;
    btn.textContent = "💡 Re-analyze Budget";
  }
}

// ══════════════════════════════════════════════════
//  REPLAN MODAL
// ══════════════════════════════════════════════════

function openReplanModal() {
  if (!state.currentTrip) {
    alert("Please generate a trip plan first!");
    return;
  }
  document.getElementById("replanModal").style.display = "flex";
}

function closeReplanModal() {
  document.getElementById("replanModal").style.display = "none";
  document.getElementById("replanRequest").value = "";
  document.getElementById("replanBudget").value = "";
}

function closeModal(event) {
  if (event.target === document.getElementById("replanModal")) {
    closeReplanModal();
  }
}

async function submitReplan() {
  const changeRequest = document.getElementById("replanRequest").value.trim();
  if (!changeRequest) {
    alert("Please describe what you'd like to change.");
    return;
  }

  const btn = document.getElementById("replanBtnText");
  btn.textContent = "⏳ Re-planning...";

  const newBudget = document.getElementById("replanBudget").value
    ? parseFloat(document.getElementById("replanBudget").value)
    : null;

  try {
    const result = await api.replanTrip({
      original_plan: state.currentTrip,
      change_request: changeRequest,
      destination: state.formData?.destination || "the destination",
      num_days: state.formData?.num_days || 3,
      new_budget: newBudget,
      language: state.language,
    });

    if (result.success) {
      state.currentTrip = result.itinerary;
      state.interactionId = result.interaction_id;

      document.getElementById("itineraryContent").innerHTML = renderMarkdown(result.itinerary);
      
      // Switch to itinerary tab
      document.querySelectorAll(".tab-btn")[0].click();
      
      closeReplanModal();
      alert("✅ Your trip has been re-planned by Gemma 4!");
    } else {
      alert("Re-planning failed: " + (result.error || "Unknown error"));
    }
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    btn.textContent = "🔄 Re-plan with Gemma 4";
  }
}

// ══════════════════════════════════════════════════
//  CHAT ASSISTANT
// ══════════════════════════════════════════════════

function handleChatKeydown(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendChat();
  }
}

function sendSuggestion(btn) {
  document.getElementById("chatInput").value = btn.textContent;
  sendChat();
}

async function sendChat() {
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;

  input.value = "";
  input.style.height = "auto";

  // Append user message
  appendChatMessage("user", message);

  // Show loading
  const loadingEl = appendChatMessage("assistant", "...", true);

  const sendBtn = document.getElementById("chatSendBtn");
  sendBtn.disabled = true;

  try {
    const result = await api.chat({
      message,
      trip_context: state.currentTrip ? state.currentTrip.substring(0, 2000) : null,
      conversation_id: state.chatConversationId,
      language: state.language,
    });

    // Remove loading message
    loadingEl.remove();

    if (result.success) {
      state.chatConversationId = result.interaction_id;
      appendChatMessage("assistant", result.reply);
    } else {
      appendChatMessage("assistant", "❌ " + (result.error || "Something went wrong. Please try again."));
    }
  } catch (err) {
    loadingEl.remove();
    appendChatMessage("assistant", "❌ " + (err.message || "Could not reach the server."));
  } finally {
    sendBtn.disabled = false;
  }
}

function appendChatMessage(role, content, isLoading = false) {
  const container = document.getElementById("chatMessages");

  const msgEl = document.createElement("div");
  msgEl.className = `chat-message ${role}${isLoading ? " loading" : ""}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = role === "user" ? "👤" : "🤖";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  if (isLoading) {
    bubble.innerHTML = `
      <div class="loading-dots" style="display:flex;gap:6px;">
        <div class="dot"></div><div class="dot"></div><div class="dot"></div>
      </div>`;
  } else {
    // Render markdown for assistant messages
    if (role === "assistant") {
      bubble.innerHTML = renderMarkdown(content);
    } else {
      const p = document.createElement("p");
      p.textContent = content;
      bubble.appendChild(p);
    }
  }

  msgEl.appendChild(avatar);
  msgEl.appendChild(bubble);
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;

  return msgEl;
}

// ══════════════════════════════════════════════════
//  SHARE / COPY / DOWNLOAD
// ══════════════════════════════════════════════════

function copyPlan() {
  if (!state.currentTrip) return;
  navigator.clipboard.writeText(state.currentTrip).then(() => {
    showToast("✅ Trip plan copied to clipboard!");
  });
}

function downloadPlan() {
  if (!state.currentTrip) return;
  const dest = state.formData?.destination || "trip";
  const blob = new Blob([state.currentTrip], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `yatra-ai-${dest.toLowerCase().replace(/\s+/g, "-")}-plan.txt`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("⬇️ Trip plan downloaded!");
}

async function sharePlan() {
  if (!state.currentTrip) return;
  const shareData = {
    title: "My Yatra AI Trip Plan",
    text: `Check out my AI-generated trip plan for ${state.formData?.destination}!\n\n${state.currentTrip.substring(0, 300)}...`,
    url: window.location.href,
  };
  if (navigator.share) {
    await navigator.share(shareData);
  } else {
    copyPlan();
    showToast("🔗 Link copied! Share it with your friends.");
  }
}

// ══════════════════════════════════════════════════
//  TOAST NOTIFICATION
// ══════════════════════════════════════════════════

function showToast(message) {
  const toast = document.createElement("div");
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    background: var(--surface2); border: 1px solid var(--border);
    color: var(--text); padding: 12px 24px; border-radius: var(--r-full);
    font-size: 14px; font-weight: 600; z-index: 9999;
    box-shadow: var(--shadow-md); animation: slide-up 0.3s ease;
  `;
  const style = document.createElement("style");
  style.textContent = `
    @keyframes slide-up {
      from { transform: translateX(-50%) translateY(20px); opacity: 0; }
      to { transform: translateX(-50%) translateY(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}
