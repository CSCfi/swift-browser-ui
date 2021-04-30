import Vue from "vue";
import Router from "vue-router";
import Dashboard from "@/views/Dashboard.vue";
import Containers from "@/views/Containers.vue";
import Objects from "@/views/Objects.vue";
import SharedObjects from "@/views/SharedObjects";
import ShareRequests from "@/views/ShareRequests";
import SharedTo from "@/views/SharedTo";
import SharedFrom from "@/views/SharedFrom";
import Sharing from "@/views/Sharing";
import DirectRequest from "@/views/DirectRequest";
import ReplicationView from "@/views/Replicate";
import Tokens from "@/views/Tokens";
import CreateContainer from "@/views/AddContainer";

Vue.use(Router);

export default new Router({
  mode: "history",
  routes: [
    {
      path: "/browse/sharing/to/:project",
      name: "SharedTo",
      component: SharedTo,
    },
    {
      path: "/browse/sharing/from/:project",
      name: "SharedFrom",
      component: SharedFrom,
    },
    {
      path: "/browse/sharing/requests/:project",
      name: "ShareRequests",
      component: ShareRequests,
    },
    {
      path: "/browse/sharing/share",
      name: "Sharing",
      component: Sharing,
    },
    {
      path: "/browse/container/add",
      name: "AddContainer",
      component: CreateContainer,
    },
    {
      path: "/browse/sharing/requestdirect",
      name: "DirectRequest",
      component: DirectRequest,
    },
    {
      path: "/browse/shared/:project/:owner/:container",
      name: "SharedObjects",
      component: SharedObjects,
    },
    {
      path: "/browse/replicate/:project/:container",
      name: "ReplicateContainer",
      component: ReplicationView,
    },
    {
      path: "/browse/tokens/:project",
      name: "Tokens",
      component: Tokens,
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
