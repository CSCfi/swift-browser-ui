// Vuex store for the variables that need to be globally avaliable.
import Vue from "vue";
import Vuex from "vuex";

import recursivePruneCache from "@/conv";

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    projects: [],
    active: "",
    uname: "",
    multipleProjects: false,
    isLoading: false,
    isFullPage: true,
    objectCache: {},
    containerCache: [],
    langs: [
      {ph: "In English", value: "en"},
      {ph: "Suomeksi", value: "fi"},
    ],
  },
  mutations: {
    updateContainers (state, newList) {
      // Update container cache with the new container listing.
      state.containerCache = newList;
    },
    updateObjects (state, toCache, containerName) {
      // Update object cache as the object listing required wasn't
      // available in the cache.
      state.containerCache = recursivePruneCache(
        state.objectCache,
      );
      state.containerCache[containerName] = toCache;
    },
    setProjects (state, newProjects) {
      // Update the project listing in store
      state.active = newProjects;
      if (newProjects.length > 1) {
        state.multipleProjects = true;
      } else {
        state.multipleProjects = false;
      }
    },
    setActive (state, newActive) {
      // Update the active project in store
      state.active = newActive;
    },
    setUname (state, newUname) {
      // Update the username in store
      state.uname = newUname;
    },
    setLoading (state, newValue) {
      state.isLoading = newValue;
    },
  },
});

export default store;
