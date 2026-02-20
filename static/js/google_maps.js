const CENTER = { lat: 3.413568, lng: -76.519832 }; // Ajusta las coordenadas según tus necesidades

async function initMap() {
    map_bounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(3.273336759797639, -76.70717563811434),
        new google.maps.LatLng(3.5485267251372963, -76.45883778721213)
    );

    map = new google.maps.Map(document.getElementById("map"), {
        center: CENTER,
        zoom: 12,
        clickableIcons: false,
        restriction: {
            latLngBounds: map_bounds,
        },
    });

    // Validar si es movil o no para configurar los gestos de zoom de Google Maps.
    var isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent);

    if (!isMobile) {
        map.setOptions({ gestureHandling: "greedy" });
    }

    posMapsRender();
    $('#loader').fadeOut();
    $("#overlay").fadeOut();
}

function setLightMap() {
    map.setOptions({
        styles: [],
    });
}

// Funcion para obtener el centro de un poligono
function getCenter(polygon) {
    let bounds = new google.maps.LatLngBounds();

    polygon.getPath().forEach(function (item) {
        bounds.extend(item);
    });
    return bounds.getCenter();
}

// Retorna formato de mensaje de error para sweetAlert
function errorMessage(error_title, error_obj) {
    return {
        title: error_title,
        icon: "error",
        html: `
            <div style="text-align: left; display: inline-block">
            <br>
        &nbsp;&nbsp;&nbsp;&nbsp;http_code: ${error_obj.status},<br>
        &nbsp;&nbsp;&nbsp;&nbsp;http_text: ${error_obj.statusText}<br>
        }
        </div>
        `,
        focusConfirm: true,
    };
}

// Ordena el arreglo en orden alfabético
function orderArrayByString(arreglo) {
    let nuevo_arreglo = Array.from(arreglo).filter((item) => item != undefined);

    nuevo_arreglo.sort(function (a, b) {
        const nameA = a.name.toUpperCase(); // ignore upper and lowercase
        const nameB = b.name.toUpperCase(); // ignore upper and lowercase

        if (nameA > nameB) {
            return 1;
        }
        if (nameA < nameB) {
            return -1;
        }
        // names must be equal
        return 0;
    });
    return nuevo_arreglo;
}

// Limpia un arreglo de polígonos del mapa
function cleanZoneFromMap(zonas) {
    zonas.forEach((poligono) => poligono.setMap(null));
}
