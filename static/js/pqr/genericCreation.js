/**
 * Gestionar creacion de una PQR
 * @module Report
 * @author Juan David Rodriguez <jua0729.jr@gmail.com>
 */

const ArrayMarker = [];
let markersArray = [];
let infowindowsArray = [];
let nodeCircle;
let centerCircle;
let currentInfoWindow = null;

// Función auxiliar para validación de formularios
function genericValidationForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return false;
    }
    
    return true;
}

// Función auxiliar para SweetAlert simplificado
function sweetAlert(title, text, icon) {
    Swal.fire({
        title: title,
        text: text,
        icon: icon,
        confirmButtonColor: '#3b82f6'
    });
}

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

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar Select2 si está disponible
    if (typeof jQuery !== 'undefined' && typeof jQuery.fn.select2 === 'function') {
        $('.select2').select2({
            language: 'es',
            placeholder: 'Seleccionar'
        });
    }
    
    // Al recargar remueve el nodo guardado si existe
    sessionStorage.removeItem("nodeToReport");
    
    document.getElementById('stepname').textContent = "1. Ubicar poste";
    document.getElementById('step2').style.display = "none";
    
    document.getElementById('selectLocationType').addEventListener('change', function() {
        cleanMarkers();
        
        // Limpiar todos los inputs
        document.querySelectorAll('input').forEach(input => input.value = '');
        
        const selectedValue = this.value;
        const searchNodeInMap = document.getElementById('searchNodeInMap');
        const pacContainer = document.getElementById('pac-container');
        
        if (selectedValue == 1) {
            searchNodeInMap.classList.remove('hidden');
            searchNodeInMap.style.display = 'block';
            pacContainer.classList.add('hidden');
            pacContainer.style.display = 'none';
        } else if (selectedValue == 2) {
            searchNodeInMap.classList.add('hidden');
            searchNodeInMap.style.display = 'none';
            pacContainer.classList.remove('hidden');
            pacContainer.style.display = 'block';
        } else {
            searchNodeInMap.classList.add('hidden');
            searchNodeInMap.style.display = 'none';
            pacContainer.classList.add('hidden');
            pacContainer.style.display = 'none';
        }
    });
});

// Funcion ejecutada despues del callback de cargar GoogleMaps
function posMapsRender() {
    google.maps.event.addListener(map, "zoom_changed", function () {
        let zoom = map.getZoom();
        // Muestra u oculta los marcadores de acuerdo con el nivel de zoom
        if (zoom <= 16) {
            assignMarkers(markersArray, null);
        } else {
            assignMarkers(markersArray, map);
        }
    });
    // Input para la búsqueda
    const input = document.getElementById("pac-input");
    const options = {
        fields: ["formatted_address", "geometry", "name"],
        componentRestrictions: { country: "CO" },
        bounds: map_bounds,
        strictBounds: false,
    };
    const autocomplete = new google.maps.places.Autocomplete(input, options);
    autocomplete.bindTo("bounds", map);
    
    // Se crea el círculo en el mapa pero no se muestra hasta asignarle una posición
    nodeCircle = new google.maps.Circle({
        strokeColor: "#0000FF",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#0000FF",
        fillOpacity: 0.1,
        map,
        radius: 120,
    });
    centerCircle = new google.maps.Circle({
        strokeColor: "#0000FF",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#0000FF",
        fillOpacity: 0.5,
        map,
        radius: 2.5,
    });
    // Cuando cambia el input de búsqueda, ejecuta la función de geocodificación
    autocomplete.addListener("place_changed", () => {
        searchingByAddress("null");
    });
}

let currentStep = 1;
/**
 * Se usa para validar con promises pasar del Paso 1 al 2
 * @author Juan David Rodriguez <jua0729.jr@gmail.com>
 */
