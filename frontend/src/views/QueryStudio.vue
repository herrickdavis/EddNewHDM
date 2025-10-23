<template>
    <div class="container mt-4">
        <h2 class="mb-3 text-primary fw-bold">🧠 Editor Visual de Consultas</h2>

        <!-- Fuente de datos -->
        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Fuente de Datos</label>
            <select v-model="selectedDatasource" class="form-select">
                <option disabled value="">-- Selecciona una base de datos --</option>
                <option v-for="ds in datasources" :key="ds.id" :value="ds.id">
                    {{ ds.name }}
                </option>
            </select>
        </div>

        <!-- Nombre de la consulta -->
        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Nombre de la Consulta</label>
            <input v-model="queryName" type="text" class="form-control"
                placeholder="Ejemplo: Reporte general de laboratorio" />
        </div>

        <!-- Editor SQL -->
        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Consulta SQL</label>
            <textarea v-model="sqlText" class="form-control font-monospace" rows="6"
                placeholder="Escribe o pega tu consulta SQL aquí"></textarea>
        </div>

        <!-- Condicionales JSONLogic -->
        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Condiciones (JSONLogic)</label>
            <textarea v-model="rulesJson" class="form-control font-monospace" rows="3"
                placeholder='Ejemplo: {"==": [{"var":"FLATIVO"}, "S"]}'></textarea>
            <small class="text-muted">Define reglas lógicas opcionales. (FASE 6 lo hará visual)</small>
        </div>

        <!-- Botones -->
        <div class="d-flex justify-content-end gap-2 mb-4">
            <button class="btn btn-outline-secondary" @click="probarConsulta">▶ Ejecutar</button>
            <button class="btn btn-success" @click="guardarConsulta">💾 Guardar</button>
        </div>

        <!-- Resultados -->
        <div v-if="result && result.rows && result.rows.length" class="card shadow-sm">
            <div class="card-header bg-light fw-bold">📊 Resultado</div>
            <div class="table-responsive">
                <table class="table table-striped table-bordered mb-0">
                    <thead>
                        <tr>
                            <th v-for="col in result.columns" :key="col">{{ col }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(row, i) in paginatedRows" :key="i">
                            <td v-for="col in result.columns" :key="col">{{ row[col] }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Paginación -->
            <div class="d-flex justify-content-between align-items-center p-3">
                <button class="btn btn-outline-secondary" @click="prevPage" :disabled="currentPage === 1">
                    ◀ Anterior
                </button>
                <span>Página {{ currentPage }} de {{ totalPages }}</span>
                <button class="btn btn-outline-secondary" @click="nextPage" :disabled="currentPage === totalPages">
                    Siguiente ▶
                </button>
            </div>
        </div>

        <div v-else-if="result && result.error" class="alert alert-danger mt-3">
            ❌ {{ result.error }}
        </div>

        <div v-else class="text-muted text-center mt-3">
            <em>No hay resultados aún</em>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useEddStore } from "../store/index.js";
import api from "../api/eddApi";

const store = useEddStore();
const datasources = ref([]);
const selectedDatasource = ref("");
const queryName = ref("");
const sqlText = ref("");
const rulesJson = ref("");
const result = ref(null);

const currentPage = ref(1);
const itemsPerPage = 10;

const paginatedRows = computed(() => {
    if (!result.value?.rows) return [];
    const start = (currentPage.value - 1) * itemsPerPage;
    return result.value.rows.slice(start, start + itemsPerPage);
});

const totalPages = computed(() => {
    if (!result.value?.rows) return 1;
    return Math.ceil(result.value.rows.length / itemsPerPage);
});

const nextPage = () => {
    if (currentPage.value < totalPages.value) currentPage.value++;
};
const prevPage = () => {
    if (currentPage.value > 1) currentPage.value--;
};

// Cargar datasources
onMounted(async () => {
    await store.loadDatasources();
    datasources.value = store.datasources;
});

// Ejecutar temporalmente
async function probarConsulta() {
    if (!sqlText.value.trim()) {
        alert("Debes ingresar una consulta SQL válida.");
        return;
    }

    try {
        const tempQuery = {
            datasource_id: selectedDatasource.value,
            name: queryName.value || "Consulta temporal",
            sql_text: sqlText.value,
            params_json: {},
            schema_json: {},
            active: true,
        };

        const { data } = await api.post("/queries", tempQuery);
        const run = await api.post(`/queries/run/${data.id}`);
        result.value = run.data;
        currentPage.value = 1;
    } catch (err) {
        result.value = { error: err.message };
    }
}

// Validar reglas antes de guardar
function validarReglas() {
    if (!rulesJson.value.trim()) return true;
    try {
        const parsed = JSON.parse(rulesJson.value);
        if (typeof parsed !== "object" || Array.isArray(parsed)) throw new Error();
        return true;
    } catch {
        alert("Reglas inválidas. Ejemplo correcto: {\"==\": [{\"var\":\"FLATIVO\"}, \"S\"]}");
        return false;
    }
}

// Guardar consulta
async function guardarConsulta() {
    if (!selectedDatasource.value) {
        alert("Selecciona una fuente de datos antes de guardar.");
        return;
    }
    if (!queryName.value.trim() || !sqlText.value.trim()) {
        alert("Completa el nombre y la consulta SQL.");
        return;
    }
    if (!validarReglas()) return;

    let rules = null;
    if (rulesJson.value.trim()) {
        try {
            rules = JSON.parse(rulesJson.value);
        } catch {
            rules = null;
        }
    }

    const newQuery = {
        datasource_id: selectedDatasource.value,
        name: queryName.value,
        sql_text: sqlText.value,
        params_json: {},
        schema_json: {},
        rules_json: rules,
        active: true,
    };

    try {
        await api.post("/queries", newQuery);
        alert("✅ Consulta guardada correctamente con reglas JSONLogic.");
    } catch (error) {
        alert("Error al guardar la consulta: " + error.message);
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

<!--
<template>
    <div class="container mt-4">
        <h2 class="mb-3 text-primary fw-bold">🧠 Editor Visual de Consultas</h2>

        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Fuente de Datos</label>
            <select v-model="selectedDatasource" class="form-select">
                <option disabled value="">-- Selecciona una base de datos --</option>
                <option v-for="ds in datasources" :key="ds.id" :value="ds.id">{{ ds.name }}</option>
            </select>
        </div>

        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Nombre de la Consulta</label>
            <input v-model="queryName" type="text" class="form-control"
                placeholder="Ejemplo: Reporte general de laboratorio" />
        </div>

        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Consulta SQL</label>
            <textarea v-model="sqlText" class="form-control font-monospace" rows="6"
                placeholder="Escribe o pega tu consulta SQL aquí"></textarea>
        </div>

        <div class="card p-3 mb-3 shadow-sm">
            <label class="form-label fw-bold">Condiciones (JSONLogic)</label>
            <textarea v-model="rulesJson" class="form-control font-monospace" rows="3"
                placeholder='Ejemplo: {"==": [{"var":"FLATIVO"}, "S"]}'></textarea>
            <small class="text-muted">Define reglas lógicas opcionales. (FASE 6 lo hará visual)</small>
        </div>

        <div class="d-flex justify-content-end gap-2 mb-4">
            <button class="btn btn-outline-secondary" @click="probarConsulta">▶ Ejecutar</button>
            <button class="btn btn-success" @click="guardarConsulta">💾 Guardar</button>
        </div>

        <div v-if="result && result.rows && result.rows.length" class="card shadow-sm">
            <div class="card-header bg-light fw-bold">📊 Resultado</div>
            <div class="table-responsive">
                <table class="table table-striped table-bordered mb-0">
                    <thead>
                        <tr>
                            <th v-for="col in result.columns" :key="col">{{ col }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(row, i) in paginatedRows" :key="i">
                            <td v-for="col in result.columns" :key="col">{{ row[col] }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="d-flex justify-content-between align-items-center p-3">
                <button class="btn btn-outline-secondary" @click="prevPage" :disabled="currentPage === 1">
                    ◀ Anterior
                </button>
                <span>Página {{ currentPage }} de {{ totalPages }}</span>
                <button class="btn btn-outline-secondary" @click="nextPage" :disabled="currentPage === totalPages">
                    Siguiente ▶
                </button>
            </div>
        </div>

        <div v-else-if="result && result.error" class="alert alert-danger mt-3">
            ❌ {{ result.error }}
        </div>

        <div v-else class="text-muted text-center mt-3">
            <em>No hay resultados aún</em>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useEddStore } from "../store/index.js";
import api from "../api/eddApi";

const store = useEddStore();
const datasources = ref([]);
const selectedDatasource = ref("");
const queryName = ref("");
const sqlText = ref("");
const rulesJson = ref("");
const result = ref(null);

const currentPage = ref(1);
const itemsPerPage = 10;

const paginatedRows = computed(() => {
    if (!result.value?.rows) return [];
    const start = (currentPage.value - 1) * itemsPerPage;
    return result.value.rows.slice(start, start + itemsPerPage);
});

const totalPages = computed(() => {
    if (!result.value?.rows) return 1;
    return Math.ceil(result.value.rows.length / itemsPerPage);
});

const nextPage = () => {
    if (currentPage.value < totalPages.value) currentPage.value++;
};
const prevPage = () => {
    if (currentPage.value > 1) currentPage.value--;
};

// Cargar datasources
onMounted(async () => {
    await store.loadDatasources();
    datasources.value = store.datasources;
});

// Guardar consulta con JSONLogic
async function guardarConsulta() {
    if (!selectedDatasource.value) {
        alert("Selecciona una fuente de datos antes de guardar.");
        return;
    }
    if (!queryName.value.trim() || !sqlText.value.trim()) {
        alert("Completa el nombre y la consulta SQL.");
        return;
    }

    let rules = {};
    try {
        if (rulesJson.value.trim()) {
            rules = JSON.parse(rulesJson.value);
        }
    } catch (e) {
        alert("⚠️ JSON inválido en las reglas. Corrige el formato.");
        return;
    }

    const newQuery = {
        datasource_id: selectedDatasource.value,
        name: queryName.value,
        sql_text: sqlText.value,
        params_json: {},
        schema_json: {},
        rules_json: rules,
        active: true,
    };

    try {
        await api.post("/queries", newQuery);
        alert("✅ Consulta guardada correctamente con reglas JSONLogic.");
    } catch (error) {
        alert("Error al guardar la consulta: " + error.message);
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
-->