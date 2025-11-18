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

    // Set the initial theme based on the stored theme
    const theme = getStoredTheme();
    if (theme === 'dark') {
        setDarkMap();
    } else {
        setLightMap();
    }

    // Update the map theme when the theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        const storedTheme = getStoredTheme();
        if (storedTheme === 'dark') {
            setDarkMap();
        } else {
            setLightMap();
        }
    });

    posMapsRender();
    $('#loader').fadeOut();
    $("#overlay").fadeOut();
}

function setDarkMap() {
    map.setOptions({
        styles: [
            { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
            { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
            { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
            {
                featureType: "administrative.locality",
                elementType: "labels.text.fill",
                stylers: [{ color: "#d59563" }],
            },
            {
                featureType: "poi",
                elementType: "labels.text.fill",
                stylers: [{ color: "#d59563" }],
            },
            {
                featureType: "poi.park",
                elementType: "geometry",
                stylers: [{ color: "#263c3f" }],
            },
            {
                featureType: "poi.park",
                elementType: "labels.text.fill",
                stylers: [{ color: "#6b9a76" }],
            },
            {
                featureType: "road",
                elementType: "geometry",
                stylers: [{ color: "#38414e" }],
            },
            {
                featureType: "road",
                elementType: "geometry.stroke",
                stylers: [{ color: "#212a37" }],
            },
            {
                featureType: "road",
                elementType: "labels.text.fill",
                stylers: [{ color: "#9ca5b3" }],
            },
            {
                featureType: "road.highway",
                elementType: "geometry",
                stylers: [{ color: "#746855" }],
            },
            {
                featureType: "road.highway",
                elementType: "geometry.stroke",
                stylers: [{ color: "#1f2835" }],
            },
            {
                featureType: "road.highway",
                elementType: "labels.text.fill",
                stylers: [{ color: "#f3d19c" }],
            },
            {
                featureType: "transit",
                elementType: "geometry",
                stylers: [{ color: "#2f3948" }],
            },
            {
                featureType: "transit.station",
                elementType: "labels.text.fill",
                stylers: [{ color: "#d59563" }],
            },
            {
                featureType: "water",
                elementType: "geometry",
                stylers: [{ color: "#17263c" }],
            },
            {
                featureType: "water",
                elementType: "labels.text.fill",
                stylers: [{ color: "#515c6d" }],
            },
            {
                featureType: "water",
                elementType: "labels.text.stroke",
                stylers: [{ color: "#17263c" }],
            },
        ],
    });
}

function setLightMap() {
    map.setOptions({
        styles: [],
    });
}

// Define the setMapTheme function to update the map theme
function setMapTheme(theme) {
    if (theme === 'dark') {
        setDarkMap();
    } else {
        setLightMap();
    }
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
