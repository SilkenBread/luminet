$(function () {
    $('#checkPassRecoveryForm').on('submit', function (e) {
        e.preventDefault();

        if (!genericValidationForm("checkPassRecoveryForm")) {
            return;
        };

        const csrftoken = getCookie('csrftoken');
        const form = $(this).serializeArray();
        const formData = form.reduce((acc, field) => {
            acc[field.name] = field.value;
            return acc;
        }, {});

        fetch(window.location.pathname, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(formData),
        })
            .then(response => response.json())
            .then(data => {
                if (data.type === 'error') {
                    Swal.fire({
                        title: 'Notificación',
                        text: data.msg,
                        icon: 'error',
                        timer: 1500,
                        timerProgressBar: true,
                        showConfirmButton: false
                    });
                    return;
                }

                Swal.fire({
                    title: 'Notificación',
                    text: data.msg,
                    icon: 'success',
                    timer: 1000,
                    timerProgressBar: true,
                    showConfirmButton: false
                });
                setTimeout(function () {
                    location.href = window.location.origin;
                }, 1000);
            });
    });
});