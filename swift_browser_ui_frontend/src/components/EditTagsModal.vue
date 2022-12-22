<template>
  <c-card class="edit-tags">
    <h3 class="title is-3 has-text-dark">
      {{ $t('message.objects.editObject') + object.name }}
    </h3>
    <c-card-content>
      <b-field
        custom-class="has-text-dark"
        :label="$t('message.tagName')"
      >
        <b-taginput
          v-model="object.tags"
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
        @click="toggleEditTagsModal"
      >
         {{ $t("message.cancel") }}
      </c-button>
      <c-button
        size="large"
        @click="saveTags"
      >
        {{ $t("message.save") }}
      </c-button>
    </c-card-actions>
  </c-card>
</template>

<script>
import {
  updateObjectMeta,
} from "@/common/api";
import {
  taginputConfirmKeys,
  getTagsForObjects,
} from "@/common/conv";

export default {
  name: "EditTagsModal",
  data() {
    return {
      object: {id: 0, name: "", tags: []},
      taginputConfirmKeys,
    };
  },
  computed: {
    selectedObjectName() {
      return this.$store.state.selectedObjectName.length > 0
        ? this.$store.state.selectedObjectName
        : "";
    },
  },
  watch: {
    selectedObjectName: function () {
      if (this.selectedObjectName && this.selectedObjectName.length > 0) {
        this.getObject();
      }
    },
  },
  methods: {
    getObject: async function () {
      if (this.$route.name === "SharedObjects") {
        this.container.name = this.$route.params.container;
        this.object.name = this.selectedObjectName;
        this.$store.state.objectCache.map(obj => {
          if (obj.name === this.object.name) {
            this.object.tags = obj.tags;
          }
        });
      } else {
        this.container = await this.$store.state.db.containers.get({
          projectID: this.$route.params.project,
          name: this.$route.params.container,
        });
        this.object = await this.$store.state.db.objects.get({
          containerID: this.container.id,
          name: this.selectedObjectName,
        });
      }

      if (!this.object.tags.length) {
        const tags = await getTagsForObjects(
          this.$route.params.project,
          this.container.name,
          [this.object.name],
        );
        this.tags = tags[0][1] || [];
      } else {
        this.tags = this.object.tags;
      }
    },
    toggleEditTagsModal: function () {
      this.$store.commit("toggleEditTagsModal", false);
      this.$store.commit("setObjectName", "");
    },
    saveTags: function () {
      let objectMeta = [
        this.object.name,
        {
          usertags: this.object.tags.join(";"),
        },
      ];
      updateObjectMeta(
        this.$route.params.project,
        this.container.name,
        objectMeta,
      ).then(async () => {
        if (this.$route.name !== "SharedObjects") {
          await this.$store.state.db.objects
            .where(":id").equals(this.object.id)
            .modify({tags: this.object.tags});
        }
        this.toggleEditTagsModal();
      });
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

.edit-tags {
  padding: 3rem;
  position: absolute;
  top: -1rem;
  left: 0;
  right: 0;
  max-height: 75vh;
}


c-card-content {
  color: var(--csc-dark-grey);
  padding: 0;
}

c-card-actions {
  padding: 0;
}

</style>
