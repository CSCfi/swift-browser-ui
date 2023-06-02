<template>
  <c-alert
    type="success"
  >
    <c-row
      gap="64"
      justify="space-between"
    >
      <h3 v-if="closable">
        {{ $t("message.upload.complete") }}
      </h3>
      <h3 v-else>
        {{ $t("message.upload.inProgress") }}
      </h3>

      <ProgressBar />

      <a
        href="javascript:void(0)"
        class="link-underline"
        @click="$emit('view-container')"
      >
        {{ $t("message.upload.viewDestinationFolder") }}
      </a>

      <a
        ref="maximize"
        href="javascript:void(0)"
        class="toggle-notification"
        @click="$emit('toggle-notification')"
      >
        <i
          slot="icon"
          class="mdi mdi-arrow-expand"
        />
      </a>
      <a
        v-if="closable"
        ref="close"
        href="javascript:void(0)"
        @click="$emit('close-upload')"
      >
        <i
          slot="icon"
          class="mdi mdi-close"
        />
      </a>
    </c-row>
  </c-alert>
</template>

<script>
import ProgressBar from "./UploadProgressBar.vue";

export default {
  name: "UploadAlert",
  components: {
    ProgressBar,
  },
  computed: {
    closable() {
      return this.$store.state.uploadNotificationClosable;
    },
  },
  mounted() {
    setTimeout(() => {
      this.$refs.maximize.focus();
    }, 100);
  },
};
</script>

<style scoped lang="scss">

c-alert {
  margin: 1rem 5%;
}

h3 {
  font-size: 18px;
  margin-top: -2px;
}

@media screen and (max-width: 840px) {
    .link-underline {
      display: none;
    }
  }

</style>
