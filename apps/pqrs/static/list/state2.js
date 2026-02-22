// ============================================================
// PQR State 2 - En Revisión (Under Review)
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

let currentPage = 0;
let pageSize = 10;
let currentOrder = 'id';
let currentOrderDir = 'asc';
let currentSearch = '';
let totalRecords = 0;

let locateMap = null;
let locateMarker = null;

// ============================================================
// Carga de datos
// ============================================================

function loadPqrsData() {
    const inicio = currentPage * pageSize;
    const withOrders = $('#toggleWithOrders').is(':checked');

    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            action: 'searchdata',
            inicio: inicio,
            limite: pageSize,
            filtro: currentSearch,
            order_by: currentOrder,
            order_dir: currentOrderDir,
            with_orders: withOrders
        },
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        beforeSend: function () {
            $('#pqrsTable tbody').html(`
                <tr>
                    <td colspan="8" class="text-center py-8">
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
    const tbody = $('#pqrsTable tbody');
    tbody.empty();

    if (!data || data.length === 0) {
        tbody.html(`
            <tr>
                <td colspan="8" class="text-center py-8 text-gray-500">
                    <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-2 text-gray-400"></i>
                    <p>No se encontraron PQRs en revisión</p>
                </td>
            </tr>
        `);
        lucide.createIcons();
        return;
    }

    data.forEach(pqr => {
        const row = `
            <tr class="hover:bg-gray-50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm font-semibold text-blue-600">#${pqr.file_number || 'N/A'}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-700">${formatDate(pqr.date_creation)}</span>
                </td>
                <td class="px-6 py-4">
                    <span class="text-sm font-medium text-gray-900">${pqr.name || 'N/A'}</span>
                </td>
                <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        ${pqr.fk_type_damage__name || 'N/A'}
                    </span>
                </td>
                <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        ${pqr.fk_origin__name || 'N/A'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-700">${pqr.fk_node_reported__fk_district__fk_comuna__name || 'N/A'}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-700">${pqr.fk_node_reported__fk_district__name || 'N/A'}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center justify-center gap-1">
                        <button onclick="locatePqr(${pqr.id})"
                                class="inline-flex items-center p-2 text-green-600 hover:text-green-800 hover:bg-green-50 rounded-lg transition-colors duration-200"
                                title="Ubicar en mapa">
                            <i data-lucide="map-pin" class="w-4 h-4"></i>
                        </button>
                        <button onclick="viewPqrDetail(${pqr.id})"
                                class="inline-flex items-center p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                                title="Ver detalle">
                            <i data-lucide="eye" class="w-4 h-4"></i>
                        </button>
                        <button onclick="createOrder(${pqr.id})"
                                class="inline-flex items-center p-2 text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 rounded-lg transition-colors duration-200"
                                title="Crear orden de trabajo">
                            <i data-lucide="clipboard-list" class="w-4 h-4"></i>
                        </button>
                        <button onclick="openRejectPqr(${pqr.id}, '${pqr.file_number}')"
                                class="inline-flex items-center p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors duration-200"
                                title="Anular PQR">
                            <i data-lucide="x-circle" class="w-4 h-4"></i>
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

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    if (typeof dateString === 'string' && dateString.includes(' ')) return dateString;
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CO', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
    });
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

    if (totalPages <= 1) { paginationContainer.html(''); updateInfo(); return; }

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
    const text = totalRecords > 0 ? `Mostrando ${start} a ${end} de ${totalRecords} registros` : 'No hay registros para mostrar';
    $('#table-info').text(text);
}

function changePage(page) {
    const totalPages = Math.ceil(totalRecords / pageSize);
    if (page < 0 || page >= totalPages) return;
    currentPage = page;
    loadPqrsData();
}

function changePageSize(size) { pageSize = parseInt(size); currentPage = 0; loadPqrsData(); }

function searchPqrs() { currentSearch = $('#searchInput').val(); currentPage = 0; loadPqrsData(); }

function sortBy(column) {
    if (currentOrder === column) { currentOrderDir = currentOrderDir === 'asc' ? 'desc' : 'asc'; }
    else { currentOrder = column; currentOrderDir = 'asc'; }
    loadPqrsData();
}

