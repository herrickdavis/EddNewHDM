<template>
    <div class="container mt-4">
        <h2 class="mb-3 text-primary fw-bold">🧩 Diseñador de Plantillas</h2>

        <!-- Nombre -->
        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Nombre de la Plantilla</label>
            <input v-model="name" type="text" class="form-control" placeholder="Ej: Reporte General" />
        </div>

        <!-- Descripción -->
        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Descripción</label>
            <textarea v-model="description" class="form-control" rows="2"></textarea>
        </div>

        <!-- Consulta asociada -->
        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Consulta Asociada</label>
            <select v-model="queryId" class="form-select">
                <option disabled value="">-- Selecciona una consulta existente --</option>
                <option v-for="q in queries" :key="q.id" :value="q.id">
                    {{ q.name }}
                </option>
            </select>
        </div>

        <!-- Modo -->
        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Modo de Diseño</label>
            <select v-model="mode" class="form-select">
                <option value="horizontal">Horizontal (filas → columnas)</option>
                <option value="vertical">Vertical (registros como tarjetas)</option>
            </select>
        </div>

        <!-- Layout JSON -->
        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Layout JSON</label>
            <textarea v-model="layoutJson" class="form-control font-monospace" rows="6"
                placeholder='Ejemplo: {"columns":["CDAMOSTRA","FLATIVO","DTCRIACAO","DTEDICAO","NMUSUARIO"]}'></textarea>
            <small class="text-muted">Define columnas visibles y orden.</small>
        </div>

        <!-- (Opcional) Reglas JSONLogic propias de la plantilla -->
        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Reglas (JSONLogic) de la Plantilla</label>
            <textarea v-model="rulesJson" class="form-control font-monospace" rows="3"
                placeholder='Ej.: {"==": [{"var":"FLATIVO"}, "S"]}'></textarea>
            <small class="text-muted">Si las defines aquí, la Vista Previa también filtrará registros.</small>
        </div>

        <!-- Acciones -->
        <div class="d-flex justify-content-end gap-2 mb-4">
            <button class="btn btn-outline-secondary" @click="previewTemplate">👁 Vista Previa</button>
            <div class="btn-group">
                <button class="btn btn-outline-success dropdown-toggle" data-bs-toggle="dropdown">⬇ Exportar</button>
                <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#" @click.prevent="exportar('xlsx')">XLSX (filtrado)</a></li>
                    <li><a class="dropdown-item" href="#" @click.prevent="exportar('csv')">CSV (filtrado)</a></li>
                    <li><a class="dropdown-item" href="#" @click.prevent="exportar('txt')">TXT (filtrado)</a></li>
                </ul>
            </div>
            <button class="btn btn-success" @click="saveTemplate">💾 Guardar Plantilla</button>
        </div>

        <!-- Vista previa -->
        <div v-if="previewData" class="card shadow-sm">
            <div class="card-header bg-light fw-bold">👁 Vista Previa ({{ mode }})</div>

            <!-- Horizontal: tabla -->
            <div v-if="mode === 'horizontal'" class="table-responsive">
                <table class="table table-striped table-bordered mb-0">
                    <thead>
                        <tr>
                            <th v-for="col in previewColumns" :key="col">{{ col }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(row, i) in paginatedRows" :key="i">
                            <td v-for="col in previewColumns" :key="col">{{ formatValue(row[col]) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Vertical: tarjetas -->
            <div v-else class="p-3">
                <div v-for="(row, i) in paginatedRows" :key="i" class="card mb-2 shadow-sm">
                    <div class="card-body">
                        <div class="row">
                            <div v-for="col in previewColumns" :key="col" class="col-md-4 mb-2">
                                <div class="small text-muted">{{ col }}</div>
                                <div class="fw-semibold">{{ formatValue(row[col]) }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Paginación -->
            <div class="d-flex justify-content-between align-items-center p-3">
                <button class="btn btn-outline-secondary" @click="prevPage" :disabled="currentPage === 1">◀
                    Anterior</button>
                <span>Página {{ currentPage }} de {{ totalPages }}</span>
                <button class="btn btn-outline-secondary" @click="nextPage"
                    :disabled="currentPage === totalPages">Siguiente ▶</button>
            </div>
        </div>

        <div v-else class="text-muted text-center mt-3">
            <em>No hay vista previa aún</em>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import api from "../api/eddApi";

const queries = ref([]);
const name = ref("");
const description = ref("");
const mode = ref("horizontal");
const queryId = ref("");
const layoutJson = ref("");
const rulesJson = ref(""); // reglas propias de la plantilla (opcional)
const previewData = ref(null);
const previewColumns = ref([]);

// paginación
const currentPage = ref(1);
const itemsPerPage = 10;
const paginatedRows = computed(() => {
    if (!previewData.value?.rows) return [];
    const start = (currentPage.value - 1) * itemsPerPage;
    return previewData.value.rows.slice(start, start + itemsPerPage);
});
const totalPages = computed(() => {
    if (!previewData.value?.rows) return 1;
    return Math.ceil(previewData.value.rows.length / itemsPerPage);
});
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };

onMounted(async () => {
    const { data } = await api.get("/queries");
    queries.value = data;
});

function formatValue(v) {
    if (v === null || v === undefined) return "";
    // formateo simple de fechas ISO
    if (typeof v === "string" && /^\d{4}-\d{2}-\d{2}T/.test(v)) {
        return v.replace("T", " ").slice(0, 19);
    }
    return v;
}

async function saveTemplate() {
    if (!name.value.trim() || !queryId.value) {
        alert("Debes ingresar un nombre y seleccionar una consulta.");
        return;
    }

    let parsedLayout = {};
    let parsedRules = {};
    try {
        parsedLayout = layoutJson.value ? JSON.parse(layoutJson.value) : {};
    } catch (e) {
        alert("Layout JSON inválido.");
        return;
    }
    try {
        parsedRules = rulesJson.value ? JSON.parse(rulesJson.value) : {};
    } catch (e) {
        alert("Reglas JSONLogic inválidas.");
        return;
    }

    const newTpl = {
        name: name.value,
        description: description.value,
        mode: mode.value,
        query_id: queryId.value,
        layout_json: parsedLayout,
        filters_json: {},
        rules_json: parsedRules,
        active: true,
    };

    try {
        await api.post("/templates", newTpl);
        alert("✅ Plantilla guardada correctamente.");
    } catch (error) {
        alert("Error al guardar plantilla: " + error.message);
    }
}

async function previewTemplate() {
    if (!queryId.value) {
        alert("Selecciona una consulta asociada primero.");
        return;
    }
    // Nota: preview se hace por ID de plantilla, así que si es nueva y no está guardada,
    // guarda primero la plantilla para obtener el ID.
    // Para una prueba rápida: guarda, anota el ID y vuelve a abrir para vista previa.
    const templateId = await ensureTemplateIdForPreview();
    if (!templateId) return;

    const { data } = await api.get(`/templates/${templateId}/preview`);
    previewData.value = data.data;
    previewColumns.value = data.data.columns || [];
    currentPage.value = 1;
    // Actualiza el modo desde lo guardado (por si cambió)
    mode.value = data.template.mode || mode.value;
}

// si aún no existe, guarda una plantilla “temporal” para generar ID
async function ensureTemplateIdForPreview() {
    // Estrategia simple: si no está guardada, guardamos ahora
    // (En una app real: separar "crear" y "actualizar" y guardar el ID en el estado).
    if (!name.value.trim() || !queryId.value) {
        alert("Para la vista previa, guarda primero: nombre + consulta + layout.");
        return null;
    }
    let parsedLayout = {};
    let parsedRules = {};
    try { parsedLayout = layoutJson.value ? JSON.parse(layoutJson.value) : {}; } catch { parsedLayout = {}; }
    try { parsedRules = rulesJson.value ? JSON.parse(rulesJson.value) : {}; } catch { parsedRules = {}; }

    // Crear siempre una nueva “temporal” (simple)
    const newTpl = {
        name: name.value,
        description: description.value,
        mode: mode.value,
        query_id: queryId.value,
        layout_json: parsedLayout,
        filters_json: {},
        rules_json: parsedRules,
        active: true,
    };
    const res = await api.post("/templates", newTpl);
    return res.data.id;
}

async function exportar(format) {
    if (!queryId.value) {
        alert("Selecciona una consulta asociada primero.");
        return;
    }
    try {
        const url = `/queries/run/${queryId.value}/export_filtered?format=${format}`;
        const resp = await api.post(url, {}, { responseType: "blob" });
        const blob = new Blob([resp.data]);
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `resultado_filtrado.${format}`;
        a.click();
    } catch (e) {
        alert("Error exportando: " + (e?.message || e));
    }
}
</script>

<style>
.container {
    max-width: 1000px;
}

.font-monospace {
    font-family: monospace;
}
</style>
