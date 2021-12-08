// Vuex store for the variables that need to be globally available.
import Vue from "vue";
import Vuex from "vuex";

import { getBuckets } from "@/common/api";
import {
  getObjects,
  getSharedObjects,
} from "./api";
import {
  getTagsForContainer,
} from "./conv";

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
    containerTagsCache: {}, // {"containerName": ["tag1", "tag2"]}
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
    loading(state, payload) {
      state.isLoading = payload;
    },
    updateContainers (state, payload) {
      // Update container cache with the new container listing.
      state.containerCache = payload;
    },
    updateObjects (
      state,
      payload,
    ) {
      // Update object cache with the new object listing.
      let container = payload.route.params.container;
      state.isLoading = true;
      if (payload.route.name == "SharedObjects") {
        state.client.getAccessDetails(
          payload.route.params.project,
          container,
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
    updateContainerTags(state, payload) {
      state.containerTagsCache = { 
        ...state.containerTagsCache, 
        [payload.containerName]: payload.tags,
      };
    },
    eraseObjects(state) {
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
  actions: {
    updateContainers: async function ({ commit, dispatch }) {
      commit("loading", true);
      let containers = [];
      await getBuckets().then((ret) => {
        if (ret.status != 200) {
          commit("loading", false);
        }
        containers = ret;
        commit("updateContainers", ret);
        commit("loading", false);
      }).catch(() => {
        commit("loading", false);
      });
      dispatch("updateContainerTags", containers);
      return containers;
    },
    updateContainerTags: function ({ commit }, containers) {
      containers.map(async container => {
        const tags = await getTagsForContainer(container.name);
        commit(
          "updateContainerTags", 
          {containerName: container.name, tags},
        );
      });
    },
  },
});

export default store;
