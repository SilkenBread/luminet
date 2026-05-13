/**
 * Módulo de visualización y gestión de Nodos.
 * Se inicializa al final del ciclo de carga de Google Maps via posMapsRender().
 */
(function () {
    "use strict";

    // ============================================================
    // Estado
    // ============================================================
    const state = {
        map: null,
        clusterer: null,
        markers: [],
        markersById: new Map(),  // pool de marcadores por id para diffs incrementales
        comunaPolygons: [],
        districtPolygons: [],
        comunasCache: null,
        infoWindow: null,
        creatingMarker: null,   // marcador temporal mientras se crea/edita
        formMode: "create",     // 'create' | 'edit'
        editingNodeId: null,
        editingMarker: null,
        dataTable: null,
        currentComunaId: null,
        currentDistrictId: null,
    };

    const COMUNAS_CACHE_KEY = "lm:comunas:v1";
    const COMUNAS_CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24h

    // Carga por viewport: por debajo de este zoom no pedimos nodos (el bbox es demasiado grande)
    const VIEWPORT_MIN_ZOOM = 14;
    const VIEWPORT_DEBOUNCE_MS = 350;
    let viewportTimer = null;
    let viewportRequestId = 0;

    // ============================================================
    // Helpers
    // ============================================================
    function getCookie(name) {
        const cookies = document.cookie ? document.cookie.split(";") : [];
        for (let c of cookies) {
            c = c.trim();
            if (c.startsWith(name + "=")) {
                return decodeURIComponent(c.substring(name.length + 1));
            }
        }
        return null;
    }

    function urlWith(template, key, value) {
        return template.replace("__" + key + "__", String(value));
    }

    function showError(msg) {
        Swal.fire({ title: "Error", text: msg, icon: "error", confirmButtonColor: "#3b82f6" });
    }

    function showSuccess(msg) {
        Swal.fire({ title: "¡Listo!", text: msg, icon: "success", confirmButtonColor: "#3b82f6", timer: 1800, showConfirmButton: false });
    }

    function postForm(url, data) {
        const body = new URLSearchParams(data);
        return fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken") || "",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            credentials: "same-origin",
            body,
        }).then((r) => r.json());
    }

    function getJson(url) {
        return fetch(url, {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            credentials: "same-origin",
        }).then((r) => r.json());
    }

    // ============================================================
    // Carga inicial (override del hook de google_maps.js)
    // ============================================================
    window.posMapsRender = async function () {
        state.map = window.map;
        state.infoWindow = new google.maps.InfoWindow();

        await loadComunas();
        drawComunaPolygons();
        populateComunaSelect();

        initClusterer();
        initFilters();
        initFormHandlers();
        initInfraPanelHandlers();
        initMapClick();
        initDataTable();
        initViewportLoader();
    };

    // ============================================================
    // Comunas (con caché en localStorage)
    // ============================================================
    async function loadComunas() {
        try {
            const raw = localStorage.getItem(COMUNAS_CACHE_KEY);
            if (raw) {
                const parsed = JSON.parse(raw);
                if (parsed && parsed.ts && (Date.now() - parsed.ts) < COMUNAS_CACHE_TTL_MS) {
                    state.comunasCache = parsed.data;
                    return;
                }
            }
        } catch (_) { /* corrupt cache → ignore */ }

        const data = await getJson(NODE_URLS.comunas);
        state.comunasCache = Array.isArray(data) ? data : [];
        try {
            localStorage.setItem(COMUNAS_CACHE_KEY, JSON.stringify({ ts: Date.now(), data: state.comunasCache }));
        } catch (_) { /* quota exceeded → ignore */ }
    }

    function drawComunaPolygons() {
        clearPolygons(state.comunaPolygons);
        state.comunaPolygons = [];

        (state.comunasCache || []).forEach((comuna) => {
            if (!comuna.polygon || !comuna.polygon.length) return;
            const poly = new google.maps.Polygon({
                paths: comuna.polygon,
                strokeColor: "#1d4ed8",
                strokeOpacity: 0.6,
                strokeWeight: 1,
                fillColor: "#3b82f6",
                fillOpacity: 0.05,
                map: state.map,
                clickable: false,
            });
            poly._meta = { id: comuna.pk, name: comuna.name };
            state.comunaPolygons.push(poly);
        });
    }

    function populateComunaSelect() {
        const $sel = $("#selectComuna");
        const ordered = (state.comunasCache || []).slice().sort((a, b) =>
            (a.name || "").localeCompare(b.name || "")
        );
        $sel.empty().append('<option value="">Todas las comunas</option>');
        ordered.forEach((c) => $sel.append(`<option value="${c.pk}">${c.name}</option>`));
        $sel.select2({ width: "100%", placeholder: "Todas las comunas" });
    }

    function clearPolygons(arr) {
        arr.forEach((p) => p.setMap(null));
    }

    // ============================================================
    // Distritos / Barrios
    // ============================================================
    async function loadDistrictsForComuna(comunaId) {
        const url = urlWith(NODE_URLS.districtsByComuna, "pk", comunaId);
        const data = await getJson(url);
        return Array.isArray(data) ? data : [];
    }

    function drawDistrictPolygons(districts) {
        clearPolygons(state.districtPolygons);
        state.districtPolygons = [];

        districts.forEach((d) => {
            (d.polygon || []).forEach((ring) => {
                const poly = new google.maps.Polygon({
                    paths: ring,
                    strokeColor: "#9333ea",
                    strokeOpacity: 0.8,
                    strokeWeight: 1.2,
                    fillColor: "#a78bfa",
                    fillOpacity: 0.08,
                    map: state.map,
                    clickable: false,
                });
                poly._meta = { id: d.pk, name: d.name };
                state.districtPolygons.push(poly);
            });
        });
    }

    function populateDistrictSelect(districts) {
        const $sel = $("#selectDistrict");
        $sel.empty().append('<option value="">Todos los barrios</option>');
        districts
            .slice()
            .sort((a, b) => (a.name || "").localeCompare(b.name || ""))
            .forEach((d) => $sel.append(`<option value="${d.pk}">${d.name}</option>`));
        $sel.prop("disabled", false).select2({ width: "100%", placeholder: "Todos los barrios" });
    }

    function fitMapToPolygons(polygons) {
        if (!polygons.length) return;
        const bounds = new google.maps.LatLngBounds();
        polygons.forEach((p) => p.getPath().forEach((latLng) => bounds.extend(latLng)));
        if (!bounds.isEmpty()) state.map.fitBounds(bounds);
    }

    // ============================================================
    // Marcadores + Cluster
    // ============================================================
    function initClusterer() {
        if (!window.markerClusterer) {
            console.warn("@googlemaps/markerclusterer no cargado");
            return;
        }
        state.clusterer = new markerClusterer.MarkerClusterer({
            map: state.map,
            markers: [],
        });
    }

    function clearAllMarkers() {
        if (state.clusterer) state.clusterer.clearMarkers();
        NodeMarkers.clearMarkers(state.markers);
        state.markers = [];
        state.markersById.clear();
    }

    /**
     * Render incremental: sólo crea marcadores nuevos y elimina los que ya no aplican.
     * Los marcadores que persisten entre dos llamadas no se tocan — esto es lo que
     * permite que pan/zoom sea fluido aunque haya miles de nodos en pantalla.
     */
    function renderNodes(nodes) {
        const incomingIds = new Set();
        const toAdd = [];

        for (const n of nodes) {
            if (n.lat == null || n.lng == null) continue;
            const id = n.pk != null ? n.pk : n.id;
            if (id == null) continue;
            incomingIds.add(id);
            if (state.markersById.has(id)) continue;

            const marker = NodeMarkers.createMarker({
                map: state.map,
                position: { lat: parseFloat(n.lat), lng: parseFloat(n.lng) },
                title: n.painting_code,
                node: n,
            });
            NodeMarkers.addClickListener(marker, () => openNodeInfoWindow(n, marker));
            state.markersById.set(id, marker);
            toAdd.push(marker);
        }

        const toRemove = [];
        for (const [id, marker] of state.markersById) {
            if (!incomingIds.has(id)) {
                toRemove.push(marker);
                state.markersById.delete(id);
            }
        }

        if (state.clusterer) {
            if (toRemove.length) state.clusterer.removeMarkers(toRemove);
            if (toAdd.length) state.clusterer.addMarkers(toAdd);
        }
        toRemove.forEach((m) => NodeMarkers.removeMarker(m));

        state.markers = Array.from(state.markersById.values());
    }

    // ============================================================
    // Carga por viewport (sin filtros activos)
    // ============================================================
    function hasActiveFilter() {
        return Boolean(state.currentComunaId || state.currentDistrictId);
    }

    function reloadDataTable() {
        if (state.dataTable) state.dataTable.ajax.reload(null, false);
    }

    function initViewportLoader() {
        state.map.addListener("idle", () => {
            if (viewportTimer) clearTimeout(viewportTimer);
            viewportTimer = setTimeout(loadNodesInViewport, VIEWPORT_DEBOUNCE_MS);
        });
    }

    async function loadNodesInViewport() {
        const filterActive = hasActiveFilter();

        // Sin filtro activo: exigir zoom mínimo para no traer toda la ciudad de golpe.
        // Con filtro: el bbox ya está acotado por la comuna/barrio, sin importar el zoom.
        if (!filterActive) {
            const zoom = state.map.getZoom();
            if (zoom == null || zoom < VIEWPORT_MIN_ZOOM) {
                clearAllMarkers();
                return;
            }
        }

        const bounds = state.map.getBounds();
        if (!bounds) return;

        const sw = bounds.getSouthWest();
        const ne = bounds.getNorthEast();
        const params = new URLSearchParams({
            west: sw.lng(),
            south: sw.lat(),
            east: ne.lng(),
            north: ne.lat(),
        });

        const requestId = ++viewportRequestId;
        try {
            const response = await getJson(NODE_URLS.byArea + "?" + params.toString());
            // Descartar respuestas obsoletas (el usuario siguió moviéndose)
            if (requestId !== viewportRequestId) return;

            if (response.type === "success") {
                renderNodes(response.data || []);
            }
        } catch (_) { /* errores transitorios de red → silenciar */ }
    }

    function openNodeInfoWindow(node, marker) {
        const html = `
            <div class="p-1 min-w-[180px]">
                <div class="text-xs text-gray-500">Nodo #${node.pk || node.id}</div>
                <div class="text-base font-semibold text-gray-900 mb-1">${node.painting_code || "—"}</div>
                <div class="text-xs text-gray-600 mb-2">
                    ${node.comuna || "—"} / ${node.district || "—"}
                </div>
                <div class="flex gap-1">
                    <button onclick="window.NodeApp.openInfraPanel(${node.pk || node.id})"
                            class="flex-1 px-2 py-1 text-xs bg-indigo-600 hover:bg-indigo-700 text-white rounded">
                        Ver infra
                    </button>
                    <button onclick="window.NodeApp.openEdit(${node.pk || node.id})"
                            class="flex-1 px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded">
                        Editar
                    </button>
                    <button onclick="window.NodeApp.confirmDelete(${node.pk || node.id})"
                            class="px-2 py-1 text-xs bg-red-600 hover:bg-red-700 text-white rounded">
                        ✕
                    </button>
                </div>
            </div>
        `;
        state.infoWindow.setContent(html);
        state.infoWindow.open({
            map: state.map,
            anchor: marker._isAdvanced ? marker : marker,
        });
    }

    // ============================================================
    // Filtros (Comuna / Barrio / Código pintado)
    // ============================================================
    function initFilters() {
        $("#selectComuna").on("change", async function () {
            const comunaId = $(this).val();
            state.currentComunaId = comunaId || null;
            state.currentDistrictId = null;
            $("#selectDistrict").val("").trigger("change.select2");

            if (!comunaId) {
                clearPolygons(state.districtPolygons);
                state.districtPolygons = [];
                $("#selectDistrict").empty()
                    .append('<option value="">Seleccione una comuna primero</option>')
                    .prop("disabled", true);
                clearAllMarkers();
                reloadDataTable();
                loadNodesInViewport();
                return;
            }

            const districts = await loadDistrictsForComuna(comunaId);
            drawDistrictPolygons(districts);
            populateDistrictSelect(districts);
            // fitBounds dispara 'idle' → el viewport-loader pinta los marcadores que entran en cuadro.
            fitMapToPolygons(state.districtPolygons);
            reloadDataTable();
        });

        $("#selectDistrict").on("change", function () {
            const districtId = $(this).val();
            state.currentDistrictId = districtId || null;
            if (!districtId) {
                reloadDataTable();
                return;
            }
            // Zoom al polígono del barrio → idle → viewport-loader pinta marcadores.
            const districtPolys = state.districtPolygons.filter(
                (p) => p._meta && p._meta.id === parseInt(districtId, 10)
            );
            if (districtPolys.length) fitMapToPolygons(districtPolys);
            reloadDataTable();
        });

        $("#btnSearchByCode").on("click", searchByPaintingCode);
        $("#inputPaintingCode").on("keypress", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                searchByPaintingCode();
            }
        });
        $("#btnClearFilters").on("click", clearAllFilters);
        $("#btnReloadData").on("click", () => state.dataTable && state.dataTable.ajax.reload(null, false));
    }

    async function searchByPaintingCode() {
        const code = $("#inputPaintingCode").val().trim();
        if (!/^\d{7}$/.test(code)) {
            showError("El código pintado debe tener 7 dígitos numéricos.");
            return;
        }
        const url = urlWith(NODE_URLS.byPaintingCode, "code", code);
        const response = await getJson(url);
        if (response.type === "success" && response.data.length) {
            renderNodes(response.data);
            const first = response.data[0];
            state.map.panTo({ lat: parseFloat(first.lat), lng: parseFloat(first.lng) });
            state.map.setZoom(18);
        } else {
            showError(response.msg || "No se encontraron nodos con ese código.");
            clearAllMarkers();
        }
    }

    function clearAllFilters() {
        state.currentComunaId = null;
        state.currentDistrictId = null;
        $("#selectComuna").val("").trigger("change.select2");
        $("#selectDistrict").empty()
            .append('<option value="">Seleccione una comuna primero</option>')
            .prop("disabled", true);
        $("#inputPaintingCode").val("");
        clearPolygons(state.districtPolygons);
        state.districtPolygons = [];
        clearAllMarkers();
        state.map.setCenter(CENTER);
        state.map.setZoom(12);
        reloadDataTable();
        // Tras el setZoom/setCenter, Google dispara 'idle' y se recarga por viewport
    }

    // ============================================================
    // Click en mapa → abrir modal de creación
    // ============================================================
    function initMapClick() {
        state.map.addListener("click", (e) => {
            const lat = e.latLng.lat();
            const lng = e.latLng.lng();
            openCreate({ lat, lng });
        });

        $("#btnOpenCreate").on("click", () => {
            Swal.fire({
                title: "Crear Nodo",
                text: "Haz click en el mapa para fijar la ubicación del nuevo nodo.",
                icon: "info",
                confirmButtonColor: "#3b82f6",
                timer: 2200,
            });
        });
    }

    // ============================================================
    // Modal: Crear / Editar
    // ============================================================
    function initFormHandlers() {
        $("#nodeFormSubmit").on("click", submitNodeForm);
    }

    function openCreate(coords) {
        state.formMode = "create";
        state.editingNodeId = null;
        clearCreatingMarker();

        $("#nodeFormTitle").text("Crear Nodo");
        $("#nodeFormSubmitText").text("Crear");
        $("#nodeForm_id").val("");
        $("#nodeForm_paintingCode").val("");
        $("#nodeForm_observation").val("");
        $("#nodeForm_locationInfo").addClass("hidden");
        setFormCoords(coords.lat, coords.lng);

        // Marcador temporal draggable en la posición clickeada
        state.creatingMarker = NodeMarkers.createMarker({
            map: state.map,
            position: coords,
            title: "Nuevo nodo",
            node: { painting_code: "+" },
            draggable: true,
        });
        if (!state.creatingMarker._isAdvanced) {
            state.creatingMarker.addListener("dragend", (e) => {
                setFormCoords(e.latLng.lat(), e.latLng.lng());
            });
        } else {
            state.creatingMarker.addListener("dragend", () => {
                const p = state.creatingMarker.position;
                setFormCoords(typeof p.lat === "function" ? p.lat() : p.lat,
                              typeof p.lng === "function" ? p.lng() : p.lng);
            });
        }

        openModal("nodeFormModal");
    }

    async function openEdit(nodeId) {
        state.formMode = "edit";
        state.editingNodeId = nodeId;
        clearCreatingMarker();

        const url = urlWith(NODE_URLS.detail, "pk", nodeId);
        const response = await getJson(url);
        if (response.type !== "success") {
            showError(response.msg || "No se pudo cargar el nodo.");
            return;
        }
        const node = response.data;

        $("#nodeFormTitle").text("Editar Nodo #" + nodeId);
        $("#nodeFormSubmitText").text("Guardar cambios");
        $("#nodeForm_id").val(nodeId);
        $("#nodeForm_paintingCode").val(node.painting_code || "");
        $("#nodeForm_observation").val(node.observation || "");
        setFormCoords(node.lat, node.lng);

        $("#nodeForm_comuna").text(node.comuna || "—");
        $("#nodeForm_district").text(node.fk_district || "—");
        $("#nodeForm_coords").text(`${node.lat.toFixed(6)}, ${node.lng.toFixed(6)}`);
        $("#nodeForm_locationInfo").removeClass("hidden");

        // Marker draggable para reubicar
        state.creatingMarker = NodeMarkers.createMarker({
            map: state.map,
            position: { lat: parseFloat(node.lat), lng: parseFloat(node.lng) },
            title: String(node.painting_code),
            node,
            draggable: true,
        });
        state.creatingMarker.addListener(state.creatingMarker._isAdvanced ? "dragend" : "dragend", function () {
            const p = state.creatingMarker._isAdvanced
                ? state.creatingMarker.position
                : state.creatingMarker.getPosition();
            const lat = typeof p.lat === "function" ? p.lat() : p.lat;
            const lng = typeof p.lng === "function" ? p.lng() : p.lng;
            setFormCoords(lat, lng);
        });

        state.map.panTo({ lat: parseFloat(node.lat), lng: parseFloat(node.lng) });
        openModal("nodeFormModal");
    }

    function clearCreatingMarker() {
        if (state.creatingMarker) {
            NodeMarkers.removeMarker(state.creatingMarker);
            state.creatingMarker = null;
        }
    }

    function setFormCoords(lat, lng) {
        $("#nodeForm_lat").val(lat);
        $("#nodeForm_lng").val(lng);
        $("#nodeForm_coordsStatus")
            .removeClass("bg-yellow-50 border-yellow-200 text-yellow-800")
            .addClass("bg-green-50 border-green-200 text-green-800");
        $("#nodeForm_coordsMsg").text(`Ubicación fijada: ${parseFloat(lat).toFixed(6)}, ${parseFloat(lng).toFixed(6)}`);
    }

    async function submitNodeForm() {
        const paintingCode = $("#nodeForm_paintingCode").val().trim();
        const observation = $("#nodeForm_observation").val().trim();
        const lat = $("#nodeForm_lat").val();
        const lng = $("#nodeForm_lng").val();

        if (!/^\d{7}$/.test(paintingCode)) {
            showError("El código pintado debe tener exactamente 7 dígitos.");
            return;
        }
        if (!lat || !lng) {
            showError("Debes fijar la ubicación en el mapa.");
            return;
        }

        const payload = { painting_code: paintingCode, observation, lat, lng };
        let url, isCreate = state.formMode === "create";
        url = isCreate ? NODE_URLS.create : urlWith(NODE_URLS.detail, "pk", state.editingNodeId);

        const $btn = $("#nodeFormSubmit").prop("disabled", true);
        const response = await postForm(url, payload);
        $btn.prop("disabled", false);

        if (response.type === "success") {
            closeModal("nodeFormModal");
            clearCreatingMarker();
            showSuccess(response.msg || (isCreate ? "Nodo creado." : "Nodo actualizado."));
            if (state.dataTable) state.dataTable.ajax.reload(null, false);
            // Reaplicar filtro vigente para refrescar los marcadores en el mapa
            reapplyCurrentFilter();
        } else {
            showError(response.msg || "Error al guardar el nodo.");
        }
    }

    function reapplyCurrentFilter() {
        if (state.currentDistrictId) {
            $("#selectDistrict").trigger("change");
        } else if (state.currentComunaId) {
            $("#selectComuna").trigger("change");
        } else {
            loadNodesInViewport();
        }
    }

    function confirmDelete(nodeId) {
        Swal.fire({
            title: "¿Eliminar nodo?",
            text: "Esta acción es permanente y no se puede deshacer.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#ef4444",
            cancelButtonColor: "#6b7280",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar",
            reverseButtons: true,
        }).then(async (result) => {
            if (!result.isConfirmed) return;
            const url = urlWith(NODE_URLS.delete, "pk", nodeId);
            const response = await postForm(url, {});
            if (response.type === "success") {
                showSuccess("Nodo eliminado.");
                state.infoWindow.close();
                if (state.dataTable) state.dataTable.ajax.reload(null, false);
                reapplyCurrentFilter();
            } else {
                showError(response.msg || "No se pudo eliminar el nodo.");
            }
        });
    }

    // ============================================================
    // Panel de infraestructura asociada
    // ============================================================
    function initInfraPanelHandlers() {
        $("#btnCloseInfraPanel, #btnCloseInfraPanel2").on("click", closeInfraPanel);
    }

    async function openInfraPanel(nodeId) {
        const $panel = $("#nodeInfraPanel");
        $panel.removeClass("hidden-panel");
        $("#nodeInfraPanel_nodeLabel").text("Nodo #" + nodeId);
        $("#nodeInfraPanel_loader").removeClass("hidden");
        $("#nodeInfraPanel_content").empty();
        $("#nodeInfraPanel_empty").addClass("hidden");

        const url = urlWith(NODE_URLS.infrastructure, "pk", nodeId);
        const response = await getJson(url);
        $("#nodeInfraPanel_loader").addClass("hidden");

        if (response.type !== "success") {
            showError(response.msg || "No se pudo cargar la infraestructura.");
            return;
        }
        renderInfraContent(response.data);
    }

    function closeInfraPanel() {
        $("#nodeInfraPanel").addClass("hidden-panel");
    }

    function renderInfraContent(data) {
        const $c = $("#nodeInfraPanel_content").empty();
        const sections = [
            { key: "trafo", title: "Transformadores", icon: "zap", color: "amber" },
            { key: "apbox", title: "Cajas AP", icon: "box", color: "sky" },
            { key: "luminaire", title: "Luminarias", icon: "lightbulb", color: "yellow" },
            { key: "support", title: "Apoyos", icon: "anchor", color: "stone" },
        ];

        let totalCount = 0;
        sections.forEach((sec) => {
            const items = data[sec.key] || [];
            totalCount += items.length;
            if (!items.length) return;

            const cards = items.map((it) => renderInfraCard(sec, it)).join("");
            $c.append(`
                <div>
                    <h4 class="text-xs font-bold uppercase text-gray-500 mb-2 flex items-center gap-2">
                        <i data-lucide="${sec.icon}" class="w-4 h-4 text-${sec.color}-500"></i>
                        ${sec.title} (${items.length})
                    </h4>
                    <div class="space-y-2">${cards}</div>
                </div>
            `);
        });

        if (totalCount === 0) {
            $("#nodeInfraPanel_empty").removeClass("hidden");
        }
        if (window.lucide) lucide.createIcons();
    }

    function renderInfraCard(sec, item) {
        const rows = Object.entries(item)
            .filter(([k, v]) => v != null && v !== "" && !["id"].includes(k) && typeof v !== "object")
            .slice(0, 6)
            .map(([k, v]) => `
                <div class="flex justify-between text-xs">
                    <span class="text-gray-500">${k}</span>
                    <span class="text-gray-800 font-medium text-right ml-2">${v}</span>
                </div>
            `).join("");
        return `
            <div class="border border-gray-200 rounded-lg p-3 bg-${sec.color}-50/40">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-semibold text-gray-800">#${item.id || "—"}</span>
                </div>
                <div class="space-y-0.5">${rows}</div>
            </div>
        `;
    }

    // ============================================================
    // DataTable server-side
    // ============================================================
    function initDataTable() {
        state.dataTable = $("#nodesTable").DataTable({
            processing: true,
            serverSide: true,
            deferLoading: 0,  // arranca vacía; no dispara request hasta que haya filtro
            ajax: {
                url: NODE_URLS.listData,
                type: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") || "" },
                data: function (d) {
                    if (state.currentDistrictId) d.district_id = state.currentDistrictId;
                    else if (state.currentComunaId) d.comuna_id = state.currentComunaId;
                },
            },
            columns: [
                { data: "id" },
                { data: "painting_code" },
                {
                    data: "district",
                    render: function (data, type, row) {
                        if (type !== "display") return data || "";
                        const com = row.comuna ? `<div class="text-xs text-gray-500">${row.comuna}</div>` : "";
                        return `<div>${com}<div>${data || "—"}</div></div>`;
                    },
                },
                {
                    data: "id",
                    orderable: false,
                    searchable: false,
                    className: "text-center",
                    render: function (data, type, row) {
                        if (type !== "display") return "";
                        return `
                            <div class="inline-flex gap-1">
                                <button class="p-1.5 text-green-600 hover:bg-green-50 rounded" title="Ubicar"
                                        onclick="window.NodeApp.centerOn(${row.id}, ${row.lat}, ${row.lng})">
                                    <i data-lucide="map-pin" class="w-4 h-4"></i>
                                </button>
                                <button class="p-1.5 text-indigo-600 hover:bg-indigo-50 rounded" title="Ver infra"
                                        onclick="window.NodeApp.openInfraPanel(${row.id})">
                                    <i data-lucide="layers" class="w-4 h-4"></i>
                                </button>
                                <button class="p-1.5 text-blue-600 hover:bg-blue-50 rounded" title="Editar"
                                        onclick="window.NodeApp.openEdit(${row.id})">
                                    <i data-lucide="pencil" class="w-4 h-4"></i>
                                </button>
                                <button class="p-1.5 text-red-600 hover:bg-red-50 rounded" title="Eliminar"
                                        onclick="window.NodeApp.confirmDelete(${row.id})">
                                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                                </button>
                            </div>
                        `;
                    },
                },
            ],
            order: [[0, "desc"]],
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-CO.json",
                emptyTable: "Selecciona una comuna o acerca el mapa para ver nodos.",
            },
            drawCallback: function () {
                if (window.lucide) lucide.createIcons();
                // Fallback: si la versión cargada de i18n sobreescribe emptyTable, lo forzamos
                // sólo cuando no hay filtro activo.
                if (!hasActiveFilter()) {
                    const $empty = $("#nodesTable tbody td.dataTables_empty");
                    if ($empty.length) {
                        $empty.text("Selecciona una comuna o acerca el mapa para ver nodos.");
                    }
                }
            },
        });
    }

    function centerOn(nodeId, lat, lng) {
        if (lat == null || lng == null) {
            showError("Este nodo no tiene coordenadas válidas.");
            return;
        }
        const position = { lat: parseFloat(lat), lng: parseFloat(lng) };
        state.map.panTo(position);
        state.map.setZoom(18);
        // Si ya hay marcador con ese id, abrir su info window
        const marker = state.markers.find((m) => m._node && (m._node.pk === nodeId || m._node.id === nodeId));
        if (marker) {
            openNodeInfoWindow(marker._node, marker);
        }
    }

    // ============================================================
    // API pública (usada desde renderizado dinámico)
    // ============================================================
    window.NodeApp = {
        openInfraPanel,
        openEdit,
        confirmDelete,
        centerOn,
    };
})();
