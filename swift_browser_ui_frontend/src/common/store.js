// Vuex store for the variables that need to be globally available.
import Vue from "vue";
import Vuex from "vuex";

import { getBuckets } from "@/common/api";
import { 
  getObjects,
  getSharedObjects,
} from "./api";

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    projects: [],
    active: undefined,
    uname: undefined,
    multipleProjects: false,
    isLoading: false,
    isFullPage: true,
    objectCache: [],
    containerCache: [],
    langs: [
      {ph: "In English", value: "en"},
      {ph: "Suomeksi", value: "fi"},
    ],
    client: undefined,
    requestClient: undefined,
    resumableClient: undefined,
    isUploading: false,
    isChunking: false,
    uploadProgress: undefined,
    altContainer: undefined,
  },
  mutations: {
    updateContainers (state) {
      // Update container cache with the new container listing.
      state.isLoading = true;
      getBuckets().then((ret) => {
        if (ret.status != 200) {
          state.isLoading = false;
        }
        state.containerCache = ret;
        state.isLoading = false;
      }).catch(() => {
        state.isLoading = false;
      });
    },
    updateObjects (
      state,
      payload,
    ) {
      // Update object cache with the new object listing.
      let container = payload.route.params.container;
      state.isLoading = true;
      if (payload.route.name == "SharedObjects") {
        payload.route.params.project,
        container,
        state.client.getAccessDetails(
          payload.route.params.owner,
        ).then(
          (ret) => {
            return getSharedObjects(
              payload.route.params.owner,
              container,
              ret.address,
            );
          },
        ).then(
          (ret) => {
            state.isLoading = false;
            state.objectCache = ret;
          },
        ).catch(() => {
          state.objectCache = [];
          state.isLoading = false;
        });
      }
      else {
        getObjects(container).then((ret) => {
          if (ret.status != 200) {
            state.isLoading = false;
          }
          state.objectCache = ret;
          state.isLoading = false;
        }).catch(() => {
          state.objectCache = [];
          state.isLoading = false;
        });
      }
    },
    eraseObjects (state) {
      state.objectCache = [];
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
    setResumable (state, newClient) {
      state.resumableClient = newClient;
    },
    setUploading (state) {
      state.isUploading = true;
    },
    stopUploading (state) {
      state.isUploading = false;
    },
    setChunking (state) {
      state.isChunking = true;
    },
    stopChunking (state) {
      state.isChunking = false;
    },
    updateProgress (state, progress) {
      state.uploadProgress = progress;
    },
    eraseProgress (state) {
      state.uploadProgress = undefined;
    },
    setAltContainer (state, altContainer) {
      state.altContainer = altContainer;
    },
    eraseAltContainer (state) {
      state.altContainer = undefined;
    },
  },
});

export default store;
