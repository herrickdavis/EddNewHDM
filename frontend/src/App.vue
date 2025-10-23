<template>
  <nav class="navbar navbar-expand navbar-dark bg-dark px-3 shadow-sm">
    <a class="navbar-brand fw-bold text-light" href="#">🧩 EDD</a>
    <div class="navbar-nav">
      <router-link class="nav-link" to="/" active-class="active"
        >🏠 Home</router-link
      >
      <router-link class="nav-link" to="/queries" active-class="active"
        >📊 Consultas</router-link
      >
      <router-link class="nav-link" to="/templates" active-class="active"
        >📋 Plantillas</router-link
      >
    </div>
  </nav>

  <div class="container mt-4">
    <router-view></router-view>
  </div>
</template>

<script setup>
// El router-view carga dinámicamente las vistas
</script>

<style>
body {
  background-color: #f8f9fa;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

/* Navbar */
.navbar {
  border-bottom: 2px solid #0d6efd;
}

.navbar-brand {
  font-size: 1.2rem;
  letter-spacing: 1px;
}

.nav-link {
  color: #ffffffcc;
  font-weight: 500;
  margin-right: 12px;
}

.nav-link.active,
.nav-link:hover {
  color: #ffffff;
  background-color: #0d6efd33;
  border-radius: 6px;
}

.container {
  padding-top: 15px;
}
</style>
