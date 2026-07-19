const host = "http://127.0.0.1:8000";
let confirmCallback = null;
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.textContent = message;
  toast.className = "toast " + type;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(1rem)";
    toast.style.transition = "all 0.2s";
    setTimeout(() => toast.remove(), 200);
  }, 3000);
}

function setActiveSidebar() {
  const current = window.location.pathname;

  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.remove("active");

    if (item.getAttribute("href") === current) {
      item.classList.add("active");
    }
  });
}
async function loadSidebar() {
  const res = await fetch("frontend/components/sidebar.html");

  const html = await res.text();

  document.getElementById("sidebar").innerHTML = html;

  setActiveSidebar();

  lucide.createIcons();
}

async function checkAuth() {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/me", {
      credentials: "include",
    });

    if (!response.ok) {
      window.location.href = "/login";

      return null;
    }

    return await response.json();
  } catch (e) {
    window.location.href = "/login";

    return null;
  }
}
async function logout() {
  try {
    await fetch(`${host}/api/logout`, {
      method: "GET",
      credentials: "include",
    });

    window.location.href = "/login";
  } catch (err) {
    console.error(err);
    alert("Logout failed");
  }
}

function setupLogout() {
  const logoutBtn = document.getElementById("logout-btn");

  if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
  }
}
function setupHeaderProfile(user) {
  if (!user) return;
  const badge = document.getElementById("user-badge");
  if (badge) {
    badge.textContent = user.name.substring(0, 2).toUpperCase();
  }
}

async function loading() {
  await loadSidebar();
  await loadConfirmModal();
  const user = await checkAuth();
  if (!user) return;
  setupHeaderProfile(user);
  setActiveSidebar();
  setupLogout();

  lucide.createIcons();
  return user;
}

async function loadConfirmModal() {
  const res = await fetch("frontend/components/confirm-modal.html");

  const html = await res.text();

  document.body.insertAdjacentHTML("beforeend", html);

  document
    .getElementById("confirm-close-btn")
    .addEventListener("click", closeConfirmModal);

  document
    .getElementById("confirm-cancel-btn")
    .addEventListener("click", closeConfirmModal);

  document
    .getElementById("confirm-action-btn")
    .addEventListener("click", async () => {
      if (confirmCallback) {
        await confirmCallback();
      }

      closeConfirmModal();
    });

  lucide.createIcons();
}

function showConfirmModal({
  title,

  message,

  confirmText = "Confirm",

  confirmClass = "bg-emerald-600 hover:bg-emerald-700",

  onConfirm,
}) {
  document.getElementById("confirm-title").textContent = title;

  document.getElementById("confirm-message").textContent = message;

  const btn = document.getElementById("confirm-action-btn");

  btn.textContent = confirmText;

  btn.className = `px-5 py-2 rounded-lg text-white font-semibold ${confirmClass}`;

  confirmCallback = onConfirm;

  document.getElementById("confirm-modal").classList.remove("hidden");
}
function closeConfirmModal() {
  document.getElementById("confirm-modal").classList.add("hidden");
}
