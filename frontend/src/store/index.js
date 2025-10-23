import { defineStore } from "pinia";
import api from "../api/eddApi";

export const useEddStore = defineStore("edd", {
  state: () => ({
    datasources: [],
    queries: [],
    templates: [],
    result: null
  }),
  actions: {
    async loadDatasources() {
      const { data } = await api.get("/datasources");
      this.datasources = data;
    },
    async loadQueries() {
      const { data } = await api.get("/queries");
      this.queries = data;
    },
    async runQuery(id, params = {}) {
      const { data } = await api.post(`/queries/run/${id}`, params);
      this.result = data;
    }
  }
});
