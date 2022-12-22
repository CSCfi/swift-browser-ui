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
        class="navbar-item"
      >
        {{ $t("message.currentProj") }}: &nbsp;<span>
          {{ active.name }}
        </span>
      </div>
      <div class="navbar-item">
        <c-button
          ghost
          data-testid="copy-projectId"
          @click="copyProjectId"
        >
          <i
            slot="icon"
            class="mdi mdi-content-copy"
          />
          {{ $t("message.copy") }} {{ $t("message.share.share_id") }}
        </c-button>
        <div class="tooltip">
          <c-icon-button text>
            <i class="mdi mdi-information-outline" />
          </c-icon-button>
          <span class="tooltip-content">
            {{ $t("message.share.share_id_tooltip") }}
          </span>
        </div>

      </div>
      <c-toasts
        id="copy-toasts"
        vertical="center"
        data-testid="copy-toasts"
      />
      <c-spacer />
      <div class="navbar-item">
        <c-button
          outlined
          data-testid="create-folder"
          @click="toggleCreateFolderModal"
        >
          {{ $t("message.createFolder") }}
        </c-button>
      </div>
      <div class="navbar-item">
        <c-button @click="toggleUploadModal">
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
export default {
  name: "BrowserSecondaryNavbar",
  props: ["multipleProjects", "projects"],
  data: function () {
    return {
      copy: false,
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
        duration: 3000,
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
          setTimeout(() => { this.copy = false; }, 3000);
        },() => {
          document.querySelector("#copy-toasts").addToast(
            { ...toastMessage,
              type: "error",
              message: this.$t("message.copy_failed")},
          );
        });
      }
    },
    hoverTooltip: function () {
      console.log("HOVER!");
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
  }

  c-toasts {
    width: fit-content;
  }

  .select-project {
    min-width: 15rem;
    flex: 0.5;
  }

  c-select {
    flex: 1;
  }

  @media screen and (max-width: 767px) {
    .select-project {
      width: 100%;
      flex: auto;
    }
  }

  .tooltip {
    position: relative;
    display: inline-block;
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

    /* Position the tooltip */
    position: absolute;
    z-index: 1;
    top: 120%;
    left: 50%;
    margin-left: -10rem;
  }

  .tooltip:hover .tooltip-content {
    visibility: visible;
  }

  .tooltip-content::before {
    content: " ";
    position: absolute;
    left: 46%;
    bottom: 100%;
    width: 0;
    height: 0;
    border: 0.7rem solid transparent;
    border-bottom-color: $csc-primary;
  }
  .tooltip-content::after {
    content: " ";
    position: absolute;
    left: 50%;
    bottom: 100%;
    width: 0;
    height: 0;
    margin-left: -0.75rem;
    border: 0.65rem solid transparent;
    border-bottom-color: $white;
  }

  </style>
