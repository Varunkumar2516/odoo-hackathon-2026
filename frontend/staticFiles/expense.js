let cache = [];
let vehiclesMap = {};
let tripsList = [];

const modal = document.getElementById("modal");
const form = document.getElementById("data-form");

function registerEvents() {
  document
    .getElementById("add-btn")
    .addEventListener("click", () => openModal());

  document
    .getElementById("close-modal-btn")
    .addEventListener("click", closeModal);

  document
    .getElementById("cancel-modal-btn")
    .addEventListener("click", closeModal);

  document
    .getElementById("search-input")
    .addEventListener("input", applyFilters);

  document
    .getElementById("type-filter")
    .addEventListener("change", applyFilters);

  form.addEventListener("submit", saveExpense);
}

async function fetchDropdownMappings() {
  try {
    // Vehicles
    const vehicleRes = await fetch(`${host}/api/vehicles`, {
      credentials: "include",
    });

    if (!vehicleRes.ok) throw new Error("Failed to load vehicles");

    const vehicles = await vehicleRes.json();

    const vehicleSelect = document.getElementById("f-vehicle");

    vehicleSelect.innerHTML = `<option value="">Select Vehicle</option>`;

    vehicles.forEach((vehicle) => {
      vehiclesMap[vehicle.vehicle_id] = vehicle;

      vehicleSelect.innerHTML += `
                <option value="${vehicle.vehicle_id}">
                    ${vehicle.registration_number} - ${vehicle.name_model}
                </option>
            `;
    });

    // Trips

    const tripRes = await fetch(`${host}/api/trips`, {
      credentials: "include",
    });

    if (!tripRes.ok) throw new Error("Failed to load trips");

    tripsList = await tripRes.json();

    const tripSelect = document.getElementById("f-trip");

    tripSelect.innerHTML = `<option value="">General Expense</option>`;

    tripsList.forEach((trip) => {
      tripSelect.innerHTML += `
                <option value="${trip.trip_id}">
                    ${trip.trip_id}
                </option>
            `;
    });
  } catch (err) {
    console.error(err);

    showToast("Unable to load dropdown data", "error");
  }
}

async function loadData() {
  try {
    const res = await fetch(`${host}/api/expenses`, {
      credentials: "include",
    });

    if (!res.ok) throw new Error();

    cache = await res.json();

    renderTable(cache);

    renderStats(cache);
  } catch (err) {
    console.error(err);

    showToast("Unable to load expenses", "error");
  }
}

function renderStats(data) {
  const total = data.reduce((acc, curr) => acc + curr.amount, 0);

  const tolls = data
    .filter((i) => i.expense_type === "Toll")
    .reduce((acc, curr) => acc + curr.amount, 0);

  const maint = data
    .filter((i) => i.expense_type === "Maintenance")
    .reduce((acc, curr) => acc + curr.amount, 0);

  const other = data
    .filter((i) => i.expense_type === "Miscellaneous")
    .reduce((acc, curr) => acc + curr.amount, 0);

  document.getElementById("stat-total").textContent =
    `₹${formatCurrency(total)}`;
  document.getElementById("stat-tolls").textContent =
    `₹${formatCurrency(tolls)}`;
  document.getElementById("stat-maint").textContent =
    `₹${formatCurrency(maint)}`;
  document.getElementById("stat-other").textContent =
    `₹${formatCurrency(other)}`;
}

