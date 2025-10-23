<template>
    <div class="container mt-4">
        <h2 class="mb-3 text-primary fw-bold">🧩 Diseñador de Plantillas</h2>

        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Nombre de la Plantilla</label>
            <input v-model="name" type="text" class="form-control" placeholder="Ej: Reporte General" />
        </div>

        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Descripción</label>
            <textarea v-model="description" class="form-control" rows="2"></textarea>
        </div>

        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Consulta Asociada</label>
            <select v-model="queryId" class="form-select">
                <option disabled value="">-- Selecciona una consulta existente --</option>
                <option v-for="q in queries" :key="q.id" :value="q.id">
                    {{ q.name }}
                </option>
            </select>
        </div>

        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Modo de Diseño</label>
            <select v-model="mode" class="form-select">
                <option value="horizontal">Horizontal (filas → columnas)</option>
                <option value="vertical">Vertical (columnas → secciones)</option>
            </select>
        </div>

        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Layout JSON</label>
            <textarea v-model="layoutJson" class="form-control font-monospace" rows="6"
                placeholder='Ejemplo: {"columns":["CDAMOSTRA","FLATIVO","DTEDICAO"]}'></textarea>
            <small class="text-muted">Aquí se define qué campos se mostrarán y su orden.</small>
        </div>

        <div class="d-flex justify-content-end gap-2 mb-4">
            <button class="btn btn-outline-secondary" @click="previewTemplate">👁 Vista Previa</button>
            <button class="btn btn-success" @click="saveTemplate">💾 Guardar Plantilla</button>
        </div>

        <!-- Vista previa -->
        <div v-if="previewData" class="card shadow-sm">
            <div class="card-header bg-light fw-bold">👁 Vista Previa</div>
            <div class="table-responsive">
                <table class="table table-bordered table-sm">
                    <thead>
                        <tr>
                            <th v-for="col in previewData.columns" :key="col">{{ col }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(row, i) in previewData.rows" :key="i">
                            <td v-for="col in previewData.columns" :key="col">{{ row[col] }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/eddApi";

const queries = ref([]);
const name = ref("");
const description = ref("");
const mode = ref("horizontal");
const queryId = ref("");
const layoutJson = ref("");
const previewData = ref(null);
const savedTemplate = ref(null); // ✅ guarda el último template creado

onMounted(async () => {
    const { data } = await api.get("/queries");
    queries.value = data;
});

async function saveTemplate() {
    if (!name.value.trim() || !queryId.value) {
        alert("Debes ingresar un nombre y seleccionar una consulta.");
        return;
    }

    const newTpl = {
        name: name.value,
        description: description.value,
        mode: mode.value,
        query_id: queryId.value,
        layout_json: JSON.parse(layoutJson.value || "{}"),
        filters_json: {},
        rules_json: {},
        active: true,
    };

    try {
        const { data } = await api.post("/templates", newTpl);
        savedTemplate.value = data; // ✅ guardamos la plantilla recién creada
        alert(`✅ Plantilla guardada correctamente (ID: ${data.id})`);
    } catch (error) {
        alert("Error al guardar plantilla: " + error.message);
    }
}

async function previewTemplate() {
    if (!savedTemplate.value) {
        alert("⚠️ Primero guarda la plantilla para generar vista previa.");
        return;
    }

    try {
        const id = savedTemplate.value.id; // ✅ usa el id real del template
        const { data } = await api.get(`/templates/${id}/preview`);
        previewData.value = data.data;
    } catch (error) {
        alert("Error al generar vista previa: " + error.message);
    }
}
</script>

<style>
.container {
    max-width: 900px;
}

.font-monospace {
    font-family: monospace;
}
</style>
