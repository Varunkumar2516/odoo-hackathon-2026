let cache = [];

let vehiclesMap = {};

const modal = document.getElementById("modal");

const form = document.getElementById("data-form");

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

function renderStats(data) {
  document.getElementById("stat-total").textContent = data.length;

  document.getElementById("stat-active").textContent = data.filter(
    (item) => item.status === "Active",
  ).length;

  document.getElementById("stat-closed").textContent = data.filter(
    (item) => item.status === "Closed",
  ).length;

  const totalCost = data.reduce((sum, item) => sum + Number(item.cost), 0);

  document.getElementById("stat-cost").textContent =
    `$${totalCost.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
}
function renderTable(data) {
  const tbody = document.getElementById("table-body");

  tbody.innerHTML = "";

  if (data.length === 0) {
    tbody.innerHTML = `
        <tr>
            <td colspan="7"
                class="p-8 text-center text-slate-400">

                No Maintenance Logs Found

            </td>
        </tr>
        `;

    return;
  }

  data.forEach((log) => {
    let badgeClass = "";
    let actions = "";

    if (log.status === "Active") {
      badgeClass = "bg-amber-50 text-amber-700 border-amber-200";

      actions = `
                <button
                    class="edit-btn p-2 hover:bg-slate-100 rounded-lg"
                    data-id="${log.maintenance_id}">
                    <i data-lucide="pencil" class="w-4 h-4"></i>
                </button>

                <button
                    class="complete-btn p-2 hover:bg-emerald-100 rounded-lg text-emerald-600"
                    data-id="${log.maintenance_id}">
                    <i data-lucide="check-circle" class="w-4 h-4"></i>
                </button>

                <button
                    class="delete-btn p-2 hover:bg-red-100 rounded-lg text-red-600"
                    data-id="${log.maintenance_id}">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
            `;
    } else {
      badgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";

      actions = `
                <span class="text-xs font-semibold text-emerald-600">

                    Completed

                </span>
            `;
    }

    const row = document.createElement("tr");

    row.className = "hover:bg-slate-50 transition";

    row.innerHTML = `

            <td class="px-6 py-4 font-mono font-semibold">

                MNT-${String(log.maintenance_id).padStart(4, "0")}

            </td>

            <td class="px-6 py-4">

                <div class="font-semibold">

                    ${escapeHTML(log.vehicle)}

                </div>

            </td>

            <td class="px-6 py-4">

                ${escapeHTML(log.service_type)}

            </td>

            <td class="px-6 py-4">

                ${new Date(log.service_date).toLocaleDateString("en-GB")}

            </td>

            <td class="px-6 py-4 font-semibold text-rose-600">

                $${Number(log.cost).toFixed(2)}

            </td>

            <td class="px-6 py-4">

                <span class="px-2 py-1 rounded-full border text-xs font-semibold ${badgeClass}">

                    ${log.status}

                </span>

            </td>

            <td class="px-6 py-4 text-center">

                <div class="flex justify-center gap-2">

                    ${actions}

                </div>

            </td>

        `;

    tbody.appendChild(row);
  });

  lucide.createIcons();

  tbody.querySelectorAll(".edit-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      openModal(btn.dataset.id);
    });
  });

  tbody.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      deleteMaintenance(btn.dataset.id);
    });
  });

  tbody.querySelectorAll(".complete-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      confirmCompleteMaintenance(btn.dataset.id);
    });
  });
}

async function loadVehicles() {
  try {
    const response = await fetch(
      `${host}/api/vehicles`,

      {
        credentials: "include",
      },
    );

    if (!response.ok) {
      throw new Error("Unable to load vehicles.");
    }

    const vehicles = await response.json();

    const select = document.getElementById("f-vehicle");

    select.innerHTML = `<option value="">Select Vehicle</option>`;

    vehiclesMap = {};

    vehicles.forEach((vehicle) => {
      if (vehicle.status !== "Available") return;

      vehiclesMap[vehicle.vehicle_id] = vehicle;

      select.innerHTML += `
                <option value="${vehicle.vehicle_id}">

                    ${vehicle.registration_number}
                    •
                    ${vehicle.name_model}
                    •
                    ${vehicle.type}

                </option>
            `;
    });
  } catch (err) {
    console.error(err);

    showToast(err.message, "error");
  }
}

async function loadMaintenance() {
  try {
    const response = await fetch(`${host}/api/maintenance`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Unable to load maintenance logs.");
    }

    cache = await response.json();
    console.log(cache);
    renderTable(cache);

    renderStats(cache);
  } catch (err) {
    console.error(err);

    showToast(err.message, "error");
  }
}

document.getElementById("search-input").addEventListener("input", handleFilter);

document
  .getElementById("status-filter")
  .addEventListener("change", handleFilter);

function handleFilter() {
  const search = document
    .getElementById("search-input")
    .value.toLowerCase()
    .trim();

  const status = document.getElementById("status-filter").value;

  const filtered = cache.filter((log) => {
    const matchSearch =
      log.service_type.toLowerCase().includes(search) ||
      log.vehicle.toLowerCase().includes(search) ||
      String(log.maintenance_id).includes(search);

    const matchStatus = status === "ALL" || log.status === status;

    return matchSearch && matchStatus;
  });

  renderTable(filtered);
}

function openModal(id = null) {
  form.reset();

  modal.classList.remove("hidden");

  const vehicleSelect = document.getElementById("f-vehicle");

  if (id) {
    // FIRST create log
    const log = cache.find((x) => x.maintenance_id == id);

    console.log("Edit ID:", id);
    console.log("Log:", log);

    if (!log) {
      showToast("Maintenance record not found.", "error");
      return;
    }

    document.getElementById("modal-title").textContent = "Edit Maintenance";

    document.getElementById("form-id").value = id;

    vehicleSelect.innerHTML = `
    <option value="${log.vehicle_id}">
        ${log.vehicle}
    </option>
    `;

    vehicleSelect.value = log.vehicle_id;
    vehicleSelect.disabled = true;

    document.getElementById("f-type").value = log.service_type;
    document.getElementById("f-date").value = log.service_date;
    document.getElementById("f-cost").value = log.cost;
  } else {
    document.getElementById("modal-title").textContent = "Log Maintenance";

    document.getElementById("form-id").value = "";

    vehicleSelect.disabled = false;
    vehicleSelect.selectedIndex = 0;

    document.getElementById("f-date").value = new Date()
      .toISOString()
      .split("T")[0];
  }
}
function closeModal() {
  modal.classList.add("hidden");

  form.reset();

  document.getElementById("form-id").value = "";

  const vehicleSelect = document.getElementById("f-vehicle");

  vehicleSelect.disabled = false;
}

document.getElementById("add-btn").addEventListener("click", () => openModal());

document
  .getElementById("close-modal-btn")
  .addEventListener("click", closeModal);

document
  .getElementById("cancel-modal-btn")
  .addEventListener("click", closeModal);

async function deleteMaintenance(id) {
  showConfirmModal({
    title: "Delete Maintenance",

    message: "Delete this maintenance log?",

    confirmText: "Delete",

    confirmClass: "bg-red-600 hover:bg-red-700",

    onConfirm: async () => {
      try {
        const response = await fetch(
          `${host}/api/maintenance/${id}`,

          {
            method: "DELETE",

            credentials: "include",
          },
        );

        if (!response.ok) {
          const err = await response.json();

          throw new Error(err.detail);
        }

        await loadMaintenance();

        showToast(
          "Maintenance deleted successfully.",

          "success",
        );
      } catch (err) {
        showToast(err.message, "error");
      }
    },
  });
}

function confirmCompleteMaintenance(id) {
  showConfirmModal({
    title: "Complete Maintenance",

    message: "Mark this maintenance as completed?",

    confirmText: "Complete",

    confirmClass: "bg-emerald-600 hover:bg-emerald-700",

    onConfirm: async () => {
      try {
        const response = await fetch(
          `${host}/api/maintenance/${id}/complete`,

          {
            method: "PATCH",

            credentials: "include",
          },
        );

        if (!response.ok) {
          const err = await response.json();

          throw new Error(err.detail);
        }

        await loadMaintenance();

        await loadVehicles();

        showToast(
          "Maintenance completed.",

          "success",
        );
      } catch (err) {
        showToast(err.message, "error");
      }
    },
  });
}
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const id = document.getElementById("form-id").value;

  const isEdit = id !== "";

  const payload = {
    vehicle_id: parseInt(document.getElementById("f-vehicle").value),

    service_type: document.getElementById("f-type").value.trim(),

    service_date: document.getElementById("f-date").value,

    cost: parseFloat(document.getElementById("f-cost").value),
  };

  try {
    const url = isEdit
      ? `${host}/api/maintenance/${id}`
      : `${host}/api/maintenance`;

    const response = await fetch(
      url,

      {
        method: isEdit ? "PUT" : "POST",

        credentials: "include",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(payload),
      },
    );

    if (!response.ok) {
      const err = await response.json();

      throw new Error(err.detail || "Unable to save maintenance.");
    }

    closeModal();

    await loadMaintenance();

    showToast(
      isEdit
        ? "Maintenance updated successfully."
        : "Maintenance created successfully.",

      "success",
    );
  } catch (err) {
    console.error(err);

    showToast(err.message, "error");
  }
});
