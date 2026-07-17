let vehiclesCache = [];


      // Fleet usage operational stats
function renderStats(vehicles){

    document.getElementById("total-vehicles-stat").textContent =
        vehicles.length;

    document.getElementById("available-vehicles-stat").textContent =
        vehicles.filter(v => v.status === "Available").length;

    document.getElementById("ontrip-vehicles-stat").textContent =
        vehicles.filter(v => v.status === "On Trip").length;

    document.getElementById("inshop-vehicles-stat").textContent =
        vehicles.filter(v => v.status === "In Shop").length;

}

      // Live formatting and element bindings
function renderTable(vehicles){

    const tbody=document.getElementById("vehicles-table-body");

    tbody.innerHTML="";

    if(vehicles.length===0){

        tbody.innerHTML=`
        <tr>

            <td colspan="7"
            class="py-10 text-center text-slate-400">

                No Vehicles Found

            </td>

        </tr>
        `;

        return;

    }

    vehicles.forEach(vehicle=>{

        let badgeClass="";

        switch(vehicle.status){

            case "Available":
                badgeClass="bg-emerald-50 text-emerald-700 border-emerald-200";
                break;

            case "On Trip":
                badgeClass="bg-sky-50 text-sky-700 border-sky-200";
                break;

            case "In Shop":
                badgeClass="bg-amber-50 text-amber-700 border-amber-200";
                break;

            case "Retired":
                badgeClass="bg-rose-50 text-rose-700 border-rose-200";
                break;

            default:
                badgeClass="bg-slate-50 text-slate-700 border-slate-200";

        }

        const row=document.createElement("tr");

        row.className="hover:bg-slate-50 transition";

        row.innerHTML=`

        <td class="py-4 px-6 font-semibold">

            ${escapeHTML(vehicle.registration_number)}

        </td>

        <td class="px-6">

            ${escapeHTML(vehicle.name_model)}

        </td>

        <td class="px-6">

            ${escapeHTML(vehicle.type)}

        </td>

        <td class="px-6">

            ${vehicle.max_load_capacity_kg}

        </td>

        <td class="px-6">

            ₹${vehicle.acquisition_cost.toLocaleString()}

        </td>

        <td class="px-6">

            <span class="px-2 py-1 rounded-full border text-xs font-semibold ${badgeClass}">

                ${vehicle.status}

            </span>

        </td>

        <td class="px-6 text-center">

            <div class="flex justify-center gap-2">

                <button
                class="edit-btn"
                data-id="${vehicle.vehicle_id}">

                    <i data-lucide="pencil" class="w-4 h-4"></i>

                </button>

                <button
                class="delete-btn"
                data-id="${vehicle.vehicle_id}">

                    <i data-lucide="trash-2" class="w-4 h-4"></i>

                </button>

            </div>

        </td>

        `;

        tbody.appendChild(row);

    });

    lucide.createIcons();

}

      // Escaper
