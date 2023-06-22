<template>
  <router-link
    :to="route(item)"
  >
    <div
      class="media"
    >
      <div class="media-content">
        <span>
          <b>{{
            isSubfolder() ? $t('message.search.folder') :
            isContainer()
              ? $t('message.search.container')
              : $t('message.search.object')
          }}: </b>
          <!-- eslint-disable-next-line -->
          <span v-html="getFilename()"></span>
        </span>
        <br>
        <small>
          <span v-if="!isContainer()">
            <b>{{ $t('message.search.container') }}: </b>
            {{ item.container }}
            <br>
          </span>
          <span v-if="!isSubfolder() && hasPath()">
            <b>{{ $t('message.search.folder') }}: </b>
            <!-- eslint-disable-next-line -->
            <span v-html="getFilePath()"></span>
            <br>
          </span>
          <span v-if="item.tags && item.tags.length">
            <b>{{ $t('message.search.tags') }}: </b>
            <!-- eslint-disable-next-line -->
            <span v-html="highlight(item.tags.join(', '))"></span>
            <br>
          </span>
          <span>
            <b>{{ $t('message.search.size') }}: </b>
            <span> {{ getHumanReadableSize(item.bytes) }}</span>
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

const highlightTemplate =
  "$1<span class='has-background-primary-dark has-text-light hl-1'>$2</span>";

export default {
  name: "SearchResultItem",
  props: [
    "item",
    "searchArray",
    "route",
  ],
  methods: {
    getHumanReadableSize,
    isSubfolder: function() {
      return this.$props.item.subfolder;
    },
    isContainer: function() {
      return !this.isSubfolder() && this.$props.item.count;
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
      return this.highlight(filename);
    },
    getFilePath: function() {
      let filePath = "";
      if(this.isContainer() || !this.hasPath()) {
        return filePath;
      }
      const index = this.$props.item.name.lastIndexOf("/");
      //remove actual file name
      let str = this.$props.item.name.slice(0, index);
      //leave last subfolder
      filePath = str.slice(str.lastIndexOf("/")+1, str.length);
      return this.highlight(filePath);
    },
    highlight: function(text) {
      const searchFor = this.searchArray.join("|");
      const re = new RegExp(`(${tokenizerRE}|\\b)(${searchFor})`, "igu");
      if(re.test(text)) {
        text = text.replace(re, highlightTemplate);
      }
      return text;
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

.hl-1 {
  margin: 0 0.08rem;
}

</style>
