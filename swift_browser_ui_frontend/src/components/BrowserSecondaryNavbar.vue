<template>
  <div id="secondary-navbar">
    <div class="container is-fluid">
      <div
        v-if="multipleProjects"
        class="navbar-item select-project"
      >
        <c-select
          v-bind="active"
          c-control
          :items.prop="mappedProjects"
          :label="$t('message.selectProj')"
          placeholder="Select project"
          return-value
          hide-details
          data-testid="project-selector"
          @changeValue="changeActive($event)"
        />
      </div>
      <div
        v-if="!multipleProjects"
        class="navbar-item column"
      >
        <p class="label">
          {{ $t("message.currentProj") }}
        </p>
        <p class="project-number">
          {{ active.name }}
        </p>
      </div>
      <div class="navbar-item">
        <c-button
          ghost
          data-testid="copy-projectId"
          :aria-label="$t('label.copyshareid')"
          @click="copyProjectId"
          @keyup.enter="copyProjectId"
        >
          <i
            slot="icon"
            class="mdi mdi-content-copy"
          />
          {{ $t("message.copy") }} {{ $t("message.share.share_id") }}
        </c-button>
        <div
          class="tooltip"
          role="tooltip"
          :aria-label="$t('label.shareid_tooltip')"
        >
          <c-icon
            :path="path"
            tabindex="0"
          />
          <!-- eslint-disable vue/no-v-html -->
          <span
            id="shareid-tooltip-content"
            class="tooltip-content"
            role="tootip"
            v-html="$t('message.share.share_id_tooltip')"
          />
          <!-- eslint-enable vue/no-v-html -->
        </div>
      </div>
      <c-toasts
        id="copy-toasts"
        vertical="center"
        data-testid="copy-toasts"
      />
      <c-toasts
        id="refresh-toasts"
        data-testid="refresh-toasts"
      >
        <p>{{ $t("message.encrypt.enReady") }}</p>
        <c-button
          text
          @click="handleRefreshClick"
        >
          {{ $t("message.encrypt.refresh") }}
        </c-button>
      </c-toasts>
      <c-spacer />
      <div class="navbar-item">
        <c-button
          outlined
          data-testid="create-folder"
          @click="toggleCreateFolderModal"
          @keyup.enter="toggleCreateFolderModal"
        >
          {{ $t("message.createFolder") }}
        </c-button>
      </div>
      <div class="navbar-item">
        <c-button
          @click="toggleUploadModal"
          @keyup.enter="toggleUploadModal"
        >
          {{ $t("message.uploadSecondaryNav") }}
        </c-button>
      </div>
    </div>
  </div>
</template>

<script>
import {
  toggleCreateFolderModal,
  modifyBrowserPageStyles,
} from "@/common/globalFunctions";
import { mdiInformationOutline } from "@mdi/js";

export default {
  name: "BrowserSecondaryNavbar",
  props: ["multipleProjects", "projects"],
  data: function () {
    return {
      copy: false,
      path: mdiInformationOutline,
    };
  },
  computed: {
    active() {
      const activeObject = this.$store.state.active;
      return { ...activeObject, value: activeObject.id };
    },
    uname() {
      return this.$store.state.uname;
    },
    // C-select component handles options by name and value props
    // Append value-prop to projects
    mappedProjects() {
      return this.projects.map(project => ({ ...project, value: project.id }));
    },
  },
  methods: {
    changeActive(event) {
      const item = event.target.value;
      if (item.id !== this.active.id) {
        const navigationParams = {
          name: "AllFolders",
          params: {user: this.uname, project: item.id},
        };
        // Pushing to router before ´go´ method
        // enables navigation with updated item id
        this.$router.push(navigationParams);
        this.$router.go(navigationParams);
      }
    },
    toggleCreateFolderModal: function (folderName) {
      toggleCreateFolderModal(folderName);
    },
    toggleUploadModal: function () {
      this.$store.commit("toggleUploadModal", true);
      modifyBrowserPageStyles();
    },
    copyProjectId: function () {
      const toastMessage = {
        duration: 6000,
        persistent: false,
        progress: false,
      };
      if (!this.copy) {
        navigator.clipboard.writeText(this.active.id).then(() => {
          this.copy = true;
          document.querySelector("#copy-toasts").addToast(
            { ...toastMessage,
              type: "success",
              message: this.$t("message.copied")},
          );
          // avoid multiple clicks of copy button
          // that can stack up the toasts
          // by setting the value for 'copy'
          setTimeout(() => { this.copy = false; }, 6000);
        },() => {
          document.querySelector("#copy-toasts").addToast(
            { ...toastMessage,
              type: "error",
              message: this.$t("message.copy_failed")},
          );
        });
      }
    },
    handleRefreshClick: function() {
      document.querySelector("#refresh-toasts").removeToast("refresh-toast");
      location.reload();
    },
  },
};
</script>

<style scoped lang="scss">
  @import "@/css/prod.scss";

  #secondary-navbar {
    border-bottom: 6px solid $csc-primary-light;
  }

  .container {
    display: flex;
    padding: 0.5rem 1rem !important;
    flex-wrap: wrap;
  }

  .navbar-item {
    height: 100%;
    align-self: center;
  }

  c-toasts {
    width: fit-content;
  }

  .select-project, .column {
    min-width: 15rem;
    flex: 0.5;
  }

  c-select {
    flex: 1;
  }

  @media screen and (max-width: 767px) {
    .select-project, .column {
      width: 100%;
      flex: auto;
    }
  }

  .tooltip {
    position: relative;
    display: inline-block;
  }

  c-icon {
    margin-left: 0.5rem;
  }

  .tooltip-content {
    visibility: hidden;
    text-align: left;
    width: 20rem;
    background-color: $white;
    color: $text;
    border: 1px solid $csc-primary;
    border-radius: 0.375rem;
    padding: 1rem;
    font-size: 14px;
    line-height: 16px;

    /* Position the tooltip */
    position: absolute;
    z-index: 5;
    top: 150%;
    left: 50%;
    margin-left: -10rem;
  }

  .tooltip:hover .tooltip-content, .tooltip:focus-within .tooltip-content {
    visibility: visible;
  }

  .tooltip-content::before {
    content: " ";
    position: absolute;
    left: 48%;
    bottom: 100%;
    width: 0;
    height: 0;
    border: 0.7rem solid transparent;
    border-bottom-color: $csc-primary;
  }
  .tooltip-content::after {
    content: " ";
    position: absolute;
    left: 52%;
    bottom: 100%;
    width: 0;
    height: 0;
    margin-left: -0.75rem;
    border: 0.65rem solid transparent;
    border-bottom-color: $white;
  }

  .column {
    flex-direction: column;
    padding: 0 0 0 1.5rem;
    color: var(--csc-dark-grey);
  }

  .project-number {
    font-size: 0.875rem;
  }

  .label {
    font-weight: 400;
    font-size: 0.75rem;
  }
  </style>
