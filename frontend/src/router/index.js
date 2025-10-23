import { createRouter, createWebHistory } from "vue-router";

import Home from "../views/Home.vue";
import QueryStudio from "../views/QueryStudio.vue";
import TemplateStudio from "../views/TemplateStudio.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/queries",
    name: "QueryStudio",
    component: QueryStudio,
  },
  {
    path: "/templates",
    name: "TemplateStudio",
    component: TemplateStudio,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
