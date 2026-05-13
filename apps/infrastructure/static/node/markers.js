/**
 * Utilidades para AdvancedMarkerElement con fallback a Marker clásico.
 * Expone window.NodeMarkers
 */
(function () {
    "use strict";

    function makePinContent(node) {
        const wrapper = document.createElement("div");
        wrapper.className = "lm-pin";
        wrapper.textContent = node.painting_code || "ND";
        return wrapper;
    }

    // Ícono ligero compartido entre todos los marcadores en modo "bulk".
    // Es una referencia única → Google Maps optimiza el render a canvas y evita un DOM por pin.
    let DOT_ICON = null;
    function getDotIcon() {
        if (DOT_ICON) return DOT_ICON;
        DOT_ICON = {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 5,
            fillColor: "#2563eb",
            fillOpacity: 0.95,
            strokeColor: "#ffffff",
            strokeWeight: 1.5,
        };
        return DOT_ICON;
    }

    /**
     * Crea un marcador.
     *
     * - draggable=true (crear/editar): usa AdvancedMarkerElement con pin visible cuando hay MAP_ID,
     *   o google.maps.Marker con label como fallback. Es un único marcador a la vez, su coste no importa.
     * - draggable=false (visualización masiva): siempre google.maps.Marker con un ícono SVG
     *   compartido. Esto permite renderizado optimizado en canvas y elimina el coste de DOM por pin,
     *   que es lo que hacía lenta la navegación cuando hay miles de nodos visibles.
     */
    function createMarker({ map, position, title, node, draggable = false, useMapId = true }) {
        if (draggable) {
            const canUseAdvanced =
                useMapId &&
                window.google &&
                google.maps &&
                google.maps.marker &&
                google.maps.marker.AdvancedMarkerElement &&
                typeof MAP_ID !== "undefined" &&
                MAP_ID;

            if (canUseAdvanced) {
                const m = new google.maps.marker.AdvancedMarkerElement({
                    map,
                    position,
                    title: String(title),
                    content: makePinContent(node || { painting_code: title }),
                    gmpDraggable: true,
                });
                m._isAdvanced = true;
                m._node = node;
                return m;
            }

            const m = new google.maps.Marker({
                map,
                position,
                title: String(title),
                draggable: true,
                label: node && node.painting_code
                    ? { text: String(node.painting_code), fontSize: "10px" }
                    : undefined,
            });
            m._isAdvanced = false;
            m._node = node;
            return m;
        }

        // Marker liviano para visualización masiva.
        const m = new google.maps.Marker({
            map,
            position,
            title: String(title || ""),
            icon: getDotIcon(),
            optimized: true,
        });
        m._isAdvanced = false;
        m._node = node;
        return m;
    }

    function removeMarker(marker) {
        if (!marker) return;
        if (marker._isAdvanced) marker.map = null;
        else marker.setMap(null);
    }

    function clearMarkers(markers) {
        markers.forEach(removeMarker);
        return [];
    }

    function setMarkerPosition(marker, position) {
        if (marker._isAdvanced) marker.position = position;
        else marker.setPosition(position);
    }

    function addClickListener(marker, handler) {
        if (marker._isAdvanced) {
            marker.addListener("gmp-click", handler);
        } else {
            marker.addListener("click", handler);
        }
    }

    window.NodeMarkers = {
        createMarker,
        removeMarker,
        clearMarkers,
        setMarkerPosition,
        addClickListener,
    };
})();
