<template>
  <c-card
    ref="copyFolderContainer"
    class="copy-folder"
    @keydown="handleKeyDown"
  >
    <div class="modal-content-wrapper">
      <h2 class="title is-4">
        {{
          $t("message.replicate.copy_folder") + selectedFolderName
        }}
      </h2>
      <c-card-content>
        <div id="folder-name-wrapper">
          <c-text-field
            id="new-copy-folderName"
            v-model="folderName"
            v-csc-control
            :label="$t('message.replicate.name_newFolder')"
            name="foldername"
            :valid="loadingFoldername || errorMsg.length === 0"
            :validation="errorMsg"
            aria-required="true"
            required
          />
          <c-loader v-show="loadingFoldername" />
        </div>
        <label
          class="taginput-label"
          label-for="copy-folder-taginput"
        >
          {{ $t('message.tagName') }}
        </label>
        <TagInput
          id="copy-folder-taginput"
          :tags="tags"
          @addTag="addingTag"
          @deleteTag="deletingTag"
        />
      </c-card-content>
    </div>
    <c-card-actions justify="space-between">
      <c-button
        outlined
        size="large"
        @click="cancelCopy(false)"
        @keyup.enter="cancelCopy(true)"
      >
        {{ $t("message.cancel") }}
      </c-button>
      <c-button
        size="large"
        @click="replicateContainer(false)"
        @keyup.enter="replicateContainer(true)"
      >
        {{ $t("message.copy") }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import { debounce, delay } from "lodash";
import {
  swiftCopyContainer,
  updateContainerMeta,
  getObjects,
} from "@/common/api";
import { getDB } from "@/common/db";

import {
  addNewTag,
  deleteTag,
  validateFolderName,
} from "@/common/globalFunctions";
import {
  getFocusableElements,
  moveFocusOutOfModal,
  keyboardNavigationInsideModal,
} from "@/common/keyboardNavigation";
import { useObservable } from "@vueuse/rxjs";
import { liveQuery } from "dexie";
import TagInput from "@/components/TagInput.vue";

import { toRaw } from "vue";

export default {
  name: "CopyFolderModal",
  components: { TagInput },
  data() {
    return {
      folderName: "",
      loadingFoldername: true,
      tags: [],
      folders: [],
      checkpointsCompleted: 0,
      errorMsg: "",
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
    selectedFolderName() {
      return this.$store.state.selectedFolderName.length > 0
        ? this.$store.state.selectedFolderName
        : "";
    },
    sourceProjectId() {
      return this.$store.state.sourceProjectId;
    },
    visible() {
      return this.$store.state.openCopyFolderModal;
    },
  },
  watch: {
    visible: function () {
      if (this.visible) {
        if (this.selectedFolderName && this.selectedFolderName.length > 0) {
          this.fetchFolders().then(() => {
            if(this.folders && this.folders.length > 0) {
              this.getCopyFolder(this.selectedFolderName);
            }
          });
        }
      }
    },
    folderName() {
      if (this.folderName) {
        this.checkValidity();
      }
    },
    checkpointsCompleted() {
      if (this.checkpointsCompleted > 1) {
        this.$store.commit("setFolderCopiedStatus", true);
        document.querySelector("#copyFolder-toasts")
          .removeToast("copy-in-progress");
      }
    },
  },
  methods: {
    fetchFolders: async function () {
      if (
        this.active.id === undefined &&
        this.$route.params.project === undefined
      ) {
        return;
      }
      this.folders = useObservable(
        liveQuery(() =>
          getDB().containers
            .where({ projectID: this.$route.params.project })
            .toArray(),
        ),
      );

      await this.$store.dispatch("updateContainers", {
        projectID: this.$route.params.project,
        signal: null,
      });
    },
    getCopyFolder: function (origFolderName) {
      if (this.folders) {
        // Check if current folder is a copy
        const reg = new RegExp("\\b(copy)\\s(\\d+)\\b$", "i");
        const isCopied = origFolderName.match(reg);

        // Use a var to keep the folder as a copy name without copy version
        let copiedFolder = "";
        if (isCopied) {
          copiedFolder = `${origFolderName.slice(0, isCopied["index"])}copy`;
        } else {
          copiedFolder = `${origFolderName} copy`;
        }

        const existingCopiedFolders = [];
        for (let folder of this.folders) {
          // Check if folder is one of the copy versions
          // which ends in the form 'copy + number'
          const copiedReg = new RegExp(`\\b${copiedFolder}\\s(\\d+)\\b$`, "gi");
          folder.name.match(copiedReg) ?
            existingCopiedFolders.push(folder.name) : null;
        }

        if (existingCopiedFolders.length > 0) {
          // Sort the array in asc, the last item is the latest copy
          // then extract the copy version from it
          existingCopiedFolders.sort();
          const latestVer= existingCopiedFolders[
            existingCopiedFolders.length-1].match(reg);
          this.folderName = !isCopied ? `${copiedFolder} ${+latestVer[2] + 1}` : origFolderName.replace(/\d+$/, +latestVer[2]+1);
        } else {
          this.folderName = `${copiedFolder} 1`;
        }
        this.loadingFoldername = false;
      }
    },
    cancelCopy: function (keypress) {
      this.$store.commit("toggleCopyFolderModal", false);
      this.$store.commit("setFolderName", "");
      this.folderName = "";
      this.tags = [];
      this.loadingFoldername = true;
      this.errorMsg = "";
      document.querySelector("#copyFolder-toasts").removeToast("copy-error");

      /*
        Prev Active element is a popup menu and it is removed from DOM
        when we click it to open Copy Folder Modal.
        Therefore, we need to make its focusable parent
        to be focused instead after we close the modal.
      */
      if (keypress) {
        const prevActiveElParent = document.getElementById("container-table");
        moveFocusOutOfModal(prevActiveElParent, true);
      }
    },
    replicateContainer: function (keypress) {
      this.folderName = this.folderName.trim();
      this.checkValidity();
      this.a_replicate_container(keypress).then(() => {});
    },
    a_replicate_container: async function (keypress) {
      if (this.errorMsg.length) return;
      this.$store.commit("toggleCopyFolderModal", false);
      document.querySelector("#copyFolder-toasts").addToast(
        {
          id: "copy-in-progress",
          type: "success",
          indeterminate: true,
          message: "",
          custom: true,
        },
      );

      // Fetch the source project id if it exists
      let sourceProjectName = "";
      if (this.sourceProjectId) {
        let ids = await this.$store.state.client.projectCheckIDs(
          this.sourceProjectId,
        );
        sourceProjectName = ids.name;
      }

      // Initiate the container replication operation
      await swiftCopyContainer(
        this.active.id,
        this.folderName,
        this.sourceProjectId ? this.sourceProjectId : this.active.id,
        this.selectedFolderName,
        this.active.name,
        sourceProjectName,
      ).then(async () => {
        await this.$store.dispatch("updateContainers", {
          projectID: this.$route.params.project,
          signal: null,
        });

        this.checkpointsCompleted = 0;

        const tags = toRaw(this.tags);
        let metadata = {
          usertags: tags.join(";"),
        };
        delay((id, folder, meta, tgs) => {
          updateContainerMeta(id, folder, meta)
            .then(
              async () => {
                await getDB().containers
                  .where({
                    projectID: id,
                    name: folder,
                  })
                  .modify({ tgs });
              },
            );

          this.checkpointsCompleted++;
        }, 5000, this.active.id, this.folderName, metadata, tags);

        getObjects(
          this.sourceProjectId ? this.sourceProjectId : this.active.id,
          this.selectedFolderName,
        ).then(async (objects) => {
          const sleep =
            time => new Promise(resolve => setTimeout(resolve, time));

          let copiedObjects = undefined;
          while (copiedObjects === undefined ||
            copiedObjects.length < objects.length) {
            const task = getObjects(this.active.id, this.folderName)
              .then((obj) => copiedObjects = obj );

            await Promise.all([task, sleep(2000)]);
          }

          this.checkpointsCompleted++;
          this.cancelCopy(keypress);
        });
      }).catch(() => {
        document.querySelector("#copyFolder-toasts").addToast(
          {
            id: "copy-error",
            type: "error",
            duration: 5000,
            persistent: false,
            progress: false,
            message: this.$t("message.copyfail"),
          },
        );
      });
    },
    addingTag: function (e, onBlur) {
      this.tags = addNewTag(e, this.tags, onBlur);
    },
    deletingTag: function (e, tag) {
      this.tags = deleteTag(e, tag, this.tags);
    },
    checkValidity: debounce(function () {
      this.errorMsg = validateFolderName(
        this.folderName, this.$t, this.folders);
    }, 300, { leading: true }),
    handleKeyDown: function (e) {
      const focusableList = this.$refs.copyFolderContainer.querySelectorAll(
        "input, c-icon, c-button",
      );
      const { first, last } = getFocusableElements(focusableList);
      keyboardNavigationInsideModal(e, first, last);
    },
  },
};
</script>

<style lang="scss" scoped>

.copy-folder {
  padding: 3rem;
  position: absolute;
  top: -1rem;
  left: 0;
  right: 0;
  max-height: 75vh;
}

@media screen and (max-width: 767px), (max-height: 580px) {
   .copy-folder {
    top: -5rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 767px),
(max-width: 525px) {
  .copy-folder {
    top: -9rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 525px) {
  .copy-folder {
    top: -13rem;
  }
}

c-card-content {
  color: var(--csc-dark);
  padding: 0;
}

c-card-actions {
  padding: 0;
}

c-card-actions > c-button {
  margin: 0;
}

#folder-name-wrapper {
  position: relative;
  padding-top: 0.5rem;
}

</style>