// ============================================================
// ACCIONES: Ubicar PQR en mapa
// ============================================================

function locatePqr(pqrId) {
    const url = PQR_URLS.detail.replace('{id}', pqrId);
    $.ajax({
        url: url, type: 'GET',
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
                        locateMap = new google.maps.Map(document.getElementById('locatePqrMap'), { center: center, zoom: 17, mapTypeId: 'hybrid' });
                        locateMarker = new google.maps.Marker({ position: center, map: locateMap });
                    } else {
                        locateMap.setCenter(center);
                        locateMarker.setPosition(center);
                    }
                    google.maps.event.trigger(locateMap, 'resize');
                }, 300);
            } else { showError(response.msg || 'Error al cargar la ubicación'); }
        },
        error: function () { showError('Error al obtener información del PQR'); }
    });
}

// ============================================================
// ACCIONES: Ver detalle de PQR
// ============================================================

function viewPqrDetail(pqrId) {
    const url = PQR_URLS.detail.replace('{id}', pqrId);
    $.ajax({
        url: url, type: 'GET',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        beforeSend: function () { Swal.fire({ title: 'Cargando...', allowOutsideClick: false, didOpen: () => Swal.showLoading() }); },
        success: function (response) {
            Swal.close();
            if (response.type === 'success') { populateReviewModal(response.data); openModal('reviewPqrModal'); }
            else { showError(response.msg || 'Error al cargar el detalle'); }
        },
        error: function () { Swal.close(); showError('Error al obtener el detalle del PQR'); }
    });
}

function populateReviewModal(pqr) {
    $('#reviewPqr_fileNumber').text('#' + (pqr.file_number || ''));

    const statusColors = { 'Recibida': 'bg-blue-100 text-blue-800', 'En revisión': 'bg-yellow-100 text-yellow-800', 'Atendida': 'bg-green-100 text-green-800', 'Anulada': 'bg-red-100 text-red-800' };
    const statusClass = statusColors[pqr.status] || 'bg-gray-100 text-gray-800';
    $('#reviewPqr_statusBadge').attr('class', `inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusClass}`).text(pqr.status || '-');
    $('#reviewPqr_dateCreation').text(pqr.date_creation || '-');

    $('#reviewPqr_name').text(pqr.name || '-');
    $('#reviewPqr_dni').text(pqr.dni || '-');
    $('#reviewPqr_phone').text(pqr.phone_number || '-');
    $('#reviewPqr_email').text(pqr.email || '-');

    $('#reviewPqr_typeDamage').text(pqr.fk_type_damage || '-');
    $('#reviewPqr_origin').text(pqr.fk_origin || '-');
    $('#reviewPqr_node').text(pqr.str_node_reported || '-');
    $('#reviewPqr_location').text((pqr.comuna ? pqr.comuna + ' - ' : '') + (pqr.district || '-'));
    $('#reviewPqr_observation').text(pqr.observation || '-');

    const routeBody = $('#reviewPqr_routeHistory');
    routeBody.empty();
    if (pqr.route_history && pqr.route_history.length > 0) {
        pqr.route_history.forEach(route => {
            routeBody.append(`<tr class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm text-gray-700">${route.enum}</td>
                <td class="px-4 py-2 text-sm text-gray-700">${route.state || '-'}</td>
                <td class="px-4 py-2 text-sm text-gray-700">${route.input_date || '-'}</td>
                <td class="px-4 py-2 text-sm text-gray-700">${route.output_date || '-'}</td>
            </tr>`);
        });
    } else {
        routeBody.html('<tr><td colspan="4" class="px-4 py-3 text-center text-gray-400">Sin registros</td></tr>');
    }

    const ordersContainer = $('#reviewPqr_ordersContainer');
    ordersContainer.empty();
    if (pqr.orders && pqr.orders.length > 0) {
        let html = '<div class="space-y-2">';
        pqr.orders.forEach(order => {
            html += `<div class="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-3">
                <div><span class="text-sm font-semibold text-indigo-600">#${order.id}</span>
                <span class="text-sm text-gray-600 ml-2">${order.fk_internal_type_damage || ''}</span></div>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">${order.status || '-'}</span>
            </div>`;
        });
        html += '</div>';
        ordersContainer.html(html);
    } else {
        ordersContainer.html('<p class="text-sm text-gray-400 text-center py-3">Sin órdenes asociadas</p>');
    }
    lucide.createIcons();
}

