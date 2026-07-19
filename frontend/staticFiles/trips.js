let tripsCache = [];
let driversMap = {}; // Maps driver_id -> driver details
let vehiclesMap = {}; // Maps vehicle_id -> vehicle details

async function loadDropdowns() {
  try {
    //-------------------------
    // Drivers
    //-------------------------

    const driverResponse = await fetch(`${host}/api/drivers/available`, {
      credentials: "include",
    });

    if (!driverResponse.ok) {
      throw new Error("Unable to load drivers.");
    }

    const drivers = await driverResponse.json();

    const driverSelect = document.getElementById("f-driver");

    driverSelect.innerHTML = `<option value="">Select Driver</option>`;

    drivers.forEach((driver) => {
      driversMap[driver.driver_id] = driver;
      driverSelect.innerHTML += `
                <option value="${driver.driver_id}">
                ${driver.name} (${driver.contact_number})
            </option>
            `;
    });

    //-------------------------
    // Vehicles
    //-------------------------

    const vehicleResponse = await fetch(`${host}/api/vehicles/available`, {
      credentials: "include",
    });

    if (!vehicleResponse.ok) {
      throw new Error("Unable to load vehicles.");
    }

    const vehicles = await vehicleResponse.json();

    const vehicleSelect = document.getElementById("f-vehicle");

    vehicleSelect.innerHTML = `<option value="">Select Vehicle</option>`;

    vehicles.forEach((vehicle) => {
      vehiclesMap[vehicle.vehicle_id] = vehicle;

      vehicleSelect.innerHTML += `
                <option value="${vehicle.vehicle_id}">
                    ${vehicle.registration_number}
                    (${vehicle.name_model})
                    (${vehicle.max_load_capacity_kg} kg)
                </option>
            `;
    });
  } catch (err) {
    console.error(err);

    showToast(err.message, "error");
  }
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

// load Data
async function loadData() {
  try {
    const response = await fetch(`${host}/api/trips`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Unable to load trips.");
    }

    tripsCache = await response.json();

    renderTable(tripsCache);

    renderStats(tripsCache);
  } catch (err) {
    console.error(err);

    showToast(err.message, "error");
  }
}

function renderStats(data) {
  document.getElementById("stat-total").textContent = data.length;
  document.getElementById("stat-dispatched").textContent = data.filter(
    (i) => i.status === "Dispatched",
  ).length;
  document.getElementById("stat-completed").textContent = data.filter(
    (i) => i.status === "Completed",
  ).length;

  const activeCargo = data
    .filter((i) => i.status === "Dispatched")
    .reduce((acc, curr) => acc + curr.cargo_weight_kg, 0);
  document.getElementById("stat-cargo").textContent =
    `${(activeCargo / 1000).toFixed(1)} T`;
}

function renderTable(data) {
  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";

  if (data.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="6" class="p-8 text-center text-slate-400">
                    No active trips found.
                </td>
            </tr>
        `;
    return;
  }

  data.forEach((trip) => {
    let badgeClass = "bg-slate-100 text-slate-600 border-slate-300";
    let badgeDot = "bg-slate-400";

    switch (trip.status) {
      case "Dispatched":
        badgeClass = "bg-sky-50 text-sky-700 border-sky-200";
        badgeDot = "bg-sky-500 animate-pulse";
        break;

      case "Completed":
        badgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
        badgeDot = "bg-emerald-500";
        break;

      case "Cancelled":
        badgeClass = "bg-rose-50 text-rose-700 border-rose-200";
        badgeDot = "bg-rose-500";
        break;
    }

    const driver = driversMap[trip.driver_id];
    const vehicle = vehiclesMap[trip.vehicle_id];

    const driverName = driver ? driver.name : `Driver #${trip.driver_id}`;

    const driverLicense = driver ? driver.license_number : "N/A";

    const vehicleReg = vehicle
      ? vehicle.registration_number
      : `Vehicle #${trip.vehicle_id}`;

    const vehicleModel = vehicle ? vehicle.name_model : "";

    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-50 transition-colors group";
    let actions = "";

    if (trip.status === "Draft") {
      actions = `

        <div class="flex items-center justify-center gap-2">

            <button
                class="edit-btn p-2 rounded-lg hover:bg-sky-50 text-slate-500 hover:text-sky-600"
                data-id="${trip.trip_id}">

                <i data-lucide="pencil" class="w-4 h-4"></i>

            </button>

            <button
                class="delete-btn p-2 rounded-lg hover:bg-rose-50 text-slate-500 hover:text-rose-600"
                data-id="${trip.trip_id}">

                <i data-lucide="trash-2" class="w-4 h-4"></i>

            </button>

            <button
                class="dispatch-btn px-3 py-1 rounded-full
                bg-emerald-500 text-white text-xs font-semibold
                hover:bg-emerald-600"
                data-id="${trip.trip_id}">

                Dispatch

            </button>

        </div>

    `;
    } else if (trip.status === "Dispatched") {
      actions = `

        <button
            class="complete-btn
            px-3 py-1
            rounded-full
            bg-sky-600
            text-white
            text-xs
            font-semibold"
            data-id="${trip.trip_id}">

            Complete

        </button>

    `;
    } else {
      actions = `

        <span class="text-slate-400 text-xs">

            Completed

        </span>

    `;
    }
    tr.innerHTML = `

            <td class="px-6 py-4 font-mono font-semibold text-xs text-slate-900">
                ${escapeHTML(trip.trip_id)}
            </td>

            <td class="px-6 py-4">
                <div class="flex flex-col gap-1">

                    <div class="flex items-center gap-2 text-slate-800 text-sm font-medium">
                        <i data-lucide="map-pin" class="w-4 h-4 text-green-600"></i>
                        ${escapeHTML(trip.source)}
                    </div>

                    <div class="flex items-center gap-2 text-slate-500 text-sm">
                        <i data-lucide="move-right" class="w-4 h-4"></i>
                        ${escapeHTML(trip.destination)}
                    </div>

                </div>
            </td>

            <td class="px-6 py-4">
                <div class="space-y-3">

                    <div class="flex items-start gap-2">
                        <i data-lucide="truck" class="w-4 h-4 mt-0.5 text-sky-600"></i>

                        <div>
                            <div class="text-sm font-semibold text-slate-800">
                                ${escapeHTML(vehicleReg)}
                            </div>

                            <div class="text-xs text-slate-500">
                                ${escapeHTML(vehicleModel)}
                            </div>
                        </div>
                    </div>

                    <div class="flex items-start gap-2">
                        <i data-lucide="user" class="w-4 h-4 mt-0.5 text-emerald-600"></i>

                        <div>
                            <div class="text-sm font-semibold text-slate-800">
                                ${escapeHTML(driverName)}
                            </div>

                            <div class="text-xs text-slate-500">
                                ${escapeHTML(driverLicense)}
                            </div>
                        </div>
                    </div>

                </div>
            </td>

            <td class="px-6 py-4">

                <div class="text-sm font-semibold text-slate-800">
                    ${Number(trip.cargo_weight_kg).toLocaleString()} kg
                </div>

                <div class="text-xs text-slate-500 mt-1">
                    ${Number(trip.planned_distance_km).toLocaleString()} km
                </div>

            </td>

            <td class="px-6 py-4">

                <span class="inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-semibold ${badgeClass}">

                    <span class="w-2 h-2 rounded-full ${badgeDot}"></span>

                    ${escapeHTML(trip.status)}

                </span>

            </td>
            <td class="px-6 py-4 text-center">

               ${actions}

            </td>

            
        `;

    tbody.appendChild(tr);
  });

  tbody.querySelectorAll(".edit-btn").forEach((btn) => {
    btn.addEventListener("click", () => openModal(btn.dataset.id));
  });

  tbody.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", () => confirmDelete(btn.dataset.id));
  });
  tbody.querySelectorAll(".dispatch-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      confirmDispatch(btn.dataset.id);
    });
  });
  tbody.querySelectorAll(".complete-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      confirmComplete(btn.dataset.id);
    });
  });
  lucide.createIcons();
}

