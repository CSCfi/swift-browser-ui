import Vue from "vue";
import Router from "vue-router";
import DashboardView from "@/views/Dashboard.vue";
import ContainersView from "@/views/Containers.vue";
import ObjectsView from "@/views/Objects.vue";
import EditObjectView from "@/views/EditObject.vue";
import SharedObjects from "@/views/SharedObjects";
import ShareRequests from "@/views/ShareRequests";
import SharedTo from "@/views/SharedTo";
import SharedFrom from "@/views/SharedFrom";
import SharingView from "@/views/Sharing";
import DirectRequest from "@/views/DirectRequest";
import ReplicationView from "@/views/Replicate";
import TokensView from "@/views/Tokens";
import CreateContainer from "@/views/AddContainer";
import DirectShare from "@/views/DirectShare";
import UploadView from "@/views/Upload";

Vue.use(Router);

export default new Router({
  mode: "history",
  routes: [
    {
      path: "/browse/:user/:project/sharing/to",
      name: "SharedTo",
      component: SharedTo,
    },
    {
      path: "/browse/:user/:project/sharing/from",
      name: "SharedFrom",
      component: SharedFrom,
    },
    {
      path: "/browse/:user/:project/sharing/requests",
      name: "ShareRequests",
      component: ShareRequests,
    },
    {
      path: "/browse/:user/:project/sharing/share",
      name: "SharingView",
      component: SharingView,
    },
    {
      path: "/browse/:user/:project/add",
      name: "AddContainer",
      component: CreateContainer,
    },
    {
      path: "/browse/:user/:project/tokens",
      name: "TokensView",
      component: TokensView,
    },
    {
      path: "/browse/:user/:project/:container/edit",
      name: "EditContainer",
      component: CreateContainer,
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
      path: "/browse/upload/:project/:container",
      name: "UploadView",
      component: UploadView,
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
      path: "/browse/:user/:project/:container/replicate",
      name: "ReplicateContainer",
      component: ReplicationView,
    },
    {
      path: "/browse/:user",
      name: "DashboardView",
      component: DashboardView,
    },
    {
      path: "/browse/:user/:project",
      name: "ContainersView",
      component: ContainersView,
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
