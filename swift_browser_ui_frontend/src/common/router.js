import Vue from "vue";
import Router from "vue-router";
import Dashboard from "@/views/Dashboard.vue";
import Containers from "@/views/Containers.vue";
import Objects from "@/views/Objects.vue";
import Shared from "@/views/Shared.vue";
import SharedObjects from "@/views/SharedObjects.vue";

Vue.use(Router);

export default new Router({
  mode: "history",
  routes: [
    {
      path: "/browse/shared/:user",
      name: "Shared",
      component: Shared,
    },
    {
      path: "/browse/shared/:user/:owner/:container",
      name: "SharedObjects",
      component: SharedObjects,
    },
    {
      path: "/browse/:user",
      name: "Dashboard",
      component: Dashboard,
    },
    {
      path: "/browse/:user/:project",
      name: "Containers",
      component: Containers,
    },
    {
      path: "/browse/:user/:project/:container",
      name: "Objects",
      component: Objects,
    },
  ],
});
