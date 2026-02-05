
<template>
  <div class="breadcrumb">
    <c-row
      align="center"
    >
      <router-link
        :to="{ name: 'AllBuckets'}"
        @click="onClickBreadcrumb"
      >
        <c-icon :path="mdiHome" size="16" />
        <span>&nbsp;{{ $t("message.bucketTabs.all") }}</span>
      </router-link>
      <router-link
        class="link"
        :to="{name: currentRoute}"
        @click="onClickBreadcrumb"
      >
        <c-icon :path="mdiChevronRight" size="16" />
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
        <c-icon :path="mdiChevronRight" size="16" />
        <span :class="i === folders.length-1 ? 'last': 'default'">
          &nbsp;{{ item }}
        </span>
      </router-link>
    </c-row>
  </div>
</template>

<script>

import { mdiHome, mdiChevronRight } from "@mdi/js";

export default {
  name: "BreadcrumbNav",
  data() {
    return {
      mdiHome,
      mdiChevronRight,
    };
  },
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

<style scoped>

p {
  color: var(--csc-primary);
}

.breadcrumb {
  padding: 1.5rem 0 1rem 0;
}

.breadcrumb a {
  align-items: center;
  color: var(--csc-primary);
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
