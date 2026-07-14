
function setActiveSidebar() {

    const current = window.location.pathname;

    document.querySelectorAll(".nav-item").forEach(item => {

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

async function checkAuth(){

    try{

        const response=await fetch("http://127.0.0.1:8000/api/me",{

            credentials:"include"

        });

        if(!response.ok){

            window.location.href="/login";

            return null;

        }

        return await response.json();

    }

    catch(e){

        window.location.href="/login";

        return null;

    }

}