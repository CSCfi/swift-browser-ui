
<template>
  <div class="breadcrumb">
    <c-row
      align="center"
    >
      <router-link
        :to="{ name: 'AllBuckets'}"
        @click="onClickBreadcrumb"
      >
        <i class="mdi mdi-home" />
        <span>&nbsp;{{ $t("message.bucketTabs.all") }}</span>
      </router-link>
      <router-link
        class="link"
        :to="{name: currentRoute}"
        @click="onClickBreadcrumb"
      >
        <i class="mdi mdi-chevron-right" />
        <span :class="folders === '' ? 'last' : 'default'">
          &nbsp;{{ bucket }}
        </span>
      </router-link>

      <router-link
        v-for="item, i in folders"
        :key="item"
        :to="getPath(i)"
        @click="onClickBreadcrumb"
      >
        <i class="mdi mdi-chevron-right" />
        <span :class="i === folders.length-1 ? 'last': 'default'">
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
    bucket() {
      return this.$route.params.container;
    },
    folders() { //array of folder titles
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
      if (index === this.folders.length-1) {

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
