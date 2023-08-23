
<template>
  <div class="breadcrumb">
    <c-row
      align="center"
    >
      <router-link
        :to="{ name: 'AllFolders'}"
        @click="onClickBreadcrumb"
      >
        <i class="mdi mdi-home" />
        <span>&nbsp;{{ $t("message.folderTabs.all") }}</span>
      </router-link>
      <router-link
        class="link"
        :to="{name: currentRoute}"
        @click="onClickBreadcrumb"
      >
        <i class="mdi mdi-chevron-right" />
        <span :class="subfolders === '' ? 'last' : 'default'">
          &nbsp;{{ folder }}
        </span>
      </router-link>

      <router-link
        v-for="item, i in subfolders"
        :key="item"
        :to="getPath(i)"
        @click="onClickBreadcrumb"
      >
        <i class="mdi mdi-chevron-right" />
        <span :class="i === subfolders.length-1 ? 'last': 'default'">
          &nbsp;{{ item }}
        </span>
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
    onClickBreadcrumb() {
      this.$emit("breadcrumbClicked", true);
    },
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

.breadcrumb {
  padding: 1.5rem 0 1rem 0;
}

.breadcrumb a {
  align-items: center;
  color: $csc-primary;
  display: flex;
  justify-content: center;
  padding: 0;
}

.breadcrumb a span {
  padding: 0 0.5em;
}

.last {
  font-weight: 700;
}
.default {
  font-weight: 400;
}

</style>
