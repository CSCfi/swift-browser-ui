<template>
  <div
    id="sharingview"
    class="contents"
  >
    <h3 class="title is-3 sharinghead">
      {{ $t('message.share.share') }}
    </h3>
    <b-field
      v-if="projects.length > 1"
      :label="$t('message.share.from_me')"
    >
      <b-select
        v-model="project"
        :placeholder="active.name"
      >
        <option
          v-for="item in projects"
          :key="item.id"
          :value="item.id"
        >
          {{ item.name }}
        </option>
      </b-select>
    </b-field>
    <b-field
      grouped
    >
      <b-switch
        v-model="read"
      >
        {{ $t('message.share.read_perm') }}
      </b-switch>
      <b-switch
        v-model="write"
      >
        {{ $t('message.share.write_perm') }}
      </b-switch>
    </b-field>
    <b-field
      :label="$t('message.share.container')"
    >
      <b-input 
        v-model="container"
        name="container"
        expanded
        aria-required="true"
      />
    </b-field>
    <b-field
      :label="$t('message.share.field_label')"
    >
      <b-taginput
        v-model="tags"
        :placeholder="$t('message.share.field_placeholder')"
      />
    </b-field>

    <b-field>
      <p class="control">
        <button
          class="button is-primary"
          @click="createAndShare ()"
        >
          {{ $t('message.share.share_cont') }}
        </button>
      </p>
    </b-field>
  </div>
</template>

<script>
import delay from "lodash/delay";
import {
  addAccessControlMeta,
  swiftCreateContainer,
  getSharedContainerAddress,
} from "@/common/api.js";

export default {
  name: "DirectShare",
  data () {
    return {
      container: "",
      tags: [],
      project: "",
      read: true,
      write: true,
    };
  },
  computed: {
    projects () {
      return this.$store.state.projects;
    },
    active () {
      return this.$store.state.active;
    },
  },
  watch: {
    read: function () {
      if(!this.read) {
        this.write = false;
      }
    },
    write: function () {
      if(this.write) {
        this.read = true;
      }
    },
  },
  beforeMount () {
    this.setActive(100);
    this.setParams(100);
    delay(this.checkMultiProject, 100, [200]);
  },
  methods: {
    createAndShare: function () {
      this.asyncCreateAndShare().then((ret) => {
        if (ret) {
          this.$router.push({
            name: "SharedFrom",
            params: {
              project: this.active.id,
            },
          });
        }
      });
    },
    asyncCreateAndShare: async function () {
      let rights = [];
      if (this.read) {
        rights.push("r");
      }
      if (this.write) {
        rights.push("w");
      }
      if (rights.length < 1) {
        this.$buefy.toast.open({
          duration: 5000,
          message: this.$t("message.share.fail_noperm"),
          type: "is-danger",
        });
      }
      // create the container
      await swiftCreateContainer(
        this.projects,
        this.container,
      );
      await addAccessControlMeta(
        this.project,
        this.container,
        rights,
        this.tags,
      );
      await this.$store.state.client.shareNewAccess(
        this.project,
        this.container,
        this.tags,
        rights,
        await getSharedContainerAddress(this.project),
      );
      return true;
    },
    setActive: function (wait) {
      try {
        this.project = this.active.id;
      } catch(ReferenceError) {
        delay(this.setActive, wait, [wait * 2]);
      }
    },
    setParams: function (wait) {
      try {
        this.container = this.$route.query.container;
        for (let uuid of this.$route.query.projects.split(",")) {
          this.tags.push(uuid);
        }
      } catch (ReferenceError) {
        delay(this.setParams, wait, [wait * 2]);
      }
    },
    checkMultiProject: function (wait) {
      try {
        if (this.projects.length == 1 && this.projects != undefined) {
          this.createAndShare();
        } else {
          this.$buefy.notification.open({
            indefinite: true,
            message: this.$t("message.request.multi_project"),
            type: "is-danger",
          });
        }
      } catch (ReferenceError) {
        delay(this.checkMultiProject, wait, [wait * 2]);
      }
    },
  },
};
</script>

<style scoped>
  #sharingview {
    width: auto;
    margin-left: 5%;
    margin-right: 5%;
  }
  .sharinghead {
    margin: 1% 1% 1% 0;
  }
</style>
