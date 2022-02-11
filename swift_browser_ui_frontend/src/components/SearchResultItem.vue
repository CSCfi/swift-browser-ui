<template>
  <router-link
    :to="route(item)"
  >
    <div class="media">
      <div class="media-content">
        <span><b>{{ 
          isContainer() 
            ? $t('message.search.container')
            : $t('message.search.object')
        }}: </b> {{ filename() }}
        </span>
        <br>
        <small>
          <span v-if="item.container">
            <b>{{ $t('message.search.container') }}: </b>
            {{ item.container }}
            <br>
          </span>
          <span v-if="hasPath()">
            <b>{{ $t('message.search.folder') }}: </b>
            {{ filePath() }}
            <br>
          </span>
          <span v-if="item.tags && item.tags.length">
            <b>{{ $t('message.search.tags') }}: </b>
            {{ item.tags.join(", ") }}
            <br>
          </span>
          <b>{{ $t('message.search.size') }}: </b>
          {{ getHumanReadableSize(item.bytes) }}
          <span v-if="isContainer()">
            <br>
            <b># {{ $t('message.search.objects') }}: </b>{{ item.count }}
          </span>
        </small>
      </div>
    </div>
  </router-link>
</template>

<script>
import { getHumanReadableSize } from "@/common/conv";
export default {
  name: "SearchResultItem",
  props: [
    "item",
    "route",
  ],
  methods: {
    getHumanReadableSize,
    isContainer: function() {
      return this.$props.item.container === undefined;
    },
    hasPath: function() {
      return this.$props.item.name.match("/");
    },
    filename: function() {
      if(this.isContainer() || !this.hasPath()) {
        return this.$props.item.name;
      }
      return this.$props.item.name.replace(/^.*\//, "");
    },
    filePath: function() {
      if(this.isContainer() || !this.hasPath()) {
        return "";
      }
      return this.$props.item.name.replace(/\/.*$/, "");
    },
  },
};
</script>
