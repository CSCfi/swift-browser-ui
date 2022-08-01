<template>
  <c-menu
    simple
    :items.prop="menuItems"
  >
    <c-button
      class="menu-trigger-button"
      text
      tabindex="-1"
      :inverted="selected"
    >
      ... {{ $t('message.options') }}
    </c-button>
  </c-menu>
</template>

<script>
import {swiftDeleteContainer} from "@/common/api";
import { toggleCreateFolderModal } from "@/common/globalFunctions";
export default {
  name: "FolderOptionsMenu",
  props: ["props", "selected"],
  data: function () {
    return {
      menuItems: [
        {
          name: this.$t("message.editTags"), 
          action: () => toggleCreateFolderModal(this.props.row.name),
        },
        {
          name: this.$t("message.delete"), 
          action: () => this.confirmDelete(
            this.props.row.name, this.props.row.count,
          ),
        },
      ],
    };
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
  },
};
</script>

<style scoped>
/* Default button click event prevents menu from triggering */
  .menu-trigger-button {
    pointer-events: none; 
  }
</style>