<template>
  <c-card class="copy-folder">
    <div class="modal-content-wrapper">
      <h4 class="title is-4 has-text-dark">
        {{
          $t("message.replicate.copy_folder") + selectedFolderName
        }}
      </h4>
      <c-card-content>
        <c-alert
          v-show="folderExists"
          type="warning"
        >
          <p class="has-text-dark">
            {{ $t("message.replicate.destinationExists") }}
          </p>
        </c-alert>
        <b-field
          custom-class="has-text-dark"
          :label="$t('message.replicate.name_newFolder')"
        >
          <b-input
            v-model="folderName"
            name="foldername"
            custom-class="has-text-dark"
          />
        </b-field>
        <b-field
          custom-class="has-text-dark"
          :label="$t('message.tagName')"
        >
          <b-taginput
            v-model="tags"
            ellipsis
            maxlength="20"
            has-counter
            rounded
            type="is-primary"
            :placeholder="$t('message.tagPlaceholder')"
            :confirm-keys="taginputConfirmKeys"
            :on-paste-separators="taginputConfirmKeys"
          />
        </b-field>
      </c-card-content>
    </div>
    <c-card-actions justify="space-between">
      <c-button
        outlined
        size="large"
        @click="cancelCopy"
      >
        {{ $t("message.cancel") }}
      </c-button>
      <c-button
        size="large"
        :disabled="folderExists"
        @click="replicateContainer"
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
  taginputConfirmKeys,
  updateContainerMeta,
} from "@/common/api";

import { modifyBrowserPageStyles } from "@/common/globalFunctions";
import escapeRegExp from "lodash/escapeRegExp";
import { useObservable } from "@vueuse/rxjs";
import { liveQuery } from "dexie";

export default {
  name: "CopyFolderModal",
  data() {
    return {
      folderExists: false,
      folderName: "",
      tags: [],
      taginputConfirmKeys,
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
          this.getCopyFolder(this.selectedFolderName);
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
      if (this.folders.value) {
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
        for (let folder of this.folders.value) {
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
        }
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
      modifyBrowserPageStyles();
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
  },
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

.copy-folder {
  padding: 3rem;
  position: absolute;
  top: -1rem;
  left: 0;
  right: 0;
  max-height: 75vh;
}

@media screen and (max-height: 720px), (max-width: 992px ) {
  .copy-folder {
    max-height: 50vh;
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
