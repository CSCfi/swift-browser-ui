import { createRouter, createWebHistory } from "vue-router";
import BucketsView from "@/views/Buckets.vue";
import ObjectsView from "@/views/Objects.vue";
import SharedObjects from "@/views/SharedObjects.vue";
import { getProjects } from "@/common/api.js";
import { getDB } from "@/common/idb";
import { updateContainers } from "./idbFunctions";
import useStore from "@/common/store";

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
  const store = useStore();

  if(to.params.container === store.uploadBucket.name) {
    //When new bucket is created with upload but containers not updated yet
    next();
  }
  else {
    let buckets = await getDB()
      .containers.where({projectID: to.params.project} )
      .toArray();
    if(buckets.length === 0) {
      await updateContainers(to.params.project);
      buckets = await getDB()
        .containers.where({projectID: to.params.project} )
        .toArray();
    }

    const val = buckets.find(item =>
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
      component: BucketsView,
    },
    {
      path: "/browse/:user/:project/:container/shared/:owner",
      name: "SharedObjects",
      component: SharedObjects,
    },
    {
      path: "/browse/:user/:project",
      beforeEnter: checkProject,
      name: "AllBuckets",
      component: BucketsView,
    },
    {
      path: "/browse/:user/:project/shared/to",
      name: "SharedTo",
      component: BucketsView,
    },
    {
      path: "/browse/:user/:project/shared/from",
      name: "SharedFrom",
      component: BucketsView,
    },
    {
      path: "/browse/:user/:project/:container",
      beforeEnter: checkContainer,
      name: "ObjectsView",
      component: ObjectsView,
    },
  ],
});
