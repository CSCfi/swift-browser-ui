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
  getTagsForObjects,
  makeGetObjectsMetaURL,
} from "./conv";

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    projects: [],
    active: {},
    uname: "",
    multipleProjects: false,
    isLoading: false,
    isFullPage: true,
    objectCache: [],
    objectTagsCache: {}, // {"objectName": ["tag1", "tag2"]}
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
    updateContainerTags(state, payload) {
      state.containerTagsCache = { 
        ...state.containerTagsCache, 
        [payload.containerName]: payload.tags,
      };
    },
    updateObjects (
      state,
      payload,
    ) {
      // Update object cache with the new object listing.
      state.objectCache = payload;
    },
    updateObjectTags (state, payload) {
      state.objectTagsCache = { 
        ...state.objectTagsCache, 
        [payload.objectName]: payload.tags,
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
    updateContainers: async function ({ commit, dispatch }, signal) {
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
      dispatch("updateContainerTags", {containers, signal});
      return containers;
    },
    updateContainerTags: function ({ commit }, {containers, signal}) {
      containers.map(async container => {
        const tags = await getTagsForContainer(container.name, signal);
        commit(
          "updateContainerTags", 
          {containerName: container.name, tags},
        );
      });
    },
    updateObjects: async function (
      { commit, dispatch, state }, 
      {route, signal},
    ) {
      let container = route.params.container;
      commit("loading", true);
      if (route.name == "SharedObjects") {
        await state.client.getAccessDetails(
          route.params.project,
          container,
          route.params.owner,
        ).then(
          (ret) => {
            return getSharedObjects(
              route.params.owner,
              container,
              ret.address,
            );
          },
        ).then(
          (ret) => {
            commit("loading", false);
            commit("updateObjects", ret);
          },
        ).catch(() => {
          commit("updateObjects", []);
          commit("loading", false);
        });
      } else {
        await getObjects(
          container,
          signal,
        ).then((ret) => {
          if (ret.status != 200) {
            commit("loading", false);
          }
          commit("updateObjects", ret);
          commit("loading", false);
        }).catch(() => {
          commit("updateObjects", []);
          commit("loading", false);
        });
      }
      dispatch("updateObjectTags", {route, signal});
    },
    updateObjectTags: async function ({ commit, state }, {route, signal}) {
      if (!state.objectCache.length) {
        return;
      }
      let objectList = [];
      for (let i = 0; i < state.objectCache.length; i++) {
        // Object names end up in the URL, which has hard length limits.
        // The aiohttp backend has a limit of 2048. The maximum size
        // for object name is 1024. Set it to a safe enough amount.
        // We split the requests to prevent reaching said limits.
        objectList.push(state.objectCache[i].name);
        const url = makeGetObjectsMetaURL(route.params.container, objectList);
        if (
          i === state.objectCache.length - 1
          || url.href.length > 2000
        ) {
          getTagsForObjects(
            route.params.container, 
            objectList, 
            url,
            signal,
          )
            .then(tags => 
              tags.map(item => {
                commit(
                  "updateObjectTags", 
                  {objectName: item[0], tags: item[1]},
                );
              }),
            );
          objectList = [];
        }
      }
    },
  },
});

export default store;