function escapeHTML(str){

    return String(str ?? "").replace(

        /[&<>'"]/g,

        tag => ({

            "&":"&amp;",
            "<":"&lt;",
            ">":"&gt;",
            "'":"&#39;",
            '"':"&quot;"

        })[tag]

    );

}

// Fetch fleet assets from database rest interface
async function loadVehicles(){

    try{

        const response=await fetch(
            `${host}/api/vehicles`,
            {
                credentials:"include"
            }
        );

        if(!response.ok){

            throw new Error("Unable to load vehicles.");

        }

        vehiclesCache=await response.json();

        handleSearchAndFilter();
        renderStats(vehiclesCache);

    }

    catch(err){

        console.error(err);

        showToast(err.message,"error");

    }

}





// Search and Filtering 
const searchInput=document.getElementById("vehicle-search");

const statusFilter=document.getElementById("status-filter");

function handleSearchAndFilter(){

    const query=searchInput.value.toLowerCase();

    const status=statusFilter.value;

    const filtered=vehiclesCache.filter(vehicle=>{

        const matchesQuery=

        vehicle.registration_number.toLowerCase().includes(query) ||

        vehicle.name_model.toLowerCase().includes(query) ||

        vehicle.type.toLowerCase().includes(query);

        const matchesStatus=

        status==="ALL" ||

        vehicle.status===status;

        return matchesQuery && matchesStatus;

    });

    renderTable(filtered);

}

searchInput.addEventListener("input",handleSearchAndFilter);

statusFilter.addEventListener("change",handleSearchAndFilter);


      // Modal management
      const vehicleModal = document.getElementById('vehicle-modal');
      const vehicleForm = document.getElementById('vehicle-form');
      const modalTitle = document.getElementById('modal-title');

 function openModal(vehicle = null) {

    vehicleForm.reset();

    vehicleModal.classList.remove("hidden");

    if (vehicle) {

        modalTitle.textContent = "Edit Vehicle";

        document.getElementById("form-vehicle-id").value =
            vehicle.vehicle_id;

        document.getElementById("form-reg-number").value =
            vehicle.registration_number;

        document.getElementById("form-model").value =
            vehicle.name_model;

        document.getElementById("form-type").value =
            vehicle.type;

        document.getElementById("form-max-load").value =
            vehicle.max_load_capacity_kg;

        document.getElementById("form-acquisition-cost").value =
            vehicle.acquisition_cost;

    }

    else{

        modalTitle.textContent = "Add Vehicle";

        document.getElementById("form-vehicle-id").value="";

    }

}

      function closeModal() {
        vehicleModal.classList.add('hidden');
      }

      document.getElementById('add-vehicle-btn').addEventListener('click', () => openModal());
      document.getElementById('close-modal-btn').addEventListener('click', closeModal);
      document.getElementById('cancel-modal-btn').addEventListener('click', closeModal);



// Edit  and Delete       
      // Edit triggered
      function handleEditClick(id) {
        const vehicle = vehiclesCache.find(v => v.vehicle_id == id);
        if (vehicle) {
          openModal(vehicle);
        }
      }

      // Delete triggered
      async function handleDeleteClick(id) {
        const vehicle = vehiclesCache.find(v => v.vehicle_id == id);
        if (!vehicle) return;

        const confirmDelete = confirm(`Are you sure you want to permanently delete ${vehicle.registration_number} (${vehicle.name_model})?`);
        if (!confirmDelete) return;

        try {
          const response = await fetch(`${host}/api/vehicles/${id}`, {
            method: 'DELETE',
            credentials:"include" }
          );
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({})); 
  
            // 2. Fallback to a default message if the backend didn't provide one
            const backendMessage = errorData.message || 'Failed to delete Vehicle Due to Constraints .';
            
            // 3. Throw the backend error so your UI catch block can process it
            throw new Error(backendMessage);
          }
          showToast('Vehicle asset removed successfully', 'success');

          await loadVehicles();
        } catch (err) {
          
          console.error(err);

          showToast(err.message,"error");
        }

        
      }



vehicleForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = document.getElementById('form-vehicle-id').value;
        
        const isEdit = !!id;

        const payload = {

                        registration_number:
                            document.getElementById("form-reg-number").value.trim(),

                        name_model:
                            document.getElementById("form-model").value.trim(),

                        type:
                            document.getElementById("form-type").value.trim(),

                        max_load_capacity_kg:
                            Number(document.getElementById("form-max-load").value),

                        acquisition_cost:
                            Number(document.getElementById("form-acquisition-cost").value)

                    };
        try {
          let response;
          if (isEdit) {
            response = await fetch(`${host}/api/vehicles/${id}`, {
              method: 'PUT',
               credentials:"include",
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(payload)
            });
          } else {
            response = await fetch(`${host}/api/vehicles`, {
              method: 'POST',
              credentials:"include",
              headers: {
                'Content-Type': 'application/json',
                
              },
              body: JSON.stringify(payload)
            });
          }

          if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Asset sync crashed.');
          }

          showToast(isEdit ? 'Vehicle asset updated!' : 'Vehicle asset added!', 'success');
          closeModal();
          await loadVehicles();
        } catch (err) {
          console.error(err);

          showToast(err.message,"error");

        }

        
        
      });

const tbody = document.getElementById("vehicles-table-body");

tbody.addEventListener("click",(e)=>{

    const edit = e.target.closest(".edit-btn");

    if(edit){
        handleEditClick(edit.dataset.id);
        return;
    }

    const del = e.target.closest(".delete-btn");

    if(del){
        handleDeleteClick(del.dataset.id);
    }

});