async function nextStep() {
    if (currentStep === 1) {
        try {
            await validateStep2ByNextBtn();
            currentStep++;
            updateProgress();
        } catch (error) {
            Swal.fire({
                title:"¡Advertencia!",
                html: error.message || "Hubo un problema al validar la selección del poste",
                icon: "warning",
                confirmButtonColor: '#f92c2c'
            });
        }
    }
}
/**
 * Se usa para retroceder un paso en el Stepper
 * @author Juan David Rodriguez <jua0729.jr@gmail.com>
 */
function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateProgress();
    }
}
/**
 * Se usa para aplicar estilos y ejecutar metodos de acuerdo al paso que este
 * @author Juan David Rodriguez <jua0729.jr@gmail.com>
 */
function updateProgress() {
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const bar2 = document.getElementById("bar2");
    const stepname = document.getElementById("stepname");
    const step1 = document.getElementById("step1");
    const step2 = document.getElementById("step2");
    
    prevBtn.disabled = currentStep === 1;
    nextBtn.disabled = currentStep === 2;
    
    if (currentStep === 1) {
        bar2.classList.remove("bg-blue-600");
        bar2.classList.add("bg-gray-300");
        stepname.textContent = "1. Ubicar poste";
        step1.style.display = "block";
        step2.style.display = "none";
    } else if (currentStep === 2) {
        resetPqrFields();
        appendOptionsPqrCreation();
        cleanMarkers();

        document.querySelectorAll('input').forEach(input => input.value = '');
        bar2.classList.remove("bg-gray-300");
        bar2.classList.add("bg-blue-600");
        stepname.textContent = "2. Tipo de daño e Información personal";
        step1.style.display = "none";
        step2.style.display = "block";
    }
}

/**
 * Se usa para aplicar estilos y ejecutar metodos de acuerdo al paso que este
 * @author Juan David Rodriguez <jua0729.jr@gmail.com>
 */
function consultarDetalles() {
    cleanMarkers();

    const typeSearchChoice = Number(document.getElementById('selectLocationType').value);
    const valuePaintingCode = document.getElementById('inputPaintingCode').value;
    const valueAddress = document.getElementById('pac-input').value;
    
    switch (typeSearchChoice) {
        case 1:
            document.getElementById('pac-input').value = '';
            searchingByPaintingCode(valuePaintingCode);
            break;
        case 2:
            document.getElementById('inputPaintingCode').value = '';
            searchingByAddress(valueAddress);
            break;
        default:
            sweetAlert("¡Error!", `No se encontró un tipo de búsqueda`, "error");
    }
}

async function searchingByPaintingCode(val_pc) {
    if (val_pc.trim() === "") {
        sweetAlert(
            "Campo vacío",
            `Por favor, ingrese un valor en el campo de búsqueda.`,
            "warning"
        );
        return;
    }
    
    if (val_pc.length === 7 || val_pc === "0") {
        try {
            showLoader();
            
            const response = await fetch(`${window.location.origin}/infrastructure/searchNodesByPaintingCode/${val_pc}/`);
            const data = await response.json();
            
            hideLoader();
            
            if (data.type === 'error') {
                sweetAlert(
                    "Sin resultados",
                    `No se encontraron nodos con el código de pintado ${val_pc}`,
                    "question"
                );
            } else {
                const nodesResult = data.data;
                
                nodesResult.forEach((node) => {
                    let marker = new google.maps.Marker({
                        position: {
                            lat: node.lat, lng: node.lng
                        },
                        map,
                        icon: "/static/img/markers/nodemarker.png",
                    });
                    
                    ArrayMarker.push(marker);
                    
                    let infoWindow = new google.maps.InfoWindow({
                        content:
                        `<table class='table'>
                            <tr>
                                <td><b>Código del poste:</b></td>
                                <td> ${node.painting_code}</td> 
                            </tr>
                            <tr>
                                <td><b>Zona:</b></td>
                                <td> ${node.comuna}</td> 
                            </tr>
                            <tr>
                                <td><b>Barrio:</b></td>
                                <td> ${node.district}</td> 
                            </tr>
                        </table>
                        <div class="text-center">
                            <a id="selectNodeToReport" class='btn btn-outline-danger btn-sm' onclick='selectNode(${node.pk}, ${node.painting_code});'>Seleccionar poste</a>
                        </div>`,
                    });
                    
                    // Agrega el listener al marcador para abrir el infowindow
                    marker.addListener("click", () => {
                        // Centra el mapa en el marcador
                        map.panTo(marker.position);
                        // Abre el infowindow
                        infoWindow.open({
                            anchor: marker,
                            map,
                        });
                    });
                    // Abre los infoeindow de todos los marcadores
                    // setTimeout(function () {
                    //     infoWindow.open({
                    //         anchor: marker,
                    //         map,
                    //     });
                    // }, 210);
                });
            }
        } catch (error) {
            hideLoader();
            Swal.fire(
                "¡Error!",
                `La búsqueda de nodos ha fallado: ${error}`,
                "error"
            );
        }
    } else {
        sweetAlert(
            "¡Error!",
            "El código de pintado debe ser de 7 dígitos numéricos",
            "error"
        );
    }
}

