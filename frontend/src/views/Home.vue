<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import jsonLogic from "json-logic-js";

const queries = ref([]);
const selectedQuery = ref(null);

// Resultado crudo del backend
const resultados = ref(null);

// Resultado después de reglas (filtrado/resaltado)
const rowsFiltradas = ref([]);

// Modo de aplicación: "highlight" (solo resalta) | "filter" (filtra)
const applyMode = ref("highlight");

// Paginación
const currentPage = ref(1);
const itemsPerPage = 10;

// Reglas de la consulta actual
const activeRule = ref(null);

// Cargar consultas
const cargarConsultas = async () => {
    const { data } = await axios.get("http://127.0.0.1:8000/api/queries");
    queries.value = data;
};

// Ejecutar consulta y aplicar reglas si existen
const ejecutarConsulta = async () => {
    if (!selectedQuery.value) {
        alert("Seleccione una consulta primero");
        return;
    }

    try {
        // Trae resultado SQL
        const res = await axios.post(
            `http://127.0.0.1:8000/api/queries/run/${selectedQuery.value}`,
            {}
        );
        resultados.value = res.data || { columns: [], rows: [] };

        // Obtén regla de la consulta seleccionada
        // Opción A) si implementaste GET /api/queries/{id} usa esa:
        // const { data: q } = await axios.get(`http://127.0.0.1:8000/api/queries/${selectedQuery.value}`);

        // Opción B) si NO implementaste el GET por id, búscala en la lista:
        const q = queries.value.find(q => q.id === selectedQuery.value);

        activeRule.value = q?.rules_json || null;

        // Aplica reglas
        aplicarReglas();

        // Reinicia paginación
        currentPage.value = 1;
    } catch (error) {
        console.error("Error ejecutando consulta:", error);
        alert("Error ejecutando la consulta. Ver consola.");
    }
};

// Aplica reglas sobre resultados.value.rows → rowsFiltradas
const aplicarReglas = () => {
    const rows = resultados.value?.rows || [];
    if (!activeRule.value) {
        rowsFiltradas.value = rows.map(r => ({ __match: true, ...r }));
        return;
    }

    // Si viene como string, parsea
    let rule = activeRule.value;
    if (typeof rule === "string") {
        try { rule = JSON.parse(rule); } catch { rule = null; }
    }

    if (!rule || typeof rule !== "object") {
        rowsFiltradas.value = rows.map(r => ({ __match: true, ...r }));
        return;
    }

    // Evalúa cada fila
    const evaluadas = rows.map(r => {
        let ok = false;
        try {
            ok = !!jsonLogic.apply(rule, r);
        } catch {
            ok = false;
        }
        return { __match: ok, ...r };
    });

    // Según modo
    if (applyMode.value === "filter") {
        rowsFiltradas.value = evaluadas.filter(r => r.__match);
    } else {
        rowsFiltradas.value = evaluadas;
    }
};

// Watch manual del modo
const cambiarModo = (modo) => {
    applyMode.value = modo;
    aplicarReglas();
};

// Paginación computada
const paginatedRows = computed(() => {
    const list = rowsFiltradas.value || [];
    const start = (currentPage.value - 1) * itemsPerPage;
    return list.slice(start, start + itemsPerPage);
});

const totalPages = computed(() => {
    const list = rowsFiltradas.value || [];
    return Math.max(1, Math.ceil(list.length / itemsPerPage));
});

const nextPage = () => {
    if (currentPage.value < totalPages.value) currentPage.value++;
};

const prevPage = () => {
    if (currentPage.value > 1) currentPage.value--;
};

// Exportar (exporta el resultado crudo del backend)
const exportar = async (format) => {
    if (!selectedQuery.value) {
        alert("Seleccione una consulta primero");
        return;
    }

    try {
        const url = `http://127.0.0.1:8000/api/queries/run/${selectedQuery.value}/export?format=${format}`;
        const response = await fetch(url, { method: "POST" });
        if (!response.ok) throw new Error(`Error al exportar: ${response.status}`);

        const blob = await response.blob();
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `resultado.${format}`;
        link.click();
    } catch (error) {
        console.error("Error en exportar:", error);
        alert("Ocurrió un error al exportar el archivo");
    }
};