function renderTable(data) {
  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";

  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">No expense records found.</td></tr>`;
    return;
  }

  data.forEach((exp) => {
    const vehicleReg = vehiclesMap[exp.vehicle_id]
      ? vehiclesMap[exp.vehicle_id].registration_number
      : `Vehicle #${exp.vehicle_id}`;
    const tripDisplay = exp.trip_id
      ? `<span class="font-mono text-sky-600 bg-sky-50 px-2 py-0.5 rounded text-xs border border-sky-100">${escapeHTML(exp.trip_id)}</span>`
      : '<span class="text-slate-400 italic text-xs">General</span>';

    let typeIcon = "receipt";
    let typeColor = "text-amber-600";
    if (exp.expense_type === "Toll") {
      typeIcon = "boom-box";
      typeColor = "text-sky-600";
    }
    if (exp.expense_type === "Maintenance") {
      typeIcon = "wrench";
      typeColor = "text-rose-600";
    }

    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-50/70 transition-colors group";
    tr.innerHTML = `
            <td class="py-4 px-6 font-semibold text-slate-900 font-mono text-xs">
              EXP-${exp.expense_id.toString().padStart(4, "0")}
            </td>
            <td class="px-6 py-4 text-xs font-medium text-slate-600">
               <i data-lucide="calendar" class="w-3 h-3 inline mr-1 text-slate-400"></i>${escapeHTML(exp.date)}
            </td>
            <td class="px-6 py-4">
              <span class="text-xs font-semibold bg-slate-100 border border-slate-200 px-2 py-0.5 rounded flex w-fit items-center gap-1.5 text-slate-700"><i data-lucide="truck" class="w-3 h-3"></i> ${escapeHTML(vehicleReg)}</span>
            </td>
            <td class="px-6 py-4">${tripDisplay}</td>
            <td class="px-6 py-4 text-sm font-medium ${typeColor} flex items-center gap-1.5">
               <i data-lucide="${typeIcon}" class="w-4 h-4"></i> ${escapeHTML(exp.expense_type)}
            </td>
            <td class="px-6 py-4 text-right font-mono font-bold text-slate-800">
              ₹${formatCurrency(exp.amount)}
            </td>
            <td class="px-6 py-4 text-center">
              <div class="flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button class="edit-btn p-1.5 rounded-lg text-slate-500 hover:bg-white hover:text-sky-600 transition-all border border-transparent hover:border-slate-200" data-id="${exp.expense_id}"><i data-lucide="pencil" class="w-4 h-4"></i></button>
                <button class="delete-btn p-1.5 rounded-lg text-slate-500 hover:bg-white hover:text-rose-600 transition-all border border-transparent hover:border-slate-200" data-id="${exp.expense_id}"><i data-lucide="trash-2" class="w-4 h-4"></i></button>
              </div>
            </td>
          `;
    tbody.appendChild(tr);
  });

  tbody
    .querySelectorAll(".edit-btn")
    .forEach((b) => b.addEventListener("click", () => openModal(b.dataset.id)));
  tbody
    .querySelectorAll(".delete-btn")
    .forEach((b) =>
      b.addEventListener("click", () => deleteExpense(b.dataset.id)),
    );
  lucide.createIcons();
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

async function saveExpense(e) {
  e.preventDefault();

  const id = document.getElementById("form-id").value;

  const payload = {
    vehicle_id: parseInt(document.getElementById("f-vehicle").value),

    trip_id: document.getElementById("f-trip").value || null,

    expense_type: document.getElementById("f-type").value,

    amount: parseFloat(document.getElementById("f-amount").value),

    date: document.getElementById("f-date").value,
  };

  try {
    const url = id ? `${host}/api/expenses/${id}` : `${host}/api/expenses`;

    const method = id ? "PUT" : "POST";

    const response = await fetch(url, {
      method,

      credentials: "include",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();

      throw new Error(error.detail);
    }

    showToast(
      id ? "Expense Updated Successfully" : "Expense Added Successfully",
      "success",
    );

    closeModal();

    await loadData();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function deleteExpense(id) {
  if (!confirm("Delete this expense?")) return;

  try {
    const response = await fetch(
      `${host}/api/expenses/${id}`,

      {
        method: "DELETE",

        credentials: "include",
      },
    );

    if (!response.ok) throw new Error();

    showToast("Expense Deleted", "success");

    await loadData();
  } catch {
    showToast("Unable to delete expense", "error");
  }
}

function applyFilters() {
  const q = document.getElementById("search-input").value.toLowerCase().trim();
  const t = document.getElementById("type-filter").value;
  const filtered = cache.filter((item) => {
    const matchQ =
      (vehiclesMap[item.vehicle_id] &&
        vehiclesMap[item.vehicle_id].registration_number
          .toLowerCase()
          .includes(q)) ||
      (item.trip_id && item.trip_id.toLowerCase().includes(q));
    const matchT = t === "ALL" || item.expense_type === t;
    return matchQ && matchT;
  });
  renderTable(filtered);
}

function openModal(id = null) {
  form.reset();
  modal.classList.remove("hidden");

  if (id) {
    const t = cache.find((i) => i.expense_id == id);
    document.getElementById("modal-title").textContent = "Edit Expense";
    document.getElementById("form-id").value = t.expense_id;

    document.getElementById("f-vehicle").value = t.vehicle_id;
    document.getElementById("f-trip").value = t.trip_id || "";
    document.getElementById("f-type").value = t.expense_type;

    let formattedDate = t.date;
    if (formattedDate && formattedDate.includes("T"))
      formattedDate = formattedDate.split("T")[0];
    document.getElementById("f-date").value = formattedDate;

    document.getElementById("f-amount").value = t.amount;
  } else {
    document.getElementById("modal-title").textContent = "Log Expense";
    document.getElementById("form-id").value = "";
    document.getElementById("f-date").value = new Date()
      .toISOString()
      .split("T")[0];
  }
}

function closeModal() {
  modal.classList.add("hidden");
}

function syncVehicleWithTrip() {
  const tripId = document.getElementById("f-trip").value;

  const vehicleSelect = document.getElementById("f-vehicle");

  if (!tripId) {
    vehicleSelect.disabled = false;
    return;
  }

  const trip = tripsList.find((t) => t.trip_id === tripId);

  if (!trip) return;

  vehicleSelect.value = trip.vehicle_id;
  vehicleSelect.disabled = true;
}
document
  .getElementById("f-trip")
  .addEventListener("change", syncVehicleWithTrip);
