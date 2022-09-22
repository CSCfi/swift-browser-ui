<template>
  <c-menu
    simple
    :items.prop="menuItems.map(item => ({name: $t(item.key), ...item}))"
  >
    <c-button
      class="menu-trigger-button"
      text
      tabindex="-1"
      :inverted="selected"
    >
      <i class="mdi mdi-dots-horizontal" /> {{ $t('message.options') }}
    </c-button>
  </c-menu>
</template>

<script>
import {swiftDeleteContainer} from "@/common/api";
import {
  toggleCreateFolderModal,
  toggleCopyFolderModal,
} from "@/common/globalFunctions";

export default {
  name: "FolderOptionsMenu",
  props: ["props", "selected"],
  data: function () {
    return {
      menuItems: [
        {
          key: "message.copy",
          action: () => toggleCopyFolderModal(this.props.row.name),
          disabled: !this.props.row.bytes ? true : false,
        },
        {
          key: "message.editTags",
          action: () => toggleCreateFolderModal(this.props.row.name),
        },
        {
          key: "message.delete",
          action: () => this.confirmDelete(
            this.props.row.name, this.props.row.count,
          ),
        },
      ],
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
  },
  methods: {
    confirmDelete: function (container, objects) {
      if (objects > 0) {
        this.$buefy.notification.open({
          message: "Deleting a container requires deleting all objects first.",
          type: "is-danger",
          position: "is-top-right",
          duration: 30000,
          hasIcon: true,
        });
        this.$router.push(
          this.$route.params.project
            + "/"
            + container,
        );
      } else {
        this.$buefy.dialog.confirm({
          title: this.$t("message.container_ops.deleteConfirm"),
          message: this.$t("message.container_ops.deleteConfirmMessage"),
          confirmText: this.$t("message.container_ops.deleteConfirm"),
          type: "is-danger",
          hasIcon: true,
          onConfirm: () => {this.deleteContainer(container);},
        });
      }
    },
    deleteContainer: function(container) {
      this.$buefy.toast.open({
        message: this.$t("message.container_ops.deleteSuccess"),
        type: "is-success",
      });
      const projectID = this.$store.state.active.id;
      swiftDeleteContainer(
        projectID,
        container,
      ).then(async () => {
        await this.$store.state.db.containers
          .where({
            projectID,
            name: container,
          })
          .delete();
      });
    },
    getProject: function () {
      if(this.$route.params.user == undefined) {
        return this.$props.project ? this.$props.project :
          this.$route.params.project;
      }
      return this.active.id;
    },
    getFrom: function() {
      if (this.$props.from != undefined) {
        return this.$props.from;
      }
      return this.active.id;
    },
    getContainer: function () {
      return this.props.row.name ? this.props.row.name :
        this.$route.params.container;
    },
  },
};
</script>

<style scoped>
/* Default button click event prevents menu from triggering */
  .menu-trigger-button {
    pointer-events: none;
  }

 .mdi:before {
    margin-top: 0.5rem;
  }
</style>