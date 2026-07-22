let cache = [];

let vehiclesMap = {};
let activeTrips = [];

let maintenanceCache = [];
const contextRadios = document.querySelectorAll('input[name="fuel-context"]');

function updateFuelContext() {
  const value = document.querySelector(
    'input[name="fuel-context"]:checked',
  ).value;

  document.getElementById("general-section").classList.add("hidden");

  document.getElementById("trip-section").classList.add("hidden");

  document.getElementById("maintenance-section").classList.add("hidden");

  if (value === "general") {
    document.getElementById("general-section").classList.remove("hidden");
  }

  if (value === "trip") {
    document.getElementById("trip-section").classList.remove("hidden");
  }

  if (value === "maintenance") {
    document.getElementById("maintenance-section").classList.remove("hidden");
  }
}
async function loadDispatchedTrips() {
  const res = await fetch(`${host}/api/trips/dispatched`, {
    credentials: "include",
  });

  activeTrips = await res.json();

  const select = document.getElementById("f-trip");

  select.innerHTML = `<option value="">Select Trip</option>`;

  activeTrips.forEach((trip) => {
    select.innerHTML += `

            <option value="${trip.trip_id}">

                ${trip.trip_id}
                -
                ${trip.source}
                →
                ${trip.destination}

            </option>

        `;
  });
}
document.getElementById("f-trip").addEventListener("change", function () {
  const trip = activeTrips.find((t) => t.trip_id === this.value);

  if (!trip) {
    document.getElementById("trip-vehicle").value = "";

    return;
  }

  document.getElementById("trip-vehicle").value = trip.vehicle;
});

contextRadios.forEach((r) => {
  r.addEventListener("change", updateFuelContext);
});

async function loadMaintenance() {
  const res = await fetch(`${host}/api/maintenance/active`, {
    credentials: "include",
  });

  maintenanceCache = await res.json();
  console.log(res.status);
  const select = document.getElementById("f-maintenance");

  select.innerHTML = `<option>Select Maintenance</option>`;

  maintenanceCache.forEach((item) => {
    select.innerHTML += `

            <option
            value="${item.maintenance_id}">

                MNT-${item.maintenance_id}

                (${item.service_type})

            </option>

        `;
  });
}
document
  .getElementById("f-maintenance")
  .addEventListener("change", function () {
    const item = maintenanceCache.find((m) => m.maintenance_id == this.value);

    if (!item) {
      document.getElementById("maintenance-vehicle").value = "";

      return;
    }

    document.getElementById("maintenance-vehicle").value = item.vehicle;
  });
