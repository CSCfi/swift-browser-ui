// Vuex store for the variables that need to be globally available.
import Vue from "vue";
import Vuex from "vuex";

import { getContainers } from "@/common/api";
import { getObjects } from "@/common/api";
import {
  getTagsForContainer,
  getTagsForObjects,
  makeGetObjectsMetaURL,
  filterSegments,
  tokenize,
} from "./conv";

import { initDB } from "@/common/db";
Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    db: initDB(),
    projects: [],
    active: {},
    uname: "",
    multipleProjects: false,
    isLoading: false,
    isFullPage: true,
    objectCache: {}, // Only for shared objects
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
    uploadInfo: undefined,
    transfer: [],
    pubkey: [],
    currentPrefix: "",
  },
  mutations: {
    loading(state, payload) {
      state.isLoading = payload;
    },
    updateObjects (state,objects) {
      // Update object cache with the new object listing.
      state.objectCache = [...objects];
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
    setUploadInfo (state, uploadInfo) {
      state.uploadInfo = uploadInfo;
    },
    eraseUploadInfo (state) {
      state.uploadInfo = undefined;
    },
    appendFileTransfer (state, file) {
      state.transfer.push(file);
    },
    eraseTransfer (state) {
      state.transfer = [];
    },
    appendPubKey (state, key) {
      state.pubkey.push(key);
    },
    erasePubKey (state) {
      state.pubkey = [];
    },
    setPrefix (state, prefix) {
      state.currentPrefix = prefix;
    },
    erasePrefix (state) {
      state.currentPrefix = "";
    },
  },
  actions: {
    updateContainers: async function (
      { state, commit, dispatch },
      { projectID, signal },
    ) {
      const existingContainers = await state.db.containers
        .where({projectID})
        .toArray();
      if (existingContainers.length === 0) {
        commit("loading", true);
      }
      let containers;
      let marker = "";
      let newContainers = [];
      do {
        containers = [];
        containers = await getContainers(
          projectID,
          marker,
        ).catch(() => {
          commit("loading", false);
        });
        commit("loading", false);
        if(containers.length > 0) {
          containers.forEach(cont => {
            cont.tokens = tokenize(cont.name);
            cont.projectID = projectID;
          });
          await state.db.containers.bulkPut(containers).cacth(() => {});
          newContainers = newContainers.concat(containers);
          marker = containers[containers.length - 1].name;
        }
      } while (containers.length > 0);
      await dispatch("updateContainerTags", {projectID, newContainers, signal});
      const toDelete = [];
      existingContainers.map(oldCont => {
        if(!newContainers.find(cont => cont.name == oldCont.name)) {
          toDelete.push(oldCont.id);
        }
      });
      if (toDelete.length) {
        await state.db.containers.bulkDelete(toDelete);
        await state.db.objects.where("containerID").anyOf(toDelete).delete();
      }
      const containersFromDB = await state.db.containers
        .where({projectID}).toArray();
      for (let i = 0; i < containersFromDB.length; i++) {
        const container = containersFromDB[i];
        const oldContainer = existingContainers.find(
          cont => cont.name === container.name,
        );
        let updateObjects = true;
        const dbObjects = await state.db.objects
          .where({"containerID": container.id}).count();
        if (
          oldContainer &&
          container.count === oldContainer.count &&
          container.bytes === oldContainer.bytes &&
          !(dbObjects === 0)
        ) {
          updateObjects = false;
        }
        if (container.count === 0) {
          updateObjects = false;
          await state.db.objects
            .where({"containerID": container.id}).delete();
        }
        if (updateObjects) {
          dispatch(
            "updateObjects",
            {
              cotnainer: container,
              signal,
            }
          )
        }
      }
    },
    updateContainerTags: function (
      {state},
      {projectID, containers, signal}
    ) {
      containers.map(async container => {
        const tags = await getTagsForContainer(
          projectID,
          container,
          signal,
        ) || null;
        await state.db.containers
          .where({"projectID": container.projectID, "name": container.name})
          .modify({tags});
      });
    },
    updateObjects: async function (
      { state, dispatch },
      { projectID, container, signal },
    ) {
      const isSegmentsContainer= container.name.match("_segments");
      const existingObjects = await state.db.objects
        .where({containerID: container.id}).toArray();
      let newObjects = [];
      let objects;
      let marker = "";
      do {
        objects = await getObjects(
          projectID,
          container,
          marker,
          signal,
        );
        if (objects.length > 0) {
          objects.forEach(obj => {
            obj.container = container.name;
            obj.containerID = container.id;
            obj.tokens = isSegmentsContainer ? [] : tokenize(obj.name);
          })
          await state.db.object.bulkPut(objects).catch(() => {});
          newObjects = newObjects.concat(objects);
          marker = objects[objects.length -1].name;
        }
      } while (objects.length > 0);
  
      let toDelete = [];
      existingObjects.map(oldObj => {
        if(!objects.find(obj => obj.name === oldObj.name)) {
          toDelete.push(oldObj.id);
        }
      })
      if(toDelete.length) {
        await state.db.objects.bulkDelete(toDelete);
      }
      if (!isSegmentsContainer) {
        await dispatch("updateObjectTags", {projectID, container, signal});
      }
    },
    updateObjectTags: async function ({ commit, state }, {route, signal}) {
      if (
        !state.objectCache.length
        || (state.objectCache.length > 25000)
      ) {
        return;
      }
    },
    updateObjectTags: async function (
      { state, commit }, 
      { container, signal, sharedObjects=undefined }) {
      let objectList = [];

      let objects = [];
      if (sharedObjects) {
        objects = sharedObjects;
      } else {
        objects = await state.db.objects
          .where({"containerID": container.id}).toArray();
      }
      
      for (let i = 0; i < objects.length; i++) {
        // Object names end up in the URL, which has hard length limits.
        // The aiohttp backend has a limit of 8192. The maximum size
        // for object name is 1024. Set it to a safe enough amount.
        // We split the requests to prevent reaching said limits.
        objectList.push(objects[i].name);
        const url = makeGetObjectsMetaURL(
          route.params.project,
          container,
          objectList,
        );
        if (
          i === state.objectCache.length - 1
          || url.href.length > 8192
        ) {
          getTagsForObjects(
            route.params.project,
            route.params.container,
            objectList,
            url,
            signal,
          ).then(tags => tags);
          tags.map(item => {
            const objectName = item[0];
            const tags = item[1];
            if (sharedObjects) {
              objects.forEach(obj => {
                if (obj.name === objectName) {
                  obj.tags = tags;
                }
              });
              commit("updateObjects", objects);
            } else {
              state.db.objects.where(
                {"containerID": container.id, "name": objectName},
              ).modify({tags});
            }
          }),
          objectList = [];
        }
      }
    },
    updateSharedObjects: async function (
      { commit, dispatch, state }, 
      { owner, project, container, signal },
    ) {
      commit("loading", true);
      await state.client.getAccessDetails(
        project,
        container.name,
        owner,
      ).then(
        (ret) => {
          return getSharedObjects(
            owner,
            container.name,
            ret.address,
            signal,
          );
        },
      ).then(
        (ret) => {
          commit("loading", false);
          const sharedObjects = filterSegments(ret);
          commit("updateObjects", sharedObjects);
          dispatch("updateObjectTags", {sharedObjects, container, signal});
        },
      ).catch(() => {
        commit("updateObjects", []);
        commit("loading", false);
      });
    },
  },
});

export default store;
