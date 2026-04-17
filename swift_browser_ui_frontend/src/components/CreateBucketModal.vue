<template>
  <c-card
    ref="createBucketContainer"
    class="modal-card"
    data-testid="create-bucket-modal"
    @keydown="handleKeyDown"
  >
    <div
      id="createBucket-modal-content"
      class="modal-content-wrapper"
    >
      <c-toasts
        id="createModal-toasts"
        data-testid="createModal-toasts"
        vertical="bottom"
        absolute
      />
      <c-card-content class="modal-card-content">
        <h2 class="title is-4">
          {{ $t("message.container_ops.addContainer") }}
        </h2>
        <p class="info-text">
          {{ $t("message.encrypt.uploadStep1.nonModifiable") }}
        </p>
        <c-text-field
          id="newBucket-input"
          v-model="bucketName"
          v-control
          :label="$t('message.container_ops.bucketName')"
          name="bucketname"
          aria-required="true"
          data-testid="bucket-name"
          hide-details
          required
          trim-whitespace
          @changeValue="checkBucketName"
        />
        <BucketNameValidation
          :result="validationResult"
        />
        <!--<label
          class="taginput-label"
          label-for="create-bucket-taginput"
        >
          {{ $t('message.tagName') }}
        </label>
        <TagInput
          id="create-bucket-taginput"
          :tags="tags"
          data-testid="bucket-tag"
          @addTag="addingTag"
          @deleteTag="deletingTag"
        />-->
        <p class="info-text is-6">
          {{ $t("message.container_ops.createdBucket") }}
          <b>{{ active.name }}</b>.
        </p>
        <c-link
          :href="projectInfoLink"
          underline
          target="_blank"
        >
          {{ $t("message.container_ops.viewProjectMembers") }}
          <c-icon :path="mdiOpenInNew" />
        </c-link>
      </c-card-content>
    </div>
    <c-card-actions justify="space-between">
      <c-button
        outlined
        size="large"
        data-testid="cancel-save-bucket"
        @click="toggleCreateBucketModal"
        @keyup.enter="toggleCreateBucketModal"
      >
        {{ $t("message.cancel") }}
      </c-button>
      <c-button
        size="large"
        data-testid="save-bucket"
        @click="() => createContainer()"
        @keyup.enter="() => createContainer()"
      >
        {{ $t("message.save") }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import { mdiOpenInNew } from "@mdi/js";
import { getDB } from "@/common/idb";

import {
  DEV,
  addNewTag,
  deleteTag,
  getProjectNumber,
  validateBucketName,
  getCurrentISOtime,
  tokenize,
} from "@/common/globalFunctions";
import { captureKeyboardNavInsideModal } from "@/common/keyboardNavigation";
// import TagInput from "@/components/TagInput.vue";
import BucketNameValidation from "./BucketNameValidation.vue";

import { toRaw } from "vue";
import { debounce } from "lodash";
import { awsAddBucketCors, awsCreateBucket } from "@/common/api";

export default {
  name: "CreateBucketModal",
  components: {
    //TagInput,
    BucketNameValidation,
  },
  data() {
    return {
      mdiOpenInNew,
      bucketName: "",
      tags: [],
      projectInfoLink: "",
      validationResult: {},
      containers: [],
    };
  },
  computed: {
    active() {
      return this.$store.active;
    },
    uname() {
      return this.$store.uname;
    },
    controller() {
      return new AbortController();
    },
    prevActiveEl() {
      return this.$store.prevActiveEl;
    },
    modalVisible() {
      return this.$store.openCreateBucketModal;
    },
  },
  watch: {
    active: function () {
      this.projectInfoLink = this.$t("message.supportMenu.projectInfoBaseLink")
        + getProjectNumber(this.active);
    },
    modalVisible: async function() {
      if (this.modalVisible) {
        this.containers = await getDB().containers
          .where({ projectID: this.active.id })
          .toArray();
      }
    },
  },
  methods: {
    checkBucketName: debounce(async function () {
      this.validationResult = await validateBucketName(
        this.bucketName);
    }, 300),
    createContainer: async function () {
      this.validationResult = await validateBucketName(
        this.bucketName);
      const validationError =
        Object.values(this.validationResult).some(val => !val);
      if (validationError) return;

      let projectID = this.$route.params.project;
      const bucketName = toRaw(this.bucketName);
      //const tags = toRaw(this.tags);

      let resp = await awsCreateBucket(projectID, bucketName);
      let errorMessage = this.$t("message.error.createFail");
      switch (resp) {
        case 409:
          errorMessage = this.$t("message.error.inUseOtherPrj");
          break;
        case 400:
          errorMessage = this.$t("message.error.invalidName");
          break;
      }

      if (resp.status != 204) {
        document.querySelector("#createModal-toasts").addToast(
          {
            id: "create-toast",
            progress: false,
            type: "error",
            message: errorMessage,
          },
        );
        return;
      }

      // We won't get the timestamp immediately from the backend with S3
      // Let's just assume current time :)
      // Seen below as the bare getCurrentISOtime() call.

      let newBucket = {
        name: bucketName,
        bytes: 0,
        count: 0,
        created: getCurrentISOtime(),
        last_modified: getCurrentISOtime(),
        projectID: projectID,
      };

      try {
        await awsAddBucketCors(projectID, bucketName);
        newBucket.cors_added = true;
      } catch (e) {
        if (DEV) {
          console.error(
            `Failed to update CORS for the new bucket ${bucketName}`,
          );
        }
        newBucket.cors_added = false;
      } finally {
        await getDB().containers.add(newBucket);
      }

      this.toggleCreateBucketModal();

      this.$router.push({
        name: "AllBuckets",
        params: {
          project: this.active.id,
          user: this.uname,
        },
      });

      this.$store.setNewBucket(bucketName);
    },
    toggleCreateBucketModal: function () {
      this.$store.toggleCreateBucketModal(false);
      this.bucketName = "";
      this.tags = [];
      this.create = true;
      this.validationResult = {};
      document.querySelector("#createModal-toasts").removeToast("create-toast");
    },
    addingTag: function (e, onBlur) {
      this.tags = addNewTag(e, this.tags, onBlur);
    },
    deletingTag: function (e, tag) {
      this.tags = deleteTag(e, tag, this.tags);
    },
    handleKeyDown: function (e) {
      captureKeyboardNavInsideModal(e, this.$refs.createBucketContainer);
    },
  },
};
</script>

<style scoped>

c-card-actions {
  padding: 0;
}

c-card-actions > c-button {
  margin: 0;
}

c-link {
  margin-top: -1rem;
}


</style>