const modal = document.getElementById("modal");
const form = document.getElementById("data-form");

function openModal(id = null) {
  form.reset();
  modal.classList.remove("hidden");
  const idInput = document.getElementById("f-trip-id");

  if (id) {
    const t = tripsCache.find((i) => i.trip_id === id);
    document.getElementById("modal-title").textContent = "Edit Trip Dispatch";
    document.getElementById("form-is-edit").value = "true";

    idInput.value = t.trip_id;
    idInput.readOnly = true; // Cannot edit PK

    document.getElementById("f-source").value = t.source;
    document.getElementById("f-dest").value = t.destination;
    document.getElementById("f-vehicle").value = t.vehicle_id;
    document.getElementById("f-driver").value = t.driver_id;
    document.getElementById("f-cargo").value = t.cargo_weight_kg;
    document.getElementById("f-dist").value = t.planned_distance_km;
    document.getElementById("f-status").value = t.status;
  } else {
    document.getElementById("modal-title").textContent = "Dispatch New Trip";
    document.getElementById("form-is-edit").value = "false";

    // Generate aesthetic random Trip ID TRP-XXXX
    idInput.value =
      "TRP-" +
      Date.now().toString().slice(-6) +
      "-" +
      Math.floor(Math.random() * 1000);
    idInput.readOnly = false;
  }
}