async function loadVehicles() {
  try {
    const res = await fetch(`${host}/api/vehicles`, {
      credentials: "include",
    });

    if (!res.ok) throw new Error("Failed to load vehicles");

    const vehicles = await res.json();

    vehiclesMap = {};

    const select = document.getElementById("f-vehicle");

    select.innerHTML = `<option value="">Select Vehicle</option>`;

    vehicles.forEach((vehicle) => {
      vehiclesMap[vehicle.vehicle_id] = vehicle;

      select.innerHTML += `
        <option value="${vehicle.vehicle_id}">
            ${vehicle.registration_number}
        </option>
    `;
    });
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function loadFuelLogs() {
  try {
    const res = await fetch(`${host}/api/fuel`, {
      credentials: "include",
    });

    if (!res.ok) throw new Error("Failed to load fuel logs");

    cache = await res.json();

    renderStats();

    renderTable();
  } catch (err) {
    showToast(err.message, "error");
  }
}
function renderStats() {
  document.getElementById("stat-total").textContent = cache.length;

  const totalLiters = cache.reduce((sum, log) => sum + log.liters_filled, 0);
  document.getElementById("stat-volume").textContent = totalLiters.toFixed(1);

  const totalCost = cache.reduce((sum, log) => sum + log.fuel_cost, 0);

  // Dashboard card
  document.getElementById("stat-expense").textContent =
    "₹" + formatCurrency(totalCost);

  const avg = totalLiters ? totalCost / totalLiters : 0;

  document.getElementById("stat-avg").textContent =
    currencyFormatter.format(avg);
}

function escapeHTML(str) {
  if (!str) return "";
  return String(str).replace(
    /[&<>'"]/g,
    (t) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "'": "&#39;",
        '"': "&quot;",
      })[t] || t,
  );
}
function renderTable(data = cache) {
  const tbody = document.getElementById("table-body");

  tbody.innerHTML = "";

  if (data.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-8">
                    No fuel logs found.
                </td>
            </tr>
        `;

    return;
  }

  data.forEach((log) => {
    let context = `
        <span class="px-2 py-1 rounded-full bg-slate-100 text-slate-600 text-xs">
        General
        </span>
        `;

    if (log.trip_id) {
      context = `
            <span class="px-2 py-1 rounded-full bg-sky-100 text-sky-700 text-xs font-semibold">
                Trip
            </span>
            <div class="text-xs text-slate-500 mt-1">
                ${log.vehicle}
                ${log.trip_id}
            </div>
            `;
    } else if (log.maintenance_id) {
      context = `
            <span class="px-2 py-1 rounded-full bg-orange-100 text-orange-700 text-xs font-semibold">
                Maintenance
            </span>
            <div class="text-xs text-slate-500 mt-1">
                MNT-${log.maintenance_id}
            </div>
            `;
    }
    const costPerLiter =
      log.liters_filled > 0 ? log.fuel_cost / log.liters_filled : 0;

    tbody.innerHTML += `

        <tr>

            <td class="px-6 py-4">
                FL-${String(log.fuel_log_id).padStart(4, "0")}
            </td>

            <td class="px-6 py-4">
                ${log.vehicle} 
                ${log.name_model}
            </td>
            <td class="px-6 py-4">
                ${context}
            </td>

            <td class="px-6 py-4">
                ${log.date}
            </td>

            <td class="px-6 py-4 text-right">
                ${log.liters_filled.toFixed(2)}
            </td>

            <td class="px-6 py-4 text-right">
                ${currencyFormatter.format(log.fuel_cost)}
            </td>

            <td class="px-6 py-4 text-right">
                ${currencyFormatter.format(costPerLiter)}
            </td>

            

            <td class="px-6 py-4 text-center">
                <div class="flex justify-center gap-2">

                    <button
                        class="edit-btn p-2 rounded-lg hover:bg-slate-100"
                        data-id="${log.fuel_log_id}">

                        <i data-lucide="pencil"
                        class="w-4 h-4 text-sky-600"></i>

                    </button>

                    <button
                        class="delete-btn p-2 rounded-lg hover:bg-slate-100"
                        data-id="${log.fuel_log_id}">

                        <i data-lucide="trash-2"
                        class="w-4 h-4 text-red-600"></i>

                    </button>

                </div>

            </td>

        </tr>

        `;
  });

  document
    .querySelectorAll(".edit-btn")
    .forEach((btn) => (btn.onclick = () => openModal(btn.dataset.id)));

  document
    .querySelectorAll(".delete-btn")
    .forEach((btn) => (btn.onclick = () => confirmDelete(btn.dataset.id)));

  lucide.createIcons();
}

const modal = document.getElementById("modal");
const form = document.getElementById("data-form");

function openModal(id = null) {
  form.reset();

  document.getElementById("f-effective").textContent = "₹0.00";

  modal.classList.remove("hidden");

  // -----------------------------
  // ADD MODE
  // -----------------------------
  if (!id) {
    document.getElementById("modal-title").textContent = "Record Fuel";

    document.getElementById("form-id").value = "";

    document.querySelector(
      'input[name="fuel-context"][value="general"]',
    ).checked = true;

    updateFuelContext();

    document.getElementById("f-date").value = new Date()
      .toISOString()
      .split("T")[0];

    return;
  }

  // -----------------------------
  // EDIT MODE
  // -----------------------------
  const log = cache.find((item) => item.fuel_log_id == id);

  if (!log) return;

  document.getElementById("modal-title").textContent = "Edit Fuel Log";

  document.getElementById("form-id").value = log.fuel_log_id;

  // -----------------------------
  // Select correct context
  // -----------------------------
  if (log.maintenance_id) {
    document.querySelector(
      'input[name="fuel-context"][value="maintenance"]',
    ).checked = true;

    updateFuelContext();

    document.getElementById("f-maintenance").value = log.maintenance_id;

    const maintenance = maintenanceCache.find(
      (m) => m.maintenance_id == log.maintenance_id,
    );

    document.getElementById("maintenance-vehicle").value = maintenance
      ? maintenance.vehicle
      : "";
  } else if (log.trip_id) {
    document.querySelector('input[name="fuel-context"][value="trip"]').checked =
      true;

    updateFuelContext();

    document.getElementById("f-trip").value = log.trip_id;

    const trip = activeTrips.find((t) => t.trip_id == log.trip_id);

    document.getElementById("trip-vehicle").value = trip ? trip.vehicle : "";
  } else {
    document.querySelector(
      'input[name="fuel-context"][value="general"]',
    ).checked = true;

    updateFuelContext();

    document.getElementById("f-vehicle").value = log.vehicle_id;
  }

  document.getElementById("f-date").value = log.date;

  document.getElementById("f-liters").value = log.liters_filled;

  document.getElementById("f-cost").value = log.fuel_cost;

  updateEffectiveCost();
}

function closeModal() {
  modal.classList.add("hidden");
}
document.getElementById("add-btn").addEventListener("click", () => openModal());
document
  .getElementById("close-modal-btn")
  .addEventListener("click", closeModal);
document
  .getElementById("cancel-modal-btn")
  .addEventListener("click", closeModal);

async function saveFuelLog(e) {
  e.preventDefault();

  const id = document.getElementById("form-id").value;

  const context = document.querySelector(
    'input[name="fuel-context"]:checked',
  ).value;

  let payload = {
    vehicle_id: null,

    trip_id: null,

    date: document.getElementById("f-date").value,

    liters_filled: Number(document.getElementById("f-liters").value),

    fuel_cost: Number(document.getElementById("f-cost").value),
  };
  if (context === "general") {
    payload.vehicle_id = Number(document.getElementById("f-vehicle").value);
  } else if (context === "trip") {
    payload.trip_id = document.getElementById("f-trip").value;
  } else {
    payload.maintenance_id = Number(
      document.getElementById("f-maintenance").value,
    );
  }
  const url = id ? `${host}/api/fuel/${id}` : `${host}/api/fuel`;

  const method = id ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method,

      credentials: "include",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) throw new Error(data.detail);

    showToast(data.message, "success");

    closeModal();

    await loadFuelLogs();
  } catch (err) {
    showToast(err.message, "error");
  }
}

form.addEventListener("submit", saveFuelLog);
function confirmDelete(id) {
  showConfirmModal({
    title: "Delete Fuel logs",

    message: `Delete Logs ${id}?`,

    confirmText: "Delete",

    confirmClass: "bg-emerald-600 hover:bg-emerald-700",

    onConfirm: async () => {
      await deleteFuelLog(id);
    },
  });
}

async function deleteFuelLog(id) {
  try {
    const res = await fetch(
      `${host}/api/fuel/${id}`,

      {
        method: "DELETE",

        credentials: "include",
      },
    );

    const data = await res.json();

    if (!res.ok) throw new Error(data.detail);

    showToast(data.message, "success");

    await loadFuelLogs();
  } catch (err) {
    showToast(err.message, "error");
  }
}

document.getElementById("search-input").addEventListener("input", function () {
  const keyword = this.value.toLowerCase();

  const filtered = cache.filter(
    (log) =>
      log.vehicle.toLowerCase().includes(keyword) || log.date.includes(keyword),
  );

  renderTable(filtered);
});

const liters = document.getElementById("f-liters");

const cost = document.getElementById("f-cost");

function updateEffectiveCost() {
  const l = Number(liters.value);

  const c = Number(cost.value);

  document.getElementById("f-effective").textContent =
    l > 0 ? currencyFormatter.format(c / l) : "₹0.00";
}

liters.oninput = updateEffectiveCost;

cost.oninput = updateEffectiveCost;
