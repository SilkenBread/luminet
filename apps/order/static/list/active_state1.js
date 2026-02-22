// ============================================================
// Order Active State 1 - Por Asignar
// ============================================================

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

// Variables globales
let currentPage = 0;
let pageSize = 50;
let currentOrder = 'id';
let currentOrderDir = 'desc';
let currentSearch = '';
let totalRecords = 0;

let locateMap = null;
let locateMarker = null;

// ============================================================
// Carga de datos
// ============================================================

function loadOrdersData() {
    const inicio = currentPage * pageSize;

    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            action: 'searchdata',
            inicio: inicio,
            limite: pageSize,
            filtro: currentSearch,
            order_by: currentOrder,
            order_dir: currentOrderDir
        },
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        beforeSend: function () {
            $('#ordersTable tbody').html(`
                <tr>
                    <td colspan="11" class="text-center py-8">
                        <div class="flex items-center justify-center">
                            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        </div>
                    </td>
                </tr>
            `);
        },
        success: function (response) {
            if (response.type === 'success') {
                totalRecords = response.length;
                renderTable(response.objects);
                updatePagination();
            } else {
                showError(response.msg || 'Error al cargar los datos');
            }
        },
        error: function () {
            showError('No se pudieron cargar los datos');
        }
    });
}

function renderTable(data) {
    const tbody = $('#ordersTable tbody');
    tbody.empty();

    if (!data || data.length === 0) {
        tbody.html(`
            <tr>
                <td colspan="11" class="text-center py-8 text-gray-500">
                    <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-2 text-gray-400"></i>
                    <p>No se encontraron órdenes</p>
                </td>
            </tr>
        `);
        lucide.createIcons();
        return;
    }

    data.forEach(ot => {
        const row = `
            <tr class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm font-semibold text-blue-600">#${ot.id}</span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-700">${ot.fk_pqr__file_number || 'N/A'}</span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-700">${ot.date_creation || 'N/A'}</span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-700">${ot.date_limit || 'N/A'}</span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                    ${getRemainingTimeBadge(ot.remaining_time)}
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                    ${getPriorityBadge(ot.fk_priority__name)}
                </td>
                <td class="px-4 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        ${ot.fk_internal_type_damage__name || 'N/A'}
                    </span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-700">${ot.fk_pqr__fk_node_reported__fk_district__name || 'N/A'}</span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-700">${ot.fk_pqr__fk_node_reported__fk_district__fk_comuna__name || 'N/A'}</span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-700">${ot.fk_crew__name || 'Sin asignar'}</span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                    <div class="flex items-center justify-center gap-1">
                        <button onclick="locateOrder(${ot.fk_pqr__id})"
                                class="inline-flex items-center p-2 text-green-600 hover:text-green-800 hover:bg-green-50 rounded-lg transition-colors duration-200"
                                title="Ubicar en mapa">
                            <i data-lucide="map-pin" class="w-4 h-4"></i>
                        </button>
                        <button onclick="viewPqrDetail(${ot.fk_pqr__id})"
                                class="inline-flex items-center p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                                title="Ver detalle PQR">
                            <i data-lucide="eye" class="w-4 h-4"></i>
                        </button>
                        <button onclick="sendToField(${ot.id})"
                                class="inline-flex items-center p-2 text-yellow-600 hover:text-yellow-800 hover:bg-yellow-50 rounded-lg transition-colors duration-200"
                                title="Enviar a terreno">
                            <i data-lucide="send" class="w-4 h-4"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
        tbody.append(row);
    });

    lucide.createIcons();
}

// ============================================================
// Helpers
// ============================================================

function getPriorityBadge(priority) {
    const colors = {
        'Alta': 'bg-red-100 text-red-800',
        'Media': 'bg-yellow-100 text-yellow-800',
        'Baja': 'bg-gray-100 text-gray-800'
    };
    const cls = colors[priority] || 'bg-gray-100 text-gray-800';
    return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cls}">${priority || 'N/A'}</span>`;
}

function getRemainingTimeBadge(text) {
    if (!text) return '<span class="text-sm text-gray-400">N/A</span>';
    const isExpired = text === 'Tiempo Expirado';
    const cls = isExpired ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800';
    return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cls}">${text}</span>`;
}

function showError(message) {
    Swal.fire({ title: 'Error', text: message, icon: 'error', confirmButtonColor: '#3b82f6' });
}

// ============================================================
// Paginación
// ============================================================

function updatePagination() {
    const totalPages = Math.ceil(totalRecords / pageSize);
    const paginationContainer = $('#pagination-container');

    if (totalPages <= 1) {
        paginationContainer.html('');
        updateInfo();
        return;
    }

    let html = '<div class="flex items-center gap-2">';
    html += `<button onclick="changePage(${currentPage - 1})" ${currentPage === 0 ? 'disabled' : ''}
              class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
              <i data-lucide="chevron-left" class="w-4 h-4"></i></button>`;

    const maxVisible = 5;
    let startPage = Math.max(0, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages - 1, startPage + maxVisible - 1);
    if (endPage - startPage < maxVisible - 1) startPage = Math.max(0, endPage - maxVisible + 1);

    if (startPage > 0) {
        html += `<button onclick="changePage(0)" class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">1</button>`;
        if (startPage > 1) html += '<span class="px-2 text-gray-500">...</span>';
    }

    for (let i = startPage; i <= endPage; i++) {
        const cls = i === currentPage ? 'bg-blue-600 text-white' : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50';
        html += `<button onclick="changePage(${i})" class="px-3 py-2 text-sm font-medium rounded-lg ${cls}">${i + 1}</button>`;
    }

    if (endPage < totalPages - 1) {
        if (endPage < totalPages - 2) html += '<span class="px-2 text-gray-500">...</span>';
        html += `<button onclick="changePage(${totalPages - 1})" class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">${totalPages}</button>`;
    }

    html += `<button onclick="changePage(${currentPage + 1})" ${currentPage >= totalPages - 1 ? 'disabled' : ''}
              class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
              <i data-lucide="chevron-right" class="w-4 h-4"></i></button>`;
    html += '</div>';

    paginationContainer.html(html);
    lucide.createIcons();
    updateInfo();
}

function updateInfo() {
    const start = currentPage * pageSize + 1;
    const end = Math.min((currentPage + 1) * pageSize, totalRecords);
    const text = totalRecords > 0
        ? `Mostrando ${start} a ${end} de ${totalRecords} registros`
        : 'No hay registros para mostrar';
    $('#table-info').text(text);
}

function changePage(page) {
    const totalPages = Math.ceil(totalRecords / pageSize);
    if (page < 0 || page >= totalPages) return;
    currentPage = page;
    loadOrdersData();
}

function searchOrders() {
    currentSearch = $('#searchInput').val();
    currentPage = 0;
    loadOrdersData();
}

// ============================================================
// ACCIONES
// ============================================================

function locateOrder(pqrId) {
    const url = ORDER_URLS.pqrDetail.replace('{id}', pqrId);

    $.ajax({
        url: url,
        type: 'GET',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function (response) {
            if (response.type === 'success') {
                const pqr = response.data;
                const loc = pqr.node_location;

                if (!loc || !loc.lat || !loc.lng) {
                    Swal.fire({ title: 'Sin ubicación', text: 'Este nodo no tiene coordenadas registradas.', icon: 'warning', confirmButtonColor: '#3b82f6' });
                    return;
                }

                $('#locatePqr_nodeInfo').text(pqr.str_node_reported || loc.painting_code || '-');
                openModal('locatePqrModal');

                setTimeout(function () {
                    const center = { lat: parseFloat(loc.lat), lng: parseFloat(loc.lng) };
                    if (!locateMap) {
                        locateMap = new google.maps.Map(document.getElementById('locatePqrMap'), {
                            center: center, zoom: 17, mapTypeId: 'hybrid'
                        });
                        locateMarker = new google.maps.Marker({ position: center, map: locateMap });
                    } else {
                        locateMap.setCenter(center);
                        locateMarker.setPosition(center);
                    }
                    google.maps.event.trigger(locateMap, 'resize');
                }, 300);
            } else {
                showError(response.msg || 'Error al cargar la ubicación');
            }
        },
        error: function () {
            showError('Error al obtener información');
        }
    });
}

function viewPqrDetail(pqrId) {
    const url = ORDER_URLS.pqrDetail.replace('{id}', pqrId);

    $.ajax({
        url: url,
        type: 'GET',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        beforeSend: function () {
            Swal.fire({ title: 'Cargando...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
        },
        success: function (response) {
            Swal.close();
            if (response.type === 'success') {
                populateReviewModal(response.data);
                openModal('reviewPqrModal');
            } else {
                showError(response.msg || 'Error al cargar el detalle');
            }
        },
        error: function () {
            Swal.close();
            showError('Error al obtener el detalle del PQR');
        }
    });
}

function populateReviewModal(pqr) {
    $('#reviewPqr_fileNumber').text('#' + (pqr.file_number || ''));

    const statusMap = { 0: { text: 'Anulado', cls: 'bg-red-100 text-red-800' }, 1: { text: 'Recibido', cls: 'bg-blue-100 text-blue-800' }, 2: { text: 'En proceso', cls: 'bg-yellow-100 text-yellow-800' }, 3: { text: 'Atendida', cls: 'bg-green-100 text-green-800' } };
    const st = statusMap[pqr.status] || { text: 'Desconocido', cls: 'bg-gray-100 text-gray-800' };
    $('#reviewPqr_statusBadge').html(`<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${st.cls}">${st.text}</span>`);

    $('#reviewPqr_name').text(pqr.name || '-');
    $('#reviewPqr_dni').text(pqr.dni || '-');
    $('#reviewPqr_phone').text(pqr.telephone || '-');
    $('#reviewPqr_email').text(pqr.email || '-');
    $('#reviewPqr_node').text(pqr.str_node_reported || '-');
    $('#reviewPqr_damageType').text(pqr.str_type_damage || '-');
    $('#reviewPqr_origin').text(pqr.str_origin || '-');
    $('#reviewPqr_observation').text(pqr.observation || '-');
    $('#reviewPqr_dateCreation').text(pqr.date_creation || '-');

    // Route history
    const routeBody = $('#reviewPqr_routeHistory');
    routeBody.empty();
    if (pqr.route_history && pqr.route_history.length > 0) {
        pqr.route_history.forEach((r, i) => {
            routeBody.append(`
                <tr class="hover:bg-gray-50">
                    <td class="px-4 py-2 text-sm text-gray-700">${i + 1}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">${r.state || '-'}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">${r.date_entry || '-'}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">${r.date_exit || '-'}</td>
                </tr>
            `);
        });
    } else {
        routeBody.html('<tr><td colspan="4" class="text-center py-4 text-gray-400">Sin trazabilidad</td></tr>');
    }

    // Orders
    const ordersContainer = $('#reviewPqr_ordersContainer');
    ordersContainer.empty();
    if (pqr.orders && pqr.orders.length > 0) {
        pqr.orders.forEach(o => {
            ordersContainer.append(`<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">OT #${o.id}</span>`);
        });
    } else {
        ordersContainer.html('<span class="text-sm text-gray-400">Sin órdenes asociadas</span>');
    }
}

function sendToField(otId) {
    Swal.fire({
        title: '¿Enviar a Terreno?',
        text: `¿Deseas enviar la OT #${otId} a terreno?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3b82f6',
        cancelButtonColor: '#6b7280',
        confirmButtonText: 'Sí, enviar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            orderStatusChange(otId, 2);
        }
    });
}

function orderStatusChange(otId, state) {
    const url = ORDER_URLS.statusChange + `OrderActive/${otId}/${state}/`;

    $.ajax({
        url: url,
        type: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        beforeSend: function () {
            Swal.fire({ title: 'Procesando...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
        },
        success: function (response) {
            Swal.close();
            if (response.type === 'success') {
                Swal.fire({ title: 'Éxito', text: response.msg || 'Estado actualizado correctamente', icon: 'success', confirmButtonColor: '#3b82f6' })
                    .then(() => loadOrdersData());
            } else {
                showError(response.msg || 'Error al cambiar estado');
            }
        },
        error: function () {
            Swal.close();
            showError('Error al procesar la solicitud');
        }
    });
}

// ============================================================
// Init
// ============================================================

$(document).ready(function () {
    loadOrdersData();

    $('#searchInput').on('keyup', function (e) {
        if (e.key === 'Enter') searchOrders();
    });
});
