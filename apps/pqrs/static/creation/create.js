// Usado para la creación de PQRs activas en el componente interno y externo de la aplicación

// Función helper para obtener el CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Función para agregar opciones a un select
function appendOptions(selectId, data) {
    const select = document.querySelector(selectId);
    if (!select) return;
    
    data.forEach(item => {
        const option = document.createElement('option');
        option.value = item.id;
        option.textContent = item.name;
        select.appendChild(option);
    });
}

async function appendOptionsPqrCreation() {
    try {
        const formData = new FormData();
        formData.append('action', 'getTypeDamage');
        
        const response = await fetch(window.location.pathname, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.type === 'success') {
            appendOptions("#typeDamage", data.data.typeDamage);
            appendOptions("#origin", data.data.origin);
        } else {
            console.error('Error al cargar opciones:', data.msg);
        }
    } catch (error) {
        console.error('Error en la petición:', error);
    }
}

async function creationPqr(data) {
    try {
        showLoader();
        
        const response = await fetch(`${window.location.origin}/pqr/api/create/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(data)
        });
        
        const result = await response.json();
        hideLoader();
        
        if (result.type === "success") {
            const swalResult = await Swal.fire({
                title: "¡Correcto!",
                text: result.msg,
                icon: result.type,
                confirmButtonColor: "#3085d6",
                confirmButtonText: "Consultar",
                showCancelButton: true,
                cancelButtonText: "Cerrar"
            });
            
            if (swalResult.isConfirmed) {
                window.open(`${window.location.origin}/pqr/search/`, '_blank');
            }
            location.reload();
        } else {
            Swal.fire({
                icon: result.type,
                title: "¡Error!",
                text: result.msg,
            });
        }
    } catch (error) {
        hideLoader();
        Swal.fire({
            icon: 'error',
            title: "¡Error!",
            text: 'Ha ocurrido un error al crear la PQR',
        });
        console.error('Error:', error);
    }
}
