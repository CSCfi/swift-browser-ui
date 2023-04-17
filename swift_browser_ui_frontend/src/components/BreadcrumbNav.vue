
<template>
  <div class="breadcrumb">
    <c-row
      align="center"
    >
      <c-link
        :href="home.path"
        color="primary"
        :path="mdiHome"
        icon-fill="primary"
        icon-after="false"
        :weight="defaultWeight"
      >
        {{ home.title }}
      </c-link>

      <c-link
        :href="folderPath"
        color="primary"
        :path="mdiChevronRight"
        icon-fill="primary"
        icon-after="false"
        :weight="subfolders === '' ? lastWeight : defaultWeight"
      >
        {{ folder }}
      </c-link>
      <c-link
        v-for="item, i in subfolders"
        :key="item"
        :href="getPath(i)"
        color="primary"
        :path="mdiChevronRight"
        icon-fill="primary"
        icon-after="false"
        :weight="i === subfolders.length-1 ? lastWeight: defaultWeight"
      >
        {{ item }}
      </c-link>
    </c-row>
  </div>
</template>

<script>
import { mdiHome, mdiChevronRight } from "@mdi/js";

export default {
  name: "BreadcrumbNav",
  props: ["sharedFrom", "sharedTo"],
  data() {
    return {
      lastWeight: 700,
      defaultWeight: 400,
      mdiHome,
      mdiChevronRight,
    };
  },
  computed: {
    home() {
      if (this.sharedFrom) {
        return {
          title: this.$t("message.folderTabs.sharedFrom"),
          path: this.mainPath + "/shared/from"};
      }
      else if (this.sharedTo) {
        return {
          title: this.$t("message.folderTabs.sharedTo"),
          path: this.mainPath + "/shared/to" };
      }
      else {
        return {
          title: this.$t("message.folderTabs.all"),
          path: this.mainPath };
      }
    },
    mainPath () {
      return [
        "/browse",
        this.$route.params.user,
        this.$route.params.project,
      ].join("/");
    },
    folder() {
      return this.$route.params.container;
    },
    folderPath() {
      return this.$route.path;
    },
    subfolders() { //array of subfolder titles
      return this.$route.query.prefix != undefined ?
        this.$route.query.prefix.split("/") : "";
    },
  },
  methods: {
    getPath(index) {
      if (index === this.subfolders.length-1) {
        return this.$route.fullPath;
      } else {
        let prefixes = this.$route.query.prefix.split("/");
        prefixes = prefixes.slice(0, index+1).join("/");
        let path = this.folderPath + "?prefix=" + prefixes;
        return path;
      }
    },
  },
};

</script>

<style scoped>
.breadcrumb {
    padding: 1.5rem 0 1rem 0;
}
</style>
