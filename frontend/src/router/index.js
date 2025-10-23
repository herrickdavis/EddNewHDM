import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import QueryStudio from "../views/QueryStudio.vue";
import Templates from "../views/Templates.vue";

const routes = [
  { path: "/", name: "Home", component: Home },
  { path: "/queries", name: "QueryStudio", component: QueryStudio },
  { path: "/templates", name: "Templates", component: Templates },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
