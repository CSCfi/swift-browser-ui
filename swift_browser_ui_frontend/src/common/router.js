import Vue from "vue";
import Router from "vue-router";
import DashboardView from "@/views/Dashboard.vue";
import FoldersView from "@/views/Folders.vue";
import ObjectsView from "@/views/Objects.vue";
import EditObjectView from "@/views/EditObject.vue";
import SharedObjects from "@/views/SharedObjects";
import DirectRequest from "@/views/DirectRequest";
import ReplicationView from "@/views/Replicate";
import TokensView from "@/views/Tokens";
import DirectShare from "@/views/DirectShare";

Vue.use(Router);

export default new Router({
  mode: "history",
  routes: [
    {
      path: "/browse/:user/:project/tokens",
      name: "TokensView",
      component: TokensView,
    },
    {
      path: "/browse/:user/:project/sharing/requestdirect",
      name: "DirectRequest",
      component: DirectRequest,
    },
    {
      path: "/browse/:user/:project/sharing/sharedirect",
      name: "DirectShare",
      component: DirectShare,
    },
    {
      path: "/browse/:user/:project/:container/shared/:owner",
      name: "SharedObjects",
      component: SharedObjects,
    },
    {
      path: "/browse/:user/:project/:container/shared/:owner/:object/edit",
      name: "EditSharedObjectView",
      component: EditObjectView,
    },
    {
      path: "/browse/:user/:project/:container/replicate/:from",
      name: "ReplicateContainer",
      component: ReplicationView,
    },
    {
      path: "/browse/:user/:project/info",
      name: "DashboardView",
      component: DashboardView,
    },
    {
      path: "/browse/:user/:project",
      name: "AllFolders",
      component: FoldersView,
    },
    {
      path: "/browse/:user/:project/shared/to",
      name: "SharedTo",
      component: FoldersView,
    },
    {
      path: "/browse/:user/:project/shared/from",
      name: "SharedFrom",
      component: FoldersView,
    },
    {
      path: "/browse/:user/:project/:container",
      name: "ObjectsView",
      component: ObjectsView,
    },
    {
      path: "/browse/:user/:project/:container/:object/edit",
      name: "EditObjectView",
      component: EditObjectView,
    },
  ],
});