function closeModal() {
  modal.classList.add("hidden");
}
document
  .getElementById("add-trip-btn")
  .addEventListener("click", () => openModal());
document
  .getElementById("close-modal-btn")
  .addEventListener("click", closeModal);
document
  .getElementById("cancel-modal-btn")
  .addEventListener("click", closeModal);

function confirmDelete(id) {
  showConfirmModal({
    title: "Delete Trip",

    message: "Are You sure To Delete This trip? This can`t Be back.",

    confirmText: "Delete",

    confirmClass: "bg-red-600 hover:bg-red-700",

    onConfirm: async () => {
      await deleteData(id);
    },
  });
}
async function deleteData(id) {
  try {
    const res = await fetch(`${host}/api/trips/${id}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (!res.ok) throw new Error("Delete failed");

    showToast("Trip cancelled/deleted", "success");
    await loadData();
    await loadDropdowns();
  } catch (err) {
    console.error(err);
    showToast(err.message, "error");
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const isEdit = document.getElementById("form-is-edit").value === "true";
  const trip_id = document.getElementById("f-trip-id").value.trim();

  const payload = {
    trip_id,
    source: document.getElementById("f-source").value.trim(),
    destination: document.getElementById("f-dest").value.trim(),
    vehicle_id: parseInt(document.getElementById("f-vehicle").value),
    driver_id: parseInt(document.getElementById("f-driver").value),
    cargo_weight_kg: parseFloat(document.getElementById("f-cargo").value),
    planned_distance_km: parseFloat(document.getElementById("f-dist").value),
  };

  try {
    const url = isEdit ? `${host}/api/trips/${trip_id}` : `${host}/api/trips`;
    const res = await fetch(url, {
      method: isEdit ? "PUT" : "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      // 1. Try to parse the server's JSON error message
      const errorData = await res.json().catch(() => ({}));

      // 2. Use the server message, fallback to status text, or a default string
      const errorMessage =
        errorData.detail || res.statusText || "API Sync Failed";

      throw new Error(errorMessage);
      // const errorData = await res.json().catch(() => ({}));

      // let errorMessage = "API Sync Failed";

      // if (Array.isArray(errorData.detail)) {
      //   errorMessage = errorData.detail
      //     .map((err) => `${err.loc.join(" -> ")} : ${err.msg}`)
      //     .join("\n");
      // } else if (typeof errorData.detail === "string") {
      //   errorMessage = errorData.detail;
      // }

      // throw new Error(errorMessage);
    }
    await loadData();

    closeModal();

    showToast(
      isEdit ? "Trip updated successfully" : "Trip created successfully",
      "success",
    );
  } catch (err) {
    console.error(err);
    showToast(err.message, "error");
  }
});

function confirmDispatch(id) {
  showConfirmModal({
    title: "Dispatch Trip",

    message: `Dispatch Trip ${id}?`,

    confirmText: "Dispatch",

    confirmClass: "bg-emerald-600 hover:bg-emerald-700",

    onConfirm: async () => {
      await dispatchTrip(id);
    },
  });
}
async function dispatchTrip(id) {
  try {
    const response = await fetch(
      `${host}/api/trips/${id}/dispatch`,

      {
        method: "PATCH",

        credentials: "include",
      },
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Dispatch Failed");
    }

    showToast("Trip Dispatched Successfully", "success");

    await loadDropdowns();

    await loadData();
  } catch (err) {
    console.error(err);

    showToast(err.message, "error");
  }
}
function confirmComplete(id) {
  showConfirmModal({
    title: "Complete Trip",

    message: `Complete Trip ${id}?`,

    confirmText: "Complete",

    confirmClass: "bg-sky-600 hover:bg-sky-700",

    onConfirm: async () => {
      await completeTrip(id);
    },
  });
}
async function completeTrip(id) {
  try {
    const response = await fetch(
      `${host}/api/trips/${id}/complete`,

      {
        method: "PATCH",
        credentials: "include",
      },
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Completion Failed");
    }

    showToast("Trip Completed Successfully", "success");

    await loadDropdowns();

    await loadData();
  } catch (err) {
    console.error(err);

    showToast(err.message, "error");
  }
}