// ============================================================
// ACCIONES: Crear Orden de Trabajo
// ============================================================

function createOrder(pqrId) {
    // Clear the form fields
    $('#createOrder_damageType').html('<option value="">Cargando...</option>');
    $('#createOrder_priority').html('<option value="">Cargando...</option>');
    $('#createOrder_timing').html('<option value="">Cargando...</option>');
    $('#createOrder_observation').val('');
    $('#createOrder_pqrId').val(pqrId);

    // Fetch dropdown fields from API
    $.ajax({
        url: ORDER_URLS.getFields,
        type: 'GET',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function (response) {
            if (response.type === 'success') {
                const data = response.data;

                // Populate Damage Type
                let dmgHtml = '<option value="">Selecciona un tipo de daño</option>';
                data.listIntDamage.forEach(item => { dmgHtml += `<option value="${item.id}">${item.name}</option>`; });
                $('#createOrder_damageType').html(dmgHtml);

                // Populate Priority
                let prioHtml = '<option value="">Selecciona la prioridad</option>';
                data.listPriority.forEach(item => { prioHtml += `<option value="${item.id}">${item.name}</option>`; });
                $('#createOrder_priority').html(prioHtml);

                // Populate Timing
                let timHtml = '<option value="">Selecciona el tiempo</option>';
                data.listTiming.forEach(item => { timHtml += `<option value="${item.id}">${item.name}</option>`; });
                $('#createOrder_timing').html(timHtml);

                openModal('createOrderModal');
                lucide.createIcons();
            } else {
                showError(response.msg || 'Error al cargar los campos');
            }
        },
        error: function () {
            showError('Error al cargar los campos del formulario');
        }
    });
}

