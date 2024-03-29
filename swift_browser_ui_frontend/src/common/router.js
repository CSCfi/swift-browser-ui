import { createRouter, createWebHistory } from "vue-router";
import FoldersView from "@/views/Folders.vue";
import ObjectsView from "@/views/Objects.vue";
import SharedObjects from "@/views/SharedObjects.vue";
import {getProjects, getContainers} from "@/common/api.js";
import { getDB } from "@/common/db";
import store from "@/common/store";

async function checkProject (to, from, next){

  let projects = await getDB()
    .projects.where({id: to.params.project} )
    .toArray();
  if(projects.length === null){
    projects = await getProjects();
    const val = projects.find(item =>
      item.id === to.params.project);
    if (val === undefined) {
      window.location.pathname = "/notfound";
    }

  } else {
    if(projects.length !== 1){
      window.location.pathname = "/notfound";
    }
  }
  next();
}
async function checkContainer (to, from, next){

  if(to.params.container === store.state.uploadFolder.name) {
    //When new folder is created with upload but containers not updated yet
    next();
  }
  else {
    let containers = await getDB()
      .containers.where({projectID: to.params.project} )
      .toArray();
    if(containers.length === 0){
      containers = await getContainers();
    }
    const val = containers.find(item =>
      item.name === to.params.container);
    if(val === undefined) {
      window.location.pathname = "/notfound";
    }
    next();
  }
}

export default createRouter({

  history: createWebHistory(),
  routes: [
    {
      path: "/browse",
      name: "Browse",
      component: FoldersView,
    },
    {
      path: "/browse/:user/:project/:container/shared/:owner",
      name: "SharedObjects",
      component: SharedObjects,
    },
    {
      path: "/browse/:user/:project",
      beforeEnter: checkProject,
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
      beforeEnter: checkContainer,
      name: "ObjectsView",
      component: ObjectsView,
    },
  ],
});
