document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        
        // Mostrar confirmación con SweetAlert2
        const result = await Swal.fire({
            title: 'Notificación',
            text: '¿Estás seguro de cambiar tu contraseña?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sí, cambiar',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33'
        });
        
        if (!result.isConfirmed) {
            return;
        }
        
        // Obtener el token CSRF
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Crear FormData con los datos del formulario
        const formData = new FormData(this);
        
        try {
            // Hacer el fetch
            const response = await fetch(window.location.pathname, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });
            
            const data = await response.json();
            
            // Verificar si hubo errores
            if (data.error) {
                Swal.fire({
                    title: 'Error',
                    text: typeof data.error === 'string' ? data.error : 'Hubo un error al cambiar la contraseña',
                    icon: 'error'
                });
                return;
            }
            
            // Mostrar éxito
            await Swal.fire({
                title: 'Notificación',
                text: 'Tu contraseña ha sido cambiada correctamente',
                icon: 'success',
                timer: 1500,
                showConfirmButton: false
            });
            
            // Redirigir al login
            setTimeout(function () {
                window.location.href = window.location.origin + '/login';
            }, 1500);
            
        } catch (error) {
            Swal.fire({
                title: 'Error',
                text: 'Hubo un problema al procesar la solicitud',
                icon: 'error'
            });
            console.error('Error:', error);
        }
    });
});
