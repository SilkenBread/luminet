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

// Variables globales para paginación y ordenamiento
let currentPage = 0;
let pageSize = 10;
let currentOrder = 'id';
let currentOrderDir = 'asc';
let currentSearch = '';
let totalRecords = 0;

// Función para cargar datos
function loadPqrsData(draw = 1) {
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
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        beforeSend: function() {
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
        success: function(response) {
            if (response.type === 'success') {
                totalRecords = response.length;
                renderTable(response.objects);
                updatePagination();
            } else {
                showError(response.msg || 'Error al cargar los datos');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            showError('No se pudieron cargar los datos');
        }
    });
}

// Función para renderizar la tabla
function renderTable(data) {
    const tbody = $('#pqrsTable tbody');
    tbody.empty();
    
    if (data.length === 0) {
        tbody.html(`
            <tr>
                <td colspan="8" class="text-center py-8 text-gray-500">
                    <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-2 text-gray-400"></i>
                    <p>No se encontraron PQRs</p>
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
                        <button onclick="sendToReview(${pqr.id}, '${pqr.file_number}')" 
                                class="inline-flex items-center p-2 text-yellow-600 hover:text-yellow-800 hover:bg-yellow-50 rounded-lg transition-colors duration-200"
                                title="Enviar a revisión">
                            <i data-lucide="send" class="w-4 h-4"></i>
                        </button>
                        <button onclick="createOrder(${pqr.id})" 
                                class="inline-flex items-center p-2 text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 rounded-lg transition-colors duration-200"
                                title="Crear orden">
                            <i data-lucide="clipboard-list" class="w-4 h-4"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
        tbody.append(row);
    });
    
    // Reinicializar iconos de Lucide
    lucide.createIcons();
}

// Función para formatear fecha
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Función para actualizar paginación
function updatePagination() {
    const totalPages = Math.ceil(totalRecords / pageSize);
    const paginationContainer = $('#pagination-container');
    
    if (totalPages <= 1) {
        paginationContainer.html('');
        updateInfo();
        return;
    }
    
    let paginationHTML = '<div class="flex items-center gap-2">';
    
    // Botón anterior
    paginationHTML += `
        <button onclick="changePage(${currentPage - 1})" 
                ${currentPage === 0 ? 'disabled' : ''}
                class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            <i data-lucide="chevron-left" class="w-4 h-4"></i>
        </button>
    `;
    
    // Páginas
    const maxVisiblePages = 5;
    let startPage = Math.max(0, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages - 1, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(0, endPage - maxVisiblePages + 1);
    }
    
    if (startPage > 0) {
        paginationHTML += `
            <button onclick="changePage(0)" 
                    class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
                1
            </button>
        `;
        if (startPage > 1) {
            paginationHTML += '<span class="px-2 text-gray-500">...</span>';
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const isActive = i === currentPage;
        paginationHTML += `
            <button onclick="changePage(${i})" 
                    class="px-3 py-2 text-sm font-medium rounded-lg ${isActive ? 'bg-blue-600 text-white' : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'}">
                ${i + 1}
            </button>
        `;
    }
    
    if (endPage < totalPages - 1) {
        if (endPage < totalPages - 2) {
            paginationHTML += '<span class="px-2 text-gray-500">...</span>';
        }
        paginationHTML += `
            <button onclick="changePage(${totalPages - 1})" 
                    class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
                ${totalPages}
            </button>
        `;
    }
    
    // Botón siguiente
    paginationHTML += `
        <button onclick="changePage(${currentPage + 1})" 
                ${currentPage >= totalPages - 1 ? 'disabled' : ''}
                class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            <i data-lucide="chevron-right" class="w-4 h-4"></i>
        </button>
    `;
    
    paginationHTML += '</div>';
    paginationContainer.html(paginationHTML);
    lucide.createIcons();
    updateInfo();
}

// Función para actualizar información de registros
function updateInfo() {
    const start = currentPage * pageSize + 1;
    const end = Math.min((currentPage + 1) * pageSize, totalRecords);
    const infoText = totalRecords > 0 
        ? `Mostrando ${start} a ${end} de ${totalRecords} registros`
        : 'No hay registros para mostrar';
    
    $('#table-info').text(infoText);
}

// Función para cambiar página
function changePage(page) {
    const totalPages = Math.ceil(totalRecords / pageSize);
    if (page < 0 || page >= totalPages) return;
    currentPage = page;
    loadPqrsData();
}

// Función para cambiar tamaño de página
function changePageSize(size) {
    pageSize = parseInt(size);
    currentPage = 0;
    loadPqrsData();
}

// Función para buscar
function searchPqrs() {
    currentSearch = $('#searchInput').val();
    currentPage = 0;
    loadPqrsData();
}

// Función para ordenar
function sortBy(column) {
    if (currentOrder === column) {
        currentOrderDir = currentOrderDir === 'asc' ? 'desc' : 'asc';
    } else {
        currentOrder = column;
        currentOrderDir = 'asc';
    }
    loadPqrsData();
}

// Función para mostrar error
function showError(message) {
    Swal.fire({
        title: 'Error',
        text: message,
        icon: 'error',
        confirmButtonColor: '#3b82f6'
    });
}

// Funciones de acciones
function locatePqr(pqrId) {
    // TODO: Implementar lógica para ubicar en mapa
    console.log('Ubicar PQR:', pqrId);
    Swal.fire({
        title: 'Ubicar en Mapa',
        text: 'Funcionalidad en desarrollo',
        icon: 'info',
        confirmButtonColor: '#3b82f6'
    });
}

function viewPqrDetail(pqrId) {
    // TODO: Implementar lógica para ver detalle
    console.log('Ver detalle PQR:', pqrId);
    Swal.fire({
        title: 'Ver Detalle',
        text: 'Funcionalidad en desarrollo',
        icon: 'info',
        confirmButtonColor: '#3b82f6'
    });
}

function sendToReview(pqrId, fileNumber) {
    Swal.fire({
        title: '¿Enviar a revisión?',
        html: `¿Desea enviar la PQR <strong>#${fileNumber}</strong> a revisión?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3b82f6',
        cancelButtonColor: '#6b7280',
        confirmButtonText: 'Sí, enviar',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            // TODO: Implementar lógica para enviar a revisión
            console.log('Enviar a revisión:', pqrId);
            Swal.fire({
                title: '¡Enviado!',
                text: 'La PQR ha sido enviada a revisión',
                icon: 'success',
                confirmButtonColor: '#3b82f6',
                timer: 2000
            }).then(() => {
                loadPqrsData();
            });
        }
    });
}

function createOrder(pqrId) {
    // TODO: Implementar lógica para crear orden
    console.log('Crear orden para PQR:', pqrId);
    Swal.fire({
        title: 'Crear Orden',
        text: 'Funcionalidad en desarrollo',
        icon: 'info',
        confirmButtonColor: '#3b82f6'
    });
}

// Inicialización cuando el DOM esté listo
$(document).ready(function() {
    // Crear controles de paginación y búsqueda
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
    
    // Inicializar iconos
    lucide.createIcons();
    
    // Cargar datos iniciales
    loadPqrsData();
});