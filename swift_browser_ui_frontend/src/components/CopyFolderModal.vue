<template>
  <c-card class="copy-folder">
    <h3 class="title is-3 has-text-dark">
      {{
        $t("message.replicate.copy_folder") + selectedFolderName
      }}
    </h3>
    <c-card-content>
      <c-alert v-show="folderExists" type="warning">
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
    <c-card-actions justify="space-between">
      <c-button
        outlined
        size="large"
        @click="cancelCopy"
      >
        Cancel
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

import escapeRegExp from "lodash/escapeRegExp";
import { useObservable } from "@vueuse/rxjs";
import { liveQuery } from "dexie";

export default {
  name: "CopyFolderModal",
  data() {
    return {
      folderExists: true,
      folderName: "",
      tags: [],
      taginputConfirmKeys,
      folders: { value: [] },
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
  },
  watch: {
    selectedFolderName: function () {
      if (this.selectedFolderName && this.selectedFolderName.length > 0) {
        this.folderName = this.selectedFolderName;
        this.fetchFolders().then(() => this.checkSelectedFolder());
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
    checkSelectedFolder: function () {
      // request parameter should be sanitized first
      const safeKey = escapeRegExp(this.folderName).trim();
      let re = new RegExp("^".concat(safeKey, "$"));

      if (this.folders.value) {
        for (let folder of this.folders.value) {
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
        this.active.id,
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

h3 {
  margin: 0 !important;
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
