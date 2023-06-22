
<template>
  <div class="breadcrumb">
    <c-row
      align="center"
    >
      <router-link
        :to="{ name: 'AllFolders'}"
      >
        <i class="mdi mdi-home" />
        <p>&nbsp;{{ $t("message.folderTabs.all") }}</p>
      </router-link>
      <router-link
        class="link"
        :to="{name: currentRoute}"
      >
        <i class="mdi mdi-chevron-right" />
        <p :class="subfolders === '' ? 'last' : 'default'">
          &nbsp;{{ folder }}
        </p>
      </router-link>

      <router-link
        v-for="item, i in subfolders"
        :key="item"
        :to="getPath(i)"
      >
        <i class="mdi mdi-chevron-right" />
        <p :class="i === subfolders.length-1 ? 'last': 'default'">
          &nbsp;{{ item }}
        </p>
      </router-link>
    </c-row>
  </div>
</template>

<script>

export default {
  name: "BreadcrumbNav",
  computed: {
    folder() {
      return this.$route.params.container;
    },
    subfolders() { //array of subfolder titles
      return this.$route.query.prefix != undefined ?
        this.$route.query.prefix.split("/") : "";
    },
    currentRoute() {
      return this.$route.name;
    },
  },
  methods: {
    getPath(index) {
      if (index === this.subfolders.length-1) {

        return { name: this.currentRoute, query:
          { prefix: this.$route.query.prefix }};
      } else {
        let prefixes = this.$route.query.prefix.split("/");
        prefixes = prefixes.slice(0, index+1).join("/");
        return { name: this.currentRoute, query:
          { prefix: prefixes }};
      }
    },
  },
};

</script>

<style lang="scss" scoped>

i, p {
  color: $csc-primary;
}
c-row > * {
  margin-left: -1rem;
}
.breadcrumb {
    padding: 1.5rem 0 1rem 0;
}
.last {
  font-weight: 700;
}
.default {
  font-weight: 400;
}

</style>
