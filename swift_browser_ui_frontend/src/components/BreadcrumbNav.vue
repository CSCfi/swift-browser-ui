
<template>
  <div class="breadcrumb"> 
    <c-row
      align="center"
    >
      <c-link
        href="#"
        color="primary"
        :path="mdiHome"
        icon-fill="primary"
        icon-after="false"
        :weight="defaultWeight"
      >
        {{ home }}
      </c-link>
      <c-link
        :href="folder.path"
        color="primary"
        :path="mdiChevronRight"
        icon-fill="primary"
        icon-after="false"
        :weight="subfolders === '' ? lastWeight : defaultWeight"
      >
        {{ folder.title }}
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
    {{ route }}
  </div>
</template>

<script>
import { mdiHome, mdiChevronRight } from "@mdi/js";

export default {
  name: "BreadcrumbNav",
  props: ["home"],
  data() {
    return {
      lastWeight: 800,
      defaultWeight: 500,  
      mdiHome,
      mdiChevronRight,
    };
  },
  computed: {
    route() {
      return this.$route;
    },
    fullPath() {
      return this.$route.fullPath;
    },
    folder() {
      return { title: this.$route.params.container, path: this.$route.path };
    },
    subfolders() { //array of subfolder titles
      return this.$route.query.prefix != undefined ? 
        this.$route.query.prefix.split("/") : "";
    },
  },
  methods: {
    getPath(index) {
      if (index === this.subfolders.length-1) {
        return this.fullPath;
      } else {
        let prefixes = this.$route.query.prefix.split("/");
        prefixes = prefixes.slice(index, index+1).join("/");
        let path = this.folder.path + "?prefix=" + prefixes;
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
c-link {
    padding-right: 0rem;
}
</style>