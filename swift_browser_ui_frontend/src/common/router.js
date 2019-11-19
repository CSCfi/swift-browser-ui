import Vue from "vue";
import Router from "vue-router";
import Dashboard from "@/views/Dashboard.vue";
import Containers from "@/views/Containers.vue";
import Objects from "@/views/Objects.vue";
import SharedObjects from "@/views/SharedObjects";
import ShareRequests from "@/views/ShareRequests";
import SharedTo from "@/views/SharedTo";
import SharedFrom from "@/views/SharedFrom";

Vue.use(Router);

export default new Router({
  mode: "history",
  routes: [
    {
      path: "/browse/sharing/to/:user",
      name: "SharedTo",
      component: SharedTo,
    },
    {
      path: "/browse/sharing/from/:user",
      name: "SharedFrom",
      component: SharedFrom,
    },
    {
      path: "/browse/sharing/requests/:user",
      name: "ShareRequests",
      component: ShareRequests,
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