onMounted(() => {
    cargarConsultas();
});
</script>

<template>
    <div class="container mt-4">
        <h3>📊 EDD – Ejecución de Consultas con Condicionales</h3>

        <div class="mb-3">
            <label class="form-label">Seleccionar Consulta:</label>
            <select v-model="selectedQuery" class="form-select">
                <option disabled value="">-- Seleccione --</option>
                <option v-for="q in queries" :key="q.id" :value="q.id">
                    {{ q.name }}
                </option>
            </select>
        </div>

        <div class="d-flex gap-2 mb-2">
            <button class="btn btn-primary" @click="ejecutarConsulta">Ejecutar</button>

            <!-- Modo de aplicación visual -->
            <div class="btn-group ms-auto">
                <button class="btn"
                    :class="applyMode === 'highlight' ? 'btn-outline-success active' : 'btn-outline-success'"
                    @click="cambiarModo('highlight')" title="Solo resaltar filas que cumplen la regla">
                    🖍 Resaltar
                </button>
                <button class="btn"
                    :class="applyMode === 'filter' ? 'btn-outline-primary active' : 'btn-outline-primary'"
                    @click="cambiarModo('filter')" title="Mostrar únicamente filas que cumplen la regla">
                    🔎 Filtrar
                </button>
            </div>
        </div>

        <!-- Vista de la regla activa -->
        <div v-if="activeRule" class="alert alert-info py-2 small">
            <strong>Regla activa:</strong>
            <code class="ms-1">{{ typeof activeRule === 'string' ? activeRule : JSON.stringify(activeRule) }}</code>
        </div>

        <div v-if="resultados && resultados.rows && resultados.rows.length" class="mt-3">
            <div class="table-responsive">
                <table class="table table-bordered table-sm">
                    <thead class="table-light">
                        <tr>
                            <th v-for="col in resultados.columns" :key="col">{{ col }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(fila, i) in paginatedRows" :key="i"
                            :class="fila.__match ? 'table-match' : 'table-nomatch'">
                            <td v-for="col in resultados.columns" :key="col">{{ fila[col] }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Paginación -->
            <div class="d-flex justify-content-between align-items-center mt-3">
                <button class="btn btn-outline-secondary" @click="prevPage" :disabled="currentPage === 1">
                    ◀ Anterior
                </button>
                <span>Página {{ currentPage }} de {{ totalPages }}</span>
                <button class="btn btn-outline-secondary" @click="nextPage" :disabled="currentPage === totalPages">
                    Siguiente ▶
                </button>
            </div>

            <!-- Exportar -->
            <div class="mt-3">
                <h5>Descargar resultados (sin filtro):</h5>
                <button class="btn btn-success me-2" @click="exportar('xlsx')">📊 XLSX</button>
                <button class="btn btn-primary me-2" @click="exportar('csv')">📄 CSV</button>
                <button class="btn btn-secondary me-2" @click="exportar('txt')">🧾 TXT</button>
                <button class="btn btn-warning me-2" @click="exportar('xml')">🧬 XML</button>
            </div>
        </div>
    </div>
</template>

<style>
.table-match {
    background-color: #e7f7ee;
    /* verde suave */
}

.table-nomatch {
    background-color: #f8f9fa;
    /* gris muy claro */
}
</style>


<!--
<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";

// === Estado ===
const queries = ref([]);
const selectedQuery = ref(null);
const resultados = ref(null);
const currentPage = ref(1);
const itemsPerPage = 10; // 👈 cantidad de filas por página

// === Cargar consultas ===
const cargarConsultas = async () => {
    const res = await axios.get("http://127.0.0.1:8000/api/queries");
    queries.value = res.data;
};

// === Ejecutar consulta ===
const ejecutarConsulta = async () => {
    if (!selectedQuery.value) {
        alert("Seleccione una consulta primero");
        return;
    }

    try {
        const res = await axios.post(
            `http://127.0.0.1:8000/api/queries/run/${selectedQuery.value}`,
            {}
        );
        resultados.value = res.data;
        currentPage.value = 1; // reinicia paginación
    } catch (error) {
        console.error("Error ejecutando consulta:", error);
        alert("Error ejecutando la consulta. Ver consola.");
    }
};

// === Paginación ===
const paginatedRows = computed(() => {
    if (!resultados.value?.rows) return [];
    const start = (currentPage.value - 1) * itemsPerPage;
    return resultados.value.rows.slice(start, start + itemsPerPage);
});

const totalPages = computed(() => {
    if (!resultados.value?.rows) return 1;
    return Math.ceil(resultados.value.rows.length / itemsPerPage);
});

const nextPage = () => {
    if (currentPage.value < totalPages.value) currentPage.value++;
};

const prevPage = () => {
    if (currentPage.value > 1) currentPage.value--;
};

// === Exportar ===
const exportar = async (format) => {
    if (!selectedQuery.value) {
        alert("Seleccione una consulta primero");
        return;
    }

    try {
        const url = `http://127.0.0.1:8000/api/queries/run/${selectedQuery.value}/export?format=${format}`;
        const response = await fetch(url, { method: "POST" });
        if (!response.ok) throw new Error(`Error al exportar: ${response.status}`);

        const blob = await response.blob();
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `resultado.${format}`;
        link.click();
    } catch (error) {
        console.error("Error en exportar:", error);
        alert("Ocurrió un error al exportar el archivo");
    }
};

onMounted(() => {
    cargarConsultas();
});
</script>

<template>
    <div class="container mt-4">
        <h3 class="fw-bold text-primary">📊 EDD – Ejecución de Consultas</h3>

        
        <div class="mb-3">
            <label class="form-label fw-bold">Seleccionar Consulta:</label>
            <select v-model="selectedQuery" class="form-select">
                <option disabled value="">-- Seleccione --</option>
                <option v-for="q in queries" :key="q.id" :value="q.id">{{ q.name }}</option>
            </select>
        </div>

        <button class="btn btn-primary" @click="ejecutarConsulta">▶ Ejecutar</button>

        <div v-if="resultados && resultados.rows && resultados.rows.length" class="mt-4">
            <h5>Resultado:</h5>
            <table class="table table-bordered table-sm table-striped">
                <thead class="table-light">
                    <tr>
                        <th v-for="col in resultados.columns" :key="col">{{ col }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(fila, i) in paginatedRows" :key="i">
                        <td v-for="col in resultados.columns" :key="col">{{ fila[col] }}</td>
                    </tr>
                </tbody>
            </table>

            <div class="d-flex justify-content-between align-items-center mt-3">
                <button class="btn btn-outline-secondary" @click="prevPage" :disabled="currentPage === 1">
                    ◀ Anterior
                </button>
                <span>Página {{ currentPage }} de {{ totalPages }}</span>
                <button class="btn btn-outline-secondary" @click="nextPage" :disabled="currentPage === totalPages">
                    Siguiente ▶
                </button>
            </div>

            <div class="mt-4">
                <h5>Descargar resultados:</h5>
                <button class="btn btn-success me-2" @click="exportar('xlsx')">📊 XLSX</button>
                <button class="btn btn-primary me-2" @click="exportar('csv')">📄 CSV</button>
                <button class="btn btn-secondary me-2" @click="exportar('txt')">🧾 TXT</button>
                <button class="btn btn-warning me-2" @click="exportar('xml')">🧬 XML</button>
            </div>
        </div>

        <div v-else-if="resultados && (!resultados.rows || !resultados.rows.length)" class="alert alert-warning mt-3">
            No hay resultados para mostrar.
        </div>
    </div>
</template>
-->