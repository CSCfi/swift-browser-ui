<template>
  <div 
    id="editObject"
    class="contents"
  >
    <h1 class="title is-3">
      {{ $t('message.objects.editObject') + object.name }}
    </h1>
    <b-message type="is-info">
      {{ $t('message.objects.norename') }}
    </b-message>
    <b-field
      :label="$t('message.objects.objectName')"
    >
      <b-input 
        v-model="object.name"
        name="object"
        expanded
        aria-required="true"
        disabled
      />
    </b-field>
    <b-field
      :label="$t('message.tagName')"
      :message="$t('message.tagMessage')"
    >
      <b-taginput
        v-model="object.tags"
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

    <b-field>
      <b-button
        type="is-primary"
        @click="updateObject ()"
      >
        {{ $t('message.save') }}
      </b-button>
    </b-field>
  </div>
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
  name: "EditObjectView",
  data () {
    return {
      container: {id: 0, name: ""},
      object: {id: 0, name: "", tags: []},
      taginputConfirmKeys,
    };
  },
  beforeMount () {
    this.getObject();
  },
  methods: {
    getObject: async function () {
      if(this.$route.name === "EditSharedObjectView") {
        this.container.name = this.$route.params.container;
        this.object.name = this.$route.params.object;
        this.$store.state.objectCache.map(obj => {
          if (obj.name === this.object.name) {
            this.object.tags = obj.tags;
          }
        });
      } else {
        this.container = await this.$store.state.db.containers.get({
          projectID: this.$store.state.active.id,
          name: this.$route.params.container,
        });
        this.object = await this.$store.state.db.objects.get({
          containerID: this.container.id,
          name: this.$route.params.object,
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
    updateObject: function () {
      let objectMeta = [
        this.object.name,
        {
          usertags: this.object.tags.join(";"),
        },
      ];
      updateObjectMeta(
        this.$route.params.project,
        this.container,
        objectMeta,
      ).then(async () => {
        if(this.$route.name === "EditObjectView") {
          await this.$store.state.db.objects
            .where(":id").equals(this.object.id)
            .modify({tags: this.object.tags});
        }
        this.$router.go(-1);
      });
    },
  },
};
</script>

<style scoped>
  #editObject {
    width: auto;
    margin-left: 5%;
    margin-right: 5%;
  }
  hi.title {
    margin: 1% 1% 1% 0;
  }
</style>
