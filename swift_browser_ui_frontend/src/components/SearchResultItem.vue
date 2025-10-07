<template>
  <router-link
    :to="route(item)"
  >
    <div
      class="media"
    >
      <div
        class="media-content"
        data-testid="search-result"
      >
        <span>
          <b>{{
            isFolder() ? $t('message.search.folder') :
            isContainer()
              ? $t('message.search.container')
              : $t('message.search.object')
          }}: </b>
          <span v-if="retest(getFilename())">
            <span
              v-for="(apart, ind) in getParts(getFilename())"
              :key="ind"
            >
              <span
                v-if="searchArray.includes(apart.toLowerCase())"
                class="hl-1"
              >
                {{ apart }}
              </span>
              <span v-else>{{ apart }}</span>
            </span>
          </span>
          <span v-else>{{ getFilename() }}</span>
        </span>
        <br>
        <small>
          <span v-if="!isContainer()">
            <b>{{ $t('message.search.container') }}: </b>
            {{ item.container }}
            <br>
          </span>
          <span v-if="!isFolder() && hasPath()">
            <b>{{ $t('message.search.folder') }}: </b>
            <span v-if="retest(getFilePath())">
              <span
                v-for="(pathp, indx) in getParts(getFilePath())"
                :key="indx"
              >
                <span
                  v-if="searchArray.includes(pathp)"
                  class="hl-1"
                >
                  {{ pathp }}
                </span>
                <span v-else>{{ pathp }}</span>
              </span>
            </span>
            <span v-else>{{ getFilePath() }}</span>
            <br>
          </span>
          <span v-if="item.tags && item.tags.length">
            <b>{{ $t('message.search.tags') }}: </b>
            <span
              v-for="atag in getParts(item.tags.join(', '))"
              :key="atag"
            >
              <span
                v-if="retest(atag)"
                class="hl-1"
              >{{ atag }}</span>
              <span v-else>{{ atag }}</span>
            </span>
            <br>
          </span>
          <span>
            <b>{{ $t('message.search.size') }}: </b>
            <span> {{ getHumanReadableSize(item.bytes, locale) }}</span>
          </span>
          <span v-if="item.count">
            <br>
            <b>{{ $t('message.search.objects') }}: </b>{{ item.count }}
          </span>
        </small>
      </div>
    </div>
  </router-link>
</template>

<script>
import { getHumanReadableSize, tokenizerRE } from "@/common/conv";

export default {
  name: "SearchResultItem",
  props: [
    "item",
    "searchArray",
    "route",
  ],
  computed :{
    locale () {
      return this.$i18n.locale;
    },
  },
  methods: {
    getHumanReadableSize,
    isFolder: function() {
      return this.$props.item.folder;
    },
    isContainer: function() {
      return !this.isFolder() && this.$props.item.count !== undefined;
    },
    hasPath: function() {
      return this.$props.item.name.match("/");
    },
    getFilename: function() {
      let filename = "";
      if(this.isContainer() || !this.hasPath()) {
        filename = this.$props.item.name;
      }
      filename = this.$props.item.name.replace(/^.*\//, "");
      return filename;
    },
    getFilePath: function() {
      let filePath = "";
      if(this.isContainer() || !this.hasPath()) {
        return filePath;
      }
      const index = this.$props.item.name.lastIndexOf("/");
      //remove actual file name
      let str = this.$props.item.name.slice(0, index);
      //leave last folder
      filePath = str.slice(str.lastIndexOf("/")+1, str.length);
      return filePath;
    },
    retest: function(searched) {
      const searchFor = this.searchArray.join("|");
      const re = new RegExp(`(${tokenizerRE})(${searchFor})|(^${searchFor})`, "igu");
      return re.test(searched);
    },
    getParts: function(text) {
      let splits = [];
      const searchFor = this.searchArray.join("|");
      const re = new RegExp(`(${tokenizerRE})(${searchFor})|(^${searchFor})`, "igu");
      // Return a non sparse array split by the searched
      if(re.test(text)) {
        splits = text.split(re).filter(element => element);
      }
      return splits;
    },
  },
};
</script>

<style scoped>

.media {
  padding: 1rem;
}

span {
  display: inline !important
}

</style>
