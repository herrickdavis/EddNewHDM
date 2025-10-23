<template>
  <div class="container mt-4">
    <h2 class="mb-3">🧩 Constructor de Plantillas</h2>

    <!-- Selección de Query -->
    <div class="card p-3 mb-3 shadow-sm">
      <label class="form-label fw-bold">Selecciona una consulta</label>
      <select v-model="selectedQuery" class="form-select">
        <option disabled value="">-- Selecciona una consulta --</option>
        <option v-for="q in queries" :key="q.id" :value="q.id">
          {{ q.name }}
        </option>
      </select>
    </div>

    <!-- Nombre de la plantilla -->
    <div class="card p-3 mb-3 shadow-sm">
      <label class="form-label fw-bold">Nombre de la plantilla</label>
      <input type="text" v-model="templateName" class="form-control" placeholder="Ejemplo: Plantilla Control Diario" />
    </div>

    <!-- Modo de visualización -->
    <div class="card p-3 mb-3 shadow-sm">
      <label class="form-label fw-bold">Modo de visualización</label>
      <div class="form-check">
        <input class="form-check-input" type="radio" id="horizontal" value="horizontal" v-model="mode" />
        <label class="form-check-label" for="horizontal">Horizontal</label>
      </div>
      <div class="form-check">
        <input class="form-check-input" type="radio" id="vertical" value="vertical" v-model="mode" />
        <label class="form-check-label" for="vertical">Vertical</label>
      </div>
    </div>

    <!-- Descripción -->
    <div class="card p-3 mb-3 shadow-sm">
      <label class="form-label fw-bold">Descripción</label>
      <textarea v-model="description" class="form-control" rows="2"
        placeholder="Breve descripción de la plantilla"></textarea>
    </div>

    <!-- Botón de guardar -->
    <div class="text-end">
      <button class="btn btn-primary px-4" @click="guardarPlantilla">
        💾 Guardar Plantilla
      </button>
    </div>

    <!-- Listado de plantillas existentes -->
    <div class="card mt-4 shadow-sm">
      <div class="card-header fw-bold">📋 Plantillas registradas</div>
      <ul class="list-group list-group-flush">
        <li class="list-group-item" v-for="t in templates" :key="t.id">
          <strong>{{ t.name }}</strong> — {{ t.mode }} — Query: {{ t.query_id }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useEddStore } from "../store/index.js";
import api from "../api/eddApi";

const store = useEddStore();
const templates = ref([]);
const selectedQuery = ref("");
const templateName = ref("");
const mode = ref("horizontal");
const description = ref("");
const queries = ref([]);

onMounted(async () => {
  await store.loadQueries();
  queries.value = store.queries;
  const { data } = await api.get("/templates");
  templates.value = data;
});

async function guardarPlantilla() {
  if (!selectedQuery.value) {
    alert("Selecciona una consulta primero.");
    return;
  }

  if (!templateName.value.trim()) {
    alert("Debes ingresar un nombre para la plantilla.");
    return;
  }

  const nuevaPlantilla = {
    name: templateName.value.trim(),
    mode: mode.value,
    description: description.value,
    query_id: selectedQuery.value,
    layout_json: {},
    filters_json: {},
    rules_json: {},
    active: true,
  };

  const { data } = await api.post("/templates", nuevaPlantilla);
  templates.value.push(data);

  // Limpieza de formulario
  templateName.value = "";
  description.value = "";
  selectedQuery.value = "";
  mode.value = "horizontal";

  alert("✅ Plantilla guardada correctamente.");
}
</script>

<style>
.container {
  max-width: 800px;
}

.card {
  border-radius: 10px;
}
</style>
