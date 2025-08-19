function loadsec(page){
    fetch(`/load/${page}`)
    .then(response => {
        if(!response.ok) throw new Error("Erreur de chargement");
        return response.text();
    })
    .then(html => {
        document.getElementById('main-content').innerHTML=html;
    })
    .catch(error => {
        document.getElementById('main-content').innerHTML='<div class="alert alert-warning mt-3" style="width:300px;"><p>Erreur de chargement des données</p></div>'
    })
}

window.loadsec('reports')

function showToast(message, duration = 5000) {
    const container = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.classList.add('toast');
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}


document.addEventListener('submit', function(e){
    if(e.target.matches('form') && e.target.id !== 'export_pdf_form'){
        e.preventDefault();
        const form = e.target;
        const targetSelector = form.dataset.target
        fetch(form.action, {
            method: 'POST',
            body: new FormData(form)
        })
        .then(response => {
            if(!response.ok) throw new Error("Erreur de chargement");
            return response.text();
        })
        .then(html => {
            
            const target = document.querySelector(targetSelector) ;
            if(target) target.innerHTML = html;

            const depEl = document.getElementById("dep_id");
            const startEl = document.getElementById("start");
            const endEl = document.getElementById("end");

            if(depEl && startEl && endEl){
                document.getElementById("exp_dep_id").value = depEl.value;
                document.getElementById("exp_start_date").value = startEl.value;
                document.getElementById("exp_end_date").value = endEl.value;
            }

            console.log(depEl + startEl + endEl)

            if(form.action.endsWith('/update_emp')) {
                form.reset();
                form.style.display = "none";
                document.getElementById("input_id").value = "";
                showToast("Update Successful!")
            }

            if(form.action.endsWith('/create_admin')) {
                form.reset();
                form.style.display = "none";
                showToast("admin created !");
                window.loadsec('admin-manager')
            }

            
        })
        .catch(error => {
            const target = document.querySelector(targetSelector);
            form.reset();
            form.style.display = "none";
            if(target) target.innerHTML = '<div class="alert alert-danger mt-3" style="width:350px;"><p class="d-flex align-items-center">Erreur de chargement des données</p></div>';
        });
    }
});

function show_form(elmnt){
    const targeted_form = document.getElementById(elmnt);
    targeted_form.style.display = targeted_form.style.display === "none" ? "block" : "none";
}

document.addEventListener("click", function (e){
    if(e.target.matches(".btn-edit")){
        const row = e.target.closest("tr")
        document.getElementById("input_id").value = row.dataset.id;
        document.getElementById("input_name").value = row.querySelector(".name").textContent.trim();
        document.getElementById("input_email").value = row.querySelector(".email").textContent.trim();
        document.getElementById("input_sex").value = row.querySelector(".sex").textContent.trim();
        document.getElementById("input_department").value = row.dataset.departmentId;
        document.getElementById("input_position").value = row.dataset.positionId; 

        console.log(document.getElementById("input_department").value + " et " +document.getElementById("input_position").value )

        show_form("update_form");

    } else if(e.target.matches("#show_form")){

        show_form("register_form");
        
    } else if(e.target.matches("#register_form")){

        show_form("register_form");
        
    }else if(e.target.matches("#register_form2")){

        show_form("register_form2");
        
    }else if(e.target.matches("#show_form2")){

        show_form("register_form2");
        
    }else if(e.target.matches("#update_form")){

        show_form("update_form");
        
    } else if (e.target.matches(".btn-delete")) {
        const empId = e.target.closest("tr").dataset.id;
        
        if (confirm("Supprimer cet employé ?")) {
            fetch(`/delete_employee/${empId}`, {
                method: 'DELETE'
            })
            .then(res => {
                if (!res.ok) throw new Error("Erreur suppression");
                return res.json();
            })
            .then(data => {
                e.target.closest("tr").remove();
                showToast("Employee deleted !")
            })
            .catch(error => {
                console.error("Erreur :", error);
                alert("Échec de la suppression.");
            });
        }
    } else if (e.target.matches(".btn-delete2")) {
        const adId = e.target.closest("tr").dataset.id;    
        
        if (confirm("Supprimer cet admin ?")) {
            fetch(`/delete_admin/${adId}`, {
                method: 'DELETE'
            })
            .then(res => {
                if (!res.ok) throw new Error("Erreur suppression");
                return res.json();
            })
            .then(data => {
                e.target.closest("tr").remove();
                showToast("Admin deleted !")
            })
            .catch(error => {
                console.error("Erreur :", error);
                alert("Échec de la suppression.");
            });
        }
    }
})

document.querySelectorAll('.sidebar-link').forEach(link => {
  link.addEventListener('click', function (e) {
    e.preventDefault(); 
    document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
    this.classList.add('active');
  });
});