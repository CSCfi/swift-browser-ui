import Vue from "vue";
import Router from "vue-router";
import FoldersView from "@/views/Folders.vue";
import ObjectsView from "@/views/Objects.vue";
import SharedObjects from "@/views/SharedObjects";
import TokensView from "@/views/Tokens";

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
      path: "/browse/:user/:project/:container/shared/:owner",
      name: "SharedObjects",
      component: SharedObjects,
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
  ],
});
