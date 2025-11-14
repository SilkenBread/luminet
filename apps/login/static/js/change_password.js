$(function () {
    $('form').on('submit', function (e) {
        e.preventDefault();
        var parameters = new FormData(this);
        submit_with_ajax(window.location.pathname, 'Notificación', '¿Estas seguro de cambiar tu contraseña?', parameters, function () {
            Swal.fire({
                title: 'Notificación',
                text: 'Tu contraseña ha sido cambiada correctamente',
                icon: 'success',
            })
            setTimeout(function () {
                location.href = window.location.origin + '/login';
            }, 1500);
        });
    });
});