async function searchingByAddress(val_ads) {
    if (val_ads.trim() === "") {
        sweetAlert(
            "¡Advertencia!",
            `Por favor ingrese una dirección para continuar con la búsqueda`,
            "question"
        );
        return;
    }
    
    // Agrega "cali colombia" para asegurar que la búsqueda es dentro de
    let location = `${document.getElementById('pac-input').value} Cali Colombia`;

    geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: location }).then(async (result) => {
        const { results } = result;
        // Valida si la coordenada está dentro de los límites del mapa
        if (map_bounds.contains(results[0].geometry.location)) {
            try {
                showLoader();
                
                const response = await fetch(`${window.location.origin}/infrastructure/searchNodesInArea/?lat=${results[0].geometry.location.lat()}&lng=${results[0].geometry.location.lng()}`);
                const data = await response.text();
                
                hideLoader();
                
                nodeCircle.setMap(map);
                centerCircle.setMap(map);
                // Se eliminan todos los marcadores del mapa
                assignMarkers(markersArray, null);
                
                // Pasa la respuesta de string a json
                nodes = JSON.parse(data).features;

                // Ciclo para recorrer todos los resultados y pintarlos en el mapa
                nodes.forEach((node) => {
                    // Crea el marcador para el nodo
                    let node_marker = new google.maps.Marker({
                        position: {
                            lat: node.geometry.coordinates[1],
                            lng: node.geometry.coordinates[0],
                        },
                        map,
                        label: {
                            text: node.properties.painting_code.toString(),
                            color: "white",
                            fontSize: "10px",
                            fontWeight: "bold",
                            className: "node-painting-code",
                        },
                        title: "Marcador " + node.properties.painting_code,
                        icon: "/static/img/markers/node.png",
                    });
                    // Crea el infowindow asociado al marcador
                    let node_infowindow = new google.maps.InfoWindow({
                        content:
                        `<table class='table'>
                            <tr>
                                <td><b>Código del poste:</b></td>
                                <td> ${node.properties.painting_code}</td> 
                            </tr>
                            <tr>
                                <td><b>Zona:</b></td>
                                <td> ${node.properties.fk_comuna__name}</td> 
                            </tr>
                            <tr>
                                <td><b>Barrio:</b></td>
                                <td> ${node.properties.name}</td> 
                            </tr>
                        </table>
                        <div class="text-center">
                            <a id="selectNodeToReport" class='btn btn-outline-danger btn-sm' onclick='selectNode(${node.properties.pk}, ${node.properties.painting_code});'>Seleccionar poste</a>
                        </div>`,
                    });

                    // Agrega el listener al marcador para abrir el infowindow
                    node_marker.addListener("click", () => {
                        // Valida que sea el unico infowindow abierto
                        if (currentInfoWindow != null) {
                            // Cierra el infowindow abierto
                            currentInfoWindow.close();
                        }
                        // Abre el infowindow
                        node_infowindow.open({
                            anchor: node_marker,
                            map,
                        });
                        // Reasigna el infowindow
                        currentInfoWindow = node_infowindow;
                    });
                    
                    // Agrega el marcador al arreglo global de marcadores
                    markersArray.push(node_marker);
                    // Agrega el infowindow al arreglo global de infowindows
                    infowindowsArray.push(node_infowindow);
                });

                // Desplaza el mapa a la dirección georeferenciada
                map.panTo(results[0].geometry.location);
                map.setZoom(18);
                map.setCenter(results[0].geometry.location);

                // Mueve el centro del círculo a la nueva posición
                nodeCircle.setCenter(results[0].geometry.location);
                centerCircle.setCenter(results[0].geometry.location);
                
                // Cambia la dirección ingresada por la dirección formateada de la API
                document.getElementById('pac-input').value = results[0].formatted_address;
                
                setTimeout(() => {
                    const buscarBtn = document.getElementById('buscar');
                    if (buscarBtn) buscarBtn.focus();
                }, 0);
            } catch (error) {
                hideLoader();
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: `La solicitud de nodos ha fallado: ${error}`
                });
            }
        } else {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "La dirección está fuera del área de cobertura",
            });
        }
    })
    .catch((e) => {
        Swal.fire({
            icon: "warning",
            title: "Geocode tuvo problemas al buscar la dirección",
            text: e,
        });
    });
}

