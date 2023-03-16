<template>
  <c-card class="copy-folder">
    <div class="modal-content-wrapper">
      <h2 class="title is-4 has-text-dark">
        {{
          $t("message.replicate.copy_folder") + selectedFolderName
        }}
      </h2>
      <c-card-content>
        <c-alert
          v-show="folderExists"
          type="warning"
        >
          <p class="has-text-dark">
            {{ $t("message.replicate.destinationExists") }}
          </p>
        </c-alert>
        <c-text-field
          id="new-copy-folderName"
          v-model="folderName"
          v-csc-control
          :label="$t('message.replicate.name_newFolder')"
          name="foldername"
          :loading="loadingFoldername"
        />
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
        @click="cancelCopy"
        @keyup.enter="cancelCopy"
      >
        {{ $t("message.cancel") }}
      </c-button>
      <c-button
        size="large"
        :disabled="folderExists"
        @click="replicateContainer"
        @keyup.enter="replicateContainer"
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
} from "@/common/api";

import {
  addNewTag,
  deleteTag,
} from "@/common/globalFunctions";
import escapeRegExp from "lodash/escapeRegExp";
import { useObservable } from "@vueuse/rxjs";
import { liveQuery } from "dexie";
import TagInput from "@/components/TagInput.vue";

export default {
  name: "CopyFolderModal",
  components: { TagInput },
  data() {
    return {
      folderExists: false,
      folderName: "",
      loadingFoldername: true,
      tags: [],
      folders: [],
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
  },
  watch: {
    selectedFolderName: function () {
      if (this.selectedFolderName && this.selectedFolderName.length > 0) {
        this.fetchFolders().then(() => {
          if(this.folders && this.folders.length > 0) {
            this.getCopyFolder(this.selectedFolderName);
          }
        });
      }
    },
    folderName: debounce(function () {
      this.checkSelectedFolder();
    }, 300),
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
          this.$store.state.db.containers
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
    checkSelectedFolder: function () {
      // request parameter should be sanitized first
      const safeKey = escapeRegExp(this.folderName).trim();
      let re = new RegExp("^".concat(safeKey, "$"));

      if (this.folders) {
        for (let folder of this.folders) {
          if (folder.name.match(re)) {
            this.folderExists = true;
            return;
          }
        }
        this.folderExists = false;
      }
    },
    cancelCopy: function () {
      this.$store.commit("toggleCopyFolderModal", false);
      this.$store.commit("setFolderName", "");
      this.folderName = "";
      this.tags = [];
    },
    replicateContainer: function () {
      // Initiate the container replication operation
      swiftCopyContainer(
        this.active.id,
        this.folderName,
        this.sourceProjectId ? this.sourceProjectId : this.active.id,
        this.selectedFolderName,
      ).then(async () => {
        await this.$store.dispatch("updateContainers", {
          projectID: this.$route.params.project,
          signal: null,
        });

        document.querySelector("#copyFolder-toasts").addToast(
          {
            type: "success",
            duration: 10000,
            persistent: false,
            progress: true,
            message: "",
            custom: true,
          },
        );

        let metadata = {
          usertags: this.tags.join(";"),
        };
        updateContainerMeta(this.active.id, this.folderName, metadata)
          .then(
            async () => {
              await this.$store.state.db.containers
                .where({
                  projectID: this.active.id,
                  name: this.folderName,
                })
                .modify({ tags: this.tags });
            },
          );
        delay(() => {
          this.$store.commit("setFolderCopiedStatus", true);
        }, 10000);

        this.$store.commit("toggleCopyFolderModal", false);
        this.cancelCopy();
      }).catch(() => {
        document.querySelector("#copyFolder-toasts").addToast(
          {
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

@media screen and (max-width: 773px), (max-height: 580px) {
   .copy-folder {
    top: -5rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 773px),
(max-width: 533px) {
  .copy-folder {
    top: -9rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 533px) {
  .copy-folder {
    top: -13rem;
   }
 }

c-card-content {
  color: var(--csc-dark-grey);
  padding: 0;
}

c-card-actions {
  padding: 0;
}

c-card-actions > c-button {
  margin: 0;
}
</style>
