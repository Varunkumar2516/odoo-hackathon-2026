

const host = 'http://127.0.0.1:8000';

 // Security Helper
function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
          tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
      }

function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.className = 'toast ' + type;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
      }
function setupHeaderProfile() {
    try {
        const userStr = localStorage.getItem('user');
        if (userStr) {
        const user = JSON.parse(userStr);
        const badge = document.getElementById('user-badge');
        if (badge && user.email) {
            badge.textContent = user.email.substring(0, 2).toUpperCase();
        }
        }
    } catch (err) {
        console.warn(err);
    }
    };
      // Render calculations dynamically
function renderStats(users) {
        document.getElementById('total-users-stat').textContent = users.length;
        document.getElementById('total-admins-stat').textContent = users.filter(u => u.role === 'admin').length;
        document.getElementById('total-ops-stat').textContent = users.filter(u => u.role === 'Dispatcher' || u.role === 'Fleet Manager').length;
        document.getElementById('total-finance-stat').textContent = users.filter(u => u.role === 'Financial Analyst').length;
      }
const userModal = document.getElementById('user-modal');
const userForm = document.getElementById('user-form');
const modalTitle = document.getElementById('modal-title');
const passwordWrapper = document.getElementById('password-form-wrapper');


// Reset & Open Modal
function openModal(user = null) {
        userForm.reset();
        userModal.classList.remove('hidden');
        
        if (user) {
          modalTitle.textContent = 'Edit User Profile';
          document.getElementById('form-user-id').value = user.user_id;
          document.getElementById('form-name').value = user.name;
          document.getElementById('form-email').value = user.email;
          document.getElementById('form-role').value = user.role;
          
          // Hide password editing during update constraints (managed separately for security)
          passwordWrapper.classList.add('hidden');
          document.getElementById('form-password').removeAttribute('required');
        } else {
          modalTitle.textContent = 'Add New User';
          document.getElementById('form-user-id').value = '';
          
          passwordWrapper.classList.remove('hidden');
          document.getElementById('form-password').setAttribute('required', 'required');
        }
      }

function closeModal() {
        userModal.classList.add('hidden');
      }

// Edit click action
function handleEditClick(id) {
        const user = usersCache.find(u => u.user_id == id);
        if (user) {
          openModal(user);
        }
      }

// Delete user details
async function handleDeleteClick(id) {

    const confirmDelete = confirm("Are you sure you want to delete this user?");
    if (!confirmDelete) return;

    try {

        const response = await fetch(`${host}/api/users/${id}`, {
            method: "DELETE",
            credentials: "include"
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Delete failed");
        }

        showToast("User deleted successfully", "success");

        await new Promise(resolve => setTimeout(resolve, 200));

        await loadUsers();

        console.log("After delete:", usersCache);

    } catch (err) {
        console.error(err);
        showToast(err.message, "error");
    }
}


// Render beautiful table data
function renderTable(users) {
    const tbody = document.getElementById("users-table-body");
    tbody.innerHTML = "";

    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="py-12 text-center text-slate-400">
                    <div class="flex flex-col items-center justify-center gap-2">
                        <i data-lucide="search-code" class="w-8 h-8 text-slate-300"></i>
                        <span>No matching user accounts found</span>
                    </div>
                </td>
            </tr>
        `;
        lucide.createIcons();
        return;
    }

    users.forEach(user => {

        let badgeClass = "bg-slate-50 text-slate-700 border-slate-200";

        if (user.role === "admin")
            badgeClass = "bg-purple-50 text-purple-700 border-purple-200";
        else if (user.role === "Fleet Manager")
            badgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
        else if (user.role === "Dispatcher")
            badgeClass = "bg-sky-50 text-sky-700 border-sky-200";
        else if (user.role === "Safety Officer")
            badgeClass = "bg-amber-50 text-amber-700 border-amber-200";
        else if (user.role === "Financial Analyst")
            badgeClass = "bg-blue-50 text-blue-700 border-blue-200";

        const formattedDate = user.created_at
            ? new Date(user.created_at).toLocaleDateString("en-GB", {
                  day: "numeric",
                  month: "short",
                  year: "numeric"
              })
            : "-";

        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-50/70 transition-colors";

        tr.innerHTML = `
            <td class="py-4 px-6 font-semibold text-slate-900">${escapeHTML(user.name)}</td>
            <td class="px-6 text-slate-500">${escapeHTML(user.email)}</td>
            <td class="px-6">
                <span class="inline-flex items-center gap-1 px-2.5 py-0.5 border rounded-full text-xs font-semibold ${badgeClass}">
                    ${escapeHTML(user.role)}
                </span>
            </td>
            <td class="px-6 text-slate-500">${formattedDate}</td>
            <td class="px-6 text-center">
                <div class="flex items-center justify-center gap-2">
                    <button class="edit-btn p-1.5 rounded-lg text-slate-500 hover:bg-slate-50 hover:text-sky-600 transition-all"
                            data-id="${user.user_id}">
                        <i data-lucide="pencil" class="w-4 h-4"></i>
                    </button>

                    <button class="delete-btn p-1.5 rounded-lg text-slate-500 hover:bg-rose-50 hover:text-rose-600 transition-all"
                            data-id="${user.user_id}">
                        <i data-lucide="trash-2" class="w-4 h-4"></i>
                    </button>
                </div>
            </td>
        `;

        tbody.appendChild(tr);
    });

    lucide.createIcons();
}
const tbody = document.getElementById("users-table-body");

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
// Load Users list from DB or Fallback Mock DB
async function loadUsers() {
    try {
        const response = await fetch(`${host}/api/users`, {
        credentials:"include"
        });
        console.log("GET Status:", response.status);

        if (!response.ok) {
        throw new Error("Unable to load users.");
        } 
        usersCache = await response.json();
    } catch (err) {
        console.warn("Backend server not responding. Rendering premium fallback user cache.", err);
    }
    renderTable(usersCache);
    renderStats(usersCache);
    };


async function loading(){


    await loadSidebar();
    const user=await checkAuth();

    if(!user) return;

    setupHeaderProfile(user);

    setActiveSidebar();

    await loadUsers();

    lucide.createIcons();
};