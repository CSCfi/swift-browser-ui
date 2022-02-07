<template>
  <div 
    id="editObject"
    class="contents"
  >
    <h1 class="title is-3">
      {{ $t('message.objects.editObject') + object }}
    </h1>
    <b-message type="is-info">
      {{ $t('message.objects.norename') }}
    </b-message>
    <b-field
      :label="$t('message.objects.objectName')"
    >
      <b-input 
        v-model="object"
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
      container: "",
      object: "",
      tags: [],
      taginputConfirmKeys,
    };
  },
  beforeMount () {
    this.getObject();
  },
  methods: {
    getObject: async function () {
      const containerName = this.$route.params.container;
      const objectName = this.$route.params.object;
      this.container = containerName;
      this.object = objectName;

      const tags = this.$store.state.objectTagsCache[objectName];
      if (!tags) {
        const tags = await getTagsForObjects(containerName, [objectName]);
        this.tags = tags[0][1] || [];
      } else {
        this.tags = tags;
      }
    },
    updateObject: function () {
      let objectMeta = [
        this.object,
        {
          usertags: this.tags.join(";"),
        },
      ];
      updateObjectMeta(this.container, objectMeta).then(() => {
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
