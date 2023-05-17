<template>
  <c-alert
    type="success"
  >
    <c-row
      gap="64"
      justify="space-between"
    >
      <h3>
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
        {{ $t("message.upload.maximize") }}
        <i
          slot="icon"
          class="mdi mdi-arrow-expand"
        />
      </a>
    </c-row>
  </c-alert>
</template>

<script>
import ProgressBar from "@/components/UploadProgressBar.vue";

export default {
  name: "UploadAlert",
  components: {
    ProgressBar,
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

.toggle-notification {
  margin-top: 2px;
}

</style>
