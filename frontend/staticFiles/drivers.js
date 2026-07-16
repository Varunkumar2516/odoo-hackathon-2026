
let driversCache = [];

async function loadDrivers() {

    try {

        const response = await fetch(`${host}/api/drivers`, {
            credentials: "include"
        });

        if (!response.ok) {

            const err = await response.json();

            throw new Error(err.detail || "Unable to load drivers.");

        }

        driversCache = await response.json();

        handleSearchAndFilter();

    }

    catch (err) {

        console.error(err);

        showToast(err.message, "error");

    }

};

function renderStats(drivers){

    document.getElementById("total-drivers-stat").textContent =
        drivers.length;

    document.getElementById("total-active-stat").textContent =
        drivers.filter(
            d => d.status === "Available" ||
                 d.status === "On Trip"
        ).length;

    document.getElementById("total-standby-stat").textContent =
        drivers.filter(
            d => d.status === "Off Duty"
        ).length;

    const avgSafety =
        drivers.length === 0
            ? 0
            : Math.round(
                drivers.reduce(
                    (sum,d)=>sum+d.safety_score,
                    0
                ) / drivers.length
            );

    document.getElementById("avg-rating-stat").textContent =
        avgSafety;
};
function renderTable(drivers) {

    const tbody = document.getElementById("drivers-table-body");

    tbody.innerHTML = "";

    if (drivers.length === 0) {

        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="py-10 text-center text-slate-400">
                    No Drivers Found
                </td>
            </tr>
        `;

        return;
    }

    drivers.forEach(driver => {

        let badgeClass = "";

        switch (driver.status) {

            case "Available":
                badgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
                break;

            case "On Trip":
                badgeClass = "bg-sky-50 text-sky-700 border-sky-200";
                break;

            case "Off Duty":
                badgeClass = "bg-amber-50 text-amber-700 border-amber-200";
                break;

            case "Suspended":
                badgeClass = "bg-rose-50 text-rose-700 border-rose-200";
                break;

            default:
                badgeClass = "bg-slate-50 text-slate-700 border-slate-200";
        }

        const expiry = new Date(driver.license_expiry_date)
            .toLocaleDateString("en-GB");

        const row = document.createElement("tr");

        row.className = "hover:bg-slate-50 transition";

        row.innerHTML = `
                    <td class="py-4 px-6">
                        <div class="font-semibold text-slate-900">
                            ${escapeHTML(driver.name)}
                        </div>

                        <div class="text-sm text-slate-500">
                            ${escapeHTML(driver.email)}
                        </div>
                    </td>
                    <td class="px-6">
                        ${escapeHTML(driver.contact_number)}
                    </td>
                    <td class="px-6">
                        <div class="font-medium">
                            ${escapeHTML(driver.license_number)}
                        </div>
                        <div class="text-xs text-slate-400">
                            ${escapeHTML(driver.license_category)}
                        </div>
                    </td>
                    <td class="px-6">
                        ${expiry}
                    </td>
                    <td class="px-6">
                        <span class="font-semibold">
                            ${driver.safety_score}
                        </span>
                    </td>
                    <td class="px-6">
                        <span class="px-2 py-1 rounded-full border text-xs font-semibold ${badgeClass}">
                            ${driver.status}
                        </span>
                    </td>
                    <td class="px-6 text-center">
                        <div class="flex justify-center gap-2">
                            <button
                                class="edit-btn p-2 hover:bg-slate-100 rounded-lg"
                                data-id="${driver.driver_id}">

                                <i data-lucide="pencil" class="w-4 h-4"></i>
                            </button>
                            <button
                                class="delete-btn p-2 hover:bg-red-50 rounded-lg text-red-600"
                                data-id="${driver.driver_id}">

                                <i data-lucide="trash-2" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </td>
                `;

        tbody.appendChild(row);

    });

    lucide.createIcons();

};

const tbody = document.getElementById("drivers-table-body");

tbody.addEventListener("click", (e) => {

    const editBtn = e.target.closest(".edit-btn");

    if (editBtn) {

        handleEditClick(editBtn.dataset.id);

        return;

    }

    const deleteBtn = e.target.closest(".delete-btn");

    if (deleteBtn) {

        handleDeleteClick(deleteBtn.dataset.id);

    }

});

function escapeHTML(str) {
        if (!str) return '';
        return String(str).replace(/[&<>'"]/g, tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag));
      };


const driverModal = document.getElementById('driver-modal');
const driverForm = document.getElementById('driver-form');
const modalTitle = document.getElementById('modal-title');

function openModal(driver = null) {
    
    driverForm.reset();

    driverModal.classList.remove("hidden");

    if (driver) {

        modalTitle.textContent = "Edit Driver";

        document.getElementById("form-driver-id").value = driver.driver_id;

        document.getElementById("form-name").value = driver.name;

        document.getElementById("form-email").value = driver.email;

        document.getElementById("form-contact-number").value = driver.contact_number;

        document.getElementById("form-license-number").value = driver.license_number;

        document.getElementById("form-license-category").value = driver.license_category;

        document.getElementById("form-license-expiry").value =
            driver.license_expiry_date;

        document.getElementById("form-safety-score").value =
            driver.safety_score;

        document.getElementById("form-status").value =
            driver.status;

        passwordWrapper.classList.add("hidden");

        document
            .getElementById("form-password")
            .removeAttribute("required");

    }

    else {

        modalTitle.textContent = "Add Driver";

        document.getElementById("form-driver-id").value = "";

        passwordWrapper.classList.remove("hidden");

        document
            .getElementById("form-password")
            .setAttribute("required", "required");

    }

};
function closeModal() { 
    driverModal.classList.add('hidden');
 };


function handleEditClick(id){

    const driver = driversCache.find(d => d.driver_id == id);

    if(driver){

        openModal(driver);

    }

}

async function handleDeleteClick(id){

    const confirmDelete = confirm(

        "Delete this driver?"

    );

    if(!confirmDelete) return;

    try{

        const response = await fetch(

            `${host}/api/drivers/${id}`,

            {

                method:"DELETE",

                credentials:"include"

            }

        );

        if(!response.ok){

            const err = await response.json();

            throw new Error(

                err.detail || "Delete Failed"

            );

        }

        showToast(

            "Driver deleted successfully",

            "success"

        );

        await loadDrivers();

    }

    catch(err){

        console.error(err);

        showToast(err.message,"error");

    }

}





// Search and Filters

const searchInput = document.getElementById("driver-search");
const statusFilter = document.getElementById("status-filter");
function handleSearchAndFilter() {

    const query = searchInput.value
        .toLowerCase()
        .trim();

    const status = statusFilter.value;

    const filtered = driversCache.filter(driver => {

        const matchSearch =

            driver.name.toLowerCase().includes(query) ||

            driver.email.toLowerCase().includes(query) ||

            driver.license_number.toLowerCase().includes(query) ||
            
            driver.contact_number.toLowerCase().includes(query);

        const matchStatus =

            status === "ALL" ||

            driver.status === status;

        return matchSearch && matchStatus;

    });

    renderTable(filtered);

    renderStats(filtered);

}

searchInput.addEventListener('input', handleSearchAndFilter);
statusFilter.addEventListener('change', handleSearchAndFilter);