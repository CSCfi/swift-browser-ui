<template>
  <c-card
    ref="copyBucketContainer"
    class="copy-bucket"
    @keydown="handleKeyDown"
  >
    <div class="modal-content-wrapper">
      <h2 class="title is-4">
        {{
          $t("message.replicate.copy") + selectedBucketName
        }}
      </h2>
      <c-card-content>
        <div id="bucket-name-wrapper">
          <c-text-field
            id="new-copy-bucketName"
            v-model="bucketName"
            v-csc-control
            :label="$t('message.replicate.name')"
            name="bucketname"
            aria-required="true"
            trim-whitespace
            required
          />
          <BucketNameValidation
            :result="validationResult"
          />
          <c-loader v-show="loadingBucketname" />
        </div>
        <!--<label
          class="taginput-label"
          label-for="copy-bucket-taginput"
        >
          {{ $t('message.tagName') }}
        </label>
        <TagInput
          id="copy-bucket-taginput"
          :tags="tags"
          @addTag="addingTag"
          @deleteTag="deletingTag"
        />-->
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
  copyBucket,
  updateContainerMeta,
  getObjects,
} from "@/common/api";
import { getDB } from "@/common/db";

import {
  addNewTag,
  deleteTag,
  validateBucketName,
} from "@/common/globalFunctions";
import {
  getFocusableElements,
  moveFocusOutOfModal,
  keyboardNavigationInsideModal,
} from "@/common/keyboardNavigation";
import { useObservable } from "@vueuse/rxjs";
import { liveQuery } from "dexie";
//import TagInput from "@/components/TagInput.vue";
import BucketNameValidation from "./BucketNameValidation.vue";
import { toRaw } from "vue";

export default {
  name: "CopyBucketModal",
  components: {
    //TagInput,
    BucketNameValidation,
  },
  data() {
    return {
      bucketName: "",
      loadingBucketname: true,
      tags: [],
      buckets: [],
      checkpointsCompleted: 0,
      validationResult: {},
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
    selectedBucketName() {
      return this.$store.state.selectedBucketName.length > 0
        ? this.$store.state.selectedBucketName
        : "";
    },
    sourceProjectId() {
      return this.$store.state.sourceProjectId;
    },
    visible() {
      return this.$store.state.openCopyBucketModal;
    },
  },
  watch: {
    visible: function () {
      if (this.visible) {
        if (this.selectedBucketName && this.selectedBucketName.length > 0) {
          this.fetchBuckets().then(() => {
            if(this.buckets && this.buckets.length > 0) {
              this.getCopyBucket(this.selectedBucketName);
            }
          });
        }
      }
    },
    bucketName() {
      if (this.bucketName) {
        this.checkValidity();
      }
    },
    checkpointsCompleted() {
      if (this.checkpointsCompleted > 1) {
        this.$store.commit("setBucketCopiedStatus", true);
        document.querySelector("#copyBucket-toasts")
          .removeToast("copy-in-progress");
      }
    },
  },
  methods: {
    fetchBuckets: async function () {
      if (
        this.active.id === undefined &&
        this.$route.params.project === undefined
      ) {
        return;
      }
      this.buckets = useObservable(
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
    getCopyBucket: function (origBucketName) {
      if (this.buckets) {
        // Check if current bucket is a copy
        const copySuffix = new RegExp("-(copy)-(\\d+)$", "i");
        const hasCopySuffix = origBucketName.match(copySuffix);

        // Use a var to keep the bucket as a copy name without copy version
        let newBucketName = hasCopySuffix ?
          `${origBucketName.slice(0, hasCopySuffix["index"])}-copy` : `${origBucketName}-copy`;

        const existingCopiedBuckets = [];
        for (let bucket of this.buckets) {
          // Check if bucket is one of the copy versions
          // which ends in the form 'copy + number'
          const copiedReg = new RegExp(`^${newBucketName}-(\\d+)$`, "i");
          bucket.name.match(copiedReg) ?
            existingCopiedBuckets.push(bucket.name) : null;
        }

        let nextVersion = 1;
        if (existingCopiedBuckets.length > 0) {
          // Sort the array in asc, the last item is the latest copy
          // then extract the copy version from it
          existingCopiedBuckets.sort();
          const latestVer = existingCopiedBuckets[
            existingCopiedBuckets.length-1].match(copySuffix);
          nextVersion = +latestVer[2] + 1;
        }
        this.bucketName = `${newBucketName}-${nextVersion}`;
        this.loadingBucketname = false;
      }
    },
    cancelCopy: function (keypress) {
      this.$store.commit("toggleCopyBucketModal", false);
      this.$store.commit("setBucketName", "");
      this.bucketName = "";
      this.tags = [];
      this.loadingBucketname = true;
      this.validationResult = {};
      document.querySelector("#copyBucket-toasts").removeToast("copy-error");

      /*
        Prev Active element is a popup menu and it is removed from DOM
        when we click it to open Copy Modal.
        Therefore, we need to make its focusable parent
        to be focused instead after we close the modal.
      */
      if (keypress) {
        const prevActiveElParent = document.getElementById("container-table");
        moveFocusOutOfModal(prevActiveElParent, true);
      }
    },
    replicateContainer: async function (keypress) {
      this.validationResult = await validateBucketName(
        this.bucketName);
      const validationError =
        Object.values(this.validationResult).some(val => !val);
      if (validationError) return;

      this.a_replicate_container(keypress).then(() => {});
    },
    a_replicate_container: async function (keypress) {
      this.$store.commit("toggleCopyBucketModal", false);
      document.querySelector("#copyBucket-toasts").addToast(
        {
          id: "copy-in-progress",
          type: "success",
          indeterminate: true,
          message: "",
          custom: true,
        },
      );

      await copyBucket(
        this.active.id,
        this.bucketName,
        this.selectedBucketName,
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
        delay((id, bucket, meta, tgs) => {
          updateContainerMeta(id, bucket, meta)
            .then(
              async () => {
                await getDB().containers
                  .where({
                    projectID: id,
                    name: bucket,
                  })
                  .modify({ tgs });
              },
            );

          this.checkpointsCompleted++;
        }, 5000, this.active.id, this.bucketName, metadata, tags);

        getObjects(
          this.sourceProjectId ? this.sourceProjectId : this.active.id,
          this.selectedBucketName,
        ).then(async (objects) => {
          const sleep =
            time => new Promise(resolve => setTimeout(resolve, time));

          let copiedObjects = undefined;
          while (copiedObjects === undefined ||
            copiedObjects.length < objects.length) {
            const task = getObjects(this.active.id, this.bucketName)
              .then((obj) => copiedObjects = obj );

            await Promise.all([task, sleep(2000)]);
          }

          this.checkpointsCompleted++;
          this.cancelCopy(keypress);
        });
      }).catch(() => {
        document.querySelector("#copyBucket-toasts").addToast(
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
    checkValidity: debounce(async function () {
      this.validationResult = await validateBucketName(
        this.bucketName);
    }, 300, { leading: true }),
    handleKeyDown: function (e) {
      const focusableList = this.$refs.copyBucketContainer.querySelectorAll(
        "input, c-icon, c-button",
      );
      const { first, last } = getFocusableElements(focusableList);
      keyboardNavigationInsideModal(e, first, last);
    },
  },
};
</script>

<style lang="scss" scoped>

.copy-bucket {
  padding: 3rem;
  position: absolute;
  top: -1rem;
  left: 0;
  right: 0;
  max-height: 75vh;
}

@media screen and (max-width: 767px), (max-height: 580px) {
   .copy-bucket {
    top: -5rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 767px),
(max-width: 525px) {
  .copy-bucket {
    top: -9rem;
  }
}

@media screen and (max-height: 580px) and (max-width: 525px) {
  .copy-bucket {
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

#bucket-name-wrapper {
  position: relative;
  padding-top: 0.5rem;
}

</style>