function confirmCreateOrder() {
    const pqrId = $('#createOrder_pqrId').val();
    const damageType = $('#createOrder_damageType').val();
    const priority = $('#createOrder_priority').val();
    const timing = $('#createOrder_timing').val();
    const observation = $('#createOrder_observation').val();

    // Validate required fields
    if (!damageType || !priority || !timing || !observation.trim()) {
        Swal.fire({
            title: 'Campos requeridos',
            text: 'Todos los campos son obligatorios',
            icon: 'warning',
            confirmButtonColor: '#3b82f6'
        });
        return;
    }

    // Step 1: Confirm creation — check for existing orders
    $.ajax({
        url: ORDER_URLS.confirmCreation,
        type: 'POST',
        data: { pqr: pqrId },
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function (response) {
            if (response.type === 'success') {
                let confirmMsg = '¿Quieres crear la orden de trabajo?';
                if (response.msg) confirmMsg += '\n' + response.msg;

                Swal.fire({
                    title: 'Crear Orden de Trabajo',
                    text: confirmMsg,
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: '#6366f1',
                    cancelButtonColor: '#6b7280',
                    confirmButtonText: 'Sí, crear',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Step 2: Actually create the order
                        $.ajax({
                            url: ORDER_URLS.setOrderActive,
                            type: 'POST',
                            data: {
                                id: pqrId,
                                fk_internal_type_damage: damageType,
                                fk_priority: priority,
                                fk_timingrepair: timing,
                                internal_observation: observation
                            },
                            headers: { 'X-CSRFToken': getCookie('csrftoken') },
                            beforeSend: function () {
                                Swal.fire({ title: 'Creando orden...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
                            },
                            success: function (res) {
                                Swal.close();
                                if (res.type === 'success') {
                                    closeModal('createOrderModal');
                                    Swal.fire({
                                        title: '¡Orden Creada!',
                                        text: res.msg || 'La orden de trabajo se creó exitosamente',
                                        icon: 'success',
                                        confirmButtonColor: '#3b82f6',
                                        timer: 2500
                                    }).then(() => loadPqrsData());
                                } else {
                                    showError(res.msg || 'Error al crear la orden');
                                }
                            },
                            error: function () {
                                Swal.close();
                                showError('Error al crear la orden de trabajo');
                            }
                        });
                    }
                });
            } else {
                showError(response.msg || 'Error al verificar la creación');
            }
        },
        error: function () {
            showError('Error al verificar la creación');
        }
    });
}

// ============================================================
// ACCIONES: Anular PQR
// ============================================================

function openRejectPqr(pqrId, fileNumber) {
    $('#rejectPqr_id').val(pqrId);
    $('#rejectPqr_fileNumber').text('#' + fileNumber);

    const causeSelect = $('#rejectPqr_cause');
    causeSelect.html('<option value="">Cargando causas...</option>');

    $.ajax({
        url: PQR_URLS.reject, type: 'GET',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function (response) {
            if (response.type === 'success') {
                causeSelect.html('<option value="">Seleccione una causa...</option>');
                response.data.forEach(cause => causeSelect.append(`<option value="${cause.id}">${cause.name}</option>`));
            } else { causeSelect.html('<option value="">Error al cargar causas</option>'); }
        },
        error: function () { causeSelect.html('<option value="">Error al cargar causas</option>'); }
    });

    openModal('rejectPqrModal');
    lucide.createIcons();
}

function confirmRejectPqr() {
    const pqrId = $('#rejectPqr_id').val();
    const causeId = $('#rejectPqr_cause').val();

    if (!causeId) {
        Swal.fire({ title: 'Atención', text: 'Debe seleccionar una causa de anulación', icon: 'warning', confirmButtonColor: '#3b82f6' });
        return;
    }

    Swal.fire({
        title: '¿Anular PQR?',
        text: 'Esta acción no se puede deshacer. La PQR será anulada permanentemente.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#6b7280',
        confirmButtonText: 'Sí, anular',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: PQR_URLS.reject, type: 'POST',
                data: { pqr: pqrId, cause: causeId },
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                success: function (response) {
                    if (response.type === 'success') {
                        closeModal('rejectPqrModal');
                        Swal.fire({ title: '¡Anulada!', text: 'La PQR ha sido anulada exitosamente', icon: 'success', confirmButtonColor: '#3b82f6', timer: 2000 })
                            .then(() => loadPqrsData());
                    } else { showError(response.msg || 'Error al anular la PQR'); }
                },
                error: function () { showError('Error al anular la PQR'); }
            });
        }
    });
}

// ============================================================
// Inicialización
// ============================================================

$(document).ready(function () {
    const controlsHTML = `
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <div class="flex items-center gap-2">
                <label class="text-sm font-medium text-gray-700">Mostrar</label>
                <select id="pageSizeSelect" onchange="changePageSize(this.value)"
                        class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm">
                    <option value="10">10</option>
                    <option value="25">25</option>
                    <option value="50">50</option>
                    <option value="100">100</option>
                </select>
                <label class="text-sm font-medium text-gray-700">registros</label>
            </div>
            <div class="flex items-center gap-2">
                <label class="text-sm font-medium text-gray-700">Buscar:</label>
                <input type="text" id="searchInput"
                       class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                       placeholder="Buscar..."
                       onkeyup="if(event.key === 'Enter') searchPqrs()">
                <button onclick="searchPqrs()"
                        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors duration-200">
                    <i data-lucide="search" class="w-4 h-4"></i>
                </button>
            </div>
        </div>
    `;

    const footerHTML = `
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mt-4">
            <div id="table-info" class="text-sm text-gray-700"></div>
            <div id="pagination-container"></div>
        </div>
    `;

    $('#pqrsTable').before(controlsHTML);
    $('#pqrsTable').closest('.overflow-x-auto').after(footerHTML);

    // Toggle listener
    $('#toggleWithOrders').on('change', function () {
        currentPage = 0;
        loadPqrsData();
    });

    lucide.createIcons();
    loadPqrsData();
});
