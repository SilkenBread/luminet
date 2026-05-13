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

    /**
     * Crea un marcador moderno (AdvancedMarkerElement) si está disponible y MAP_ID está configurado;
     * de lo contrario usa google.maps.Marker como fallback.
     */
    function createMarker({ map, position, title, node, draggable = false, useMapId = true }) {
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
                gmpDraggable: draggable,
            });
            m._isAdvanced = true;
            m._node = node;
            return m;
        }

        // Fallback clásico (sigue funcionando incluso sin MAP_ID)
        const m = new google.maps.Marker({
            map,
            position,
            title: String(title),
            draggable,
            label: node && node.painting_code ? { text: String(node.painting_code), fontSize: "10px" } : undefined,
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
