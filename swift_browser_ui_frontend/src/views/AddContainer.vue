<template>
  <div 
    id="addview"
    class="contents"
  >
    <h1 class="title is-3 addcontainerhead">
      {{ 
        create 
          ? $t('message.container_ops.addContainer') 
          : $t('message.container_ops.editContainer') + container
      }}
    </h1>
    <b-message type="is-info">
      {{ $t('message.container_ops.norename') }}
    </b-message>
    <b-field
      horizontal
      :label="$t('message.container_ops.containerName')"
      :message="$t('message.container_ops.containerMessage')"
    >
      <b-input 
        v-model="container"
        name="container"
        expanded
        aria-required="true"
        :disabled="!create"
      />
    </b-field>
    <b-field
      horizontal
      :label="$t('message.tagName')"
      :message="$t('message.tagMessage')"
    >
      <b-taginput
        v-model="tags"
        ellipsis
        maxlength="20"
        icon="label"
        has-counter
        rounded
        type="is-primary"
        :confirm-keys="taginputConfirmKeys"
        :on-paste-separators="taginputConfirmKeys"
      />
    </b-field>

    <b-field
      horizontal
    >
      <p class="control">
        <b-button
          type="is-primary"
          class="addcontainerbutton"
          @click="create ? createContainer () : updateContainer ()"
        >
          {{ create ? $t('message.create') : $t('message.save') }}
        </b-button>
      </p>
    </b-field>
  </div>
</template>

<script>
import {
  swiftCreateContainer, 
  updateContainerMeta,
} from "@/common/api";
import {
  taginputConfirmKeys,
  getTagsForContainer,
} from "@/common/conv";

export default {
  name: "CreateContainer",
  data () {
    return {
      container: "",
      tags: [],
      create: true,
      taginputConfirmKeys,
    };
  },
  beforeMount () {
    if (this.$route.name === "EditContainer") {
      this.create = false;
      this.getContainer();
    }
  },
  methods: {
    createContainer: function () {
      swiftCreateContainer(this.container, this.tags.join(";")).then(() => {
        this.$store.state.db.containers.add({
          projectID: this.$store.state.active.id,
          name: this.container,
          tags: this.tags,
          count: 0,
          bytes: 0,
        });
        this.$router.go(-1);
      }).catch((err) => {

        if (err.message.match("Container name already in use")) {
          this.$buefy.toast.open({
            message: this.$t("message.error.inUse"),
            type: "is-danger",
          });
        }
        else if (err.message.match("Invalid container name")) {
          this.$buefy.toast.open({
            message: this.$t("message.error.invalidName"),
            type: "is-danger",
          });
        }
        else {
          this.$buefy.toast.open({
            message: this.$t("message.error.createFail"),
            type: "is-danger",
          });
        }
      });
    },
    getContainer: async function () {
      const containerName = this.$route.params.container;
      this.container = containerName;

      const container = await this.$store.state.db.containers.get({
        projectID: this.$store.state.active.id,
        name: this.container,
      });
      if (!container.tags) {
        this.tags = await getTagsForContainer(containerName);
      } else {
        this.tags = container.tags;
      }
    },
    updateContainer: function () {
      let meta = {
        usertags: this.tags.join(";"),
      };
      updateContainerMeta(this.container, meta).then(async () => {
        await this.$store.state.db.containers
          .where({
            projectID: this.$store.state.active.id,
            name: this.container,
          }).modify({tags: this.tags});
        this.$router.go(-1);
      });
    },
  },
};
</script>

<style scoped>
  #addview {
    width: auto;
    margin-left: 5%;
    margin-right: 5%;
  }
  .addcontainerhead {
    margin: 1% 1% 1% 0;
  }
  .addcontainerbutton {
    margin: 1%;
  }
</style>