function selectNode(idNode, nodeCode) {
    Swal.fire({
        icon: "success",
        title: `Has seleccionado el poste ${nodeCode}`,
        showConfirmButton: false,
        timerProgressBar: true,
        timer: 1000,
    });
    // Guarda el id del nodo seleccionado en el sessionStorage
    window.sessionStorage.setItem("nodeToReport", idNode);
    document.getElementById('alert_node_reported').textContent = nodeCode;
    
    setTimeout(function () {
        nextStep();
    }, 950);
}

async function validateStep2ByNextBtn() {
    const nodeSelectedtoReport = window.sessionStorage.getItem("nodeToReport");

    return new Promise(async function (resolve, reject) {
        if (nodeSelectedtoReport !== null) {
            try {
                showLoader();
                
                const formData = new FormData();
                formData.append('value', nodeSelectedtoReport);
                
                const response = await fetch(`/pqr/api/validateNode/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: formData
                });
                
                const data = await response.json();
                hideLoader();
                
                if (data.type === 'success') {
                    resolve();
                } else {
                    reject(new Error(data.msg));
                }
            } catch (error) {
                hideLoader();
                reject(error);
            }
        } else {
            reject(new Error("No se seleccionó ningún poste para reportar."));
        }
    });
}

function cleanMarkers() {
    ArrayMarker.forEach((node) => {
        node.setMap(null);
    });
}

// Asigna todos los marcadores al mapa
function assignMarkers(markersArray, map) {
    markersArray.forEach((marker) => {
        marker.setMap(map);
    });
}

function resetPqrFields() {
    const typeDamage = document.getElementById('typeDamage');
    const origin = document.getElementById('origin');
    
    if (typeDamage) {
        typeDamage.innerHTML = '<option value=""></option>';
    }
    if (origin) {
        origin.innerHTML = '';
    }
}

// Inicializar el formulario cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeForm);
} else {
    initializeForm();
}

function initializeForm() {
    const form = document.getElementById('UserReportForm');
    if (form) {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            
            if (!genericValidationForm("UserReportForm")) {
                return;
            }

            const formData = new FormData(this);
            const nodeSelected = window.sessionStorage.getItem("nodeToReport");
            formData.append("idNode", nodeSelected);

            await creationPqr(formData);
        });
    }
}
