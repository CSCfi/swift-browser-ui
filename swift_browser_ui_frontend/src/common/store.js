// Vuex store for the variables that need to be globally avaliable.
import Vue from "vue";
import Vuex from "vuex";

import { recursivePruneCache } from "@/common/conv";

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
    client: undefined,
    requestClient: undefined,
  },
  mutations: {
    updateContainers (state, newList) {
      // Update container cache with the new container listing.
      state.containerCache = newList;
    },
    updateObjects (state, updateTuple) {
      // Update object cache as the object listing required wasn't
      // available in the cache.
      state.objectCache = recursivePruneCache(
        state.objectCache,
      );
      state.objectCache[updateTuple[0]] = updateTuple[1];
    },
    eraseObjects (state) {
      state.objectCache = {};
    },
    setProjects (state, newProjects) {
      // Update the project listing in store
      state.projects = newProjects;
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
    setSharingClient (state, newClient) {
      state.client = newClient;
    },
    setRequestClient (state, newClient) {
      state.requestClient = newClient;
    },
  },
});

export default store;
