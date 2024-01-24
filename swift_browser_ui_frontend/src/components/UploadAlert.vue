<template>
  <c-alert
    type="success"
  >
    <c-row
      gap="64"
      justify="space-between"
      align="center"
    >
      <h3>
        {{ closable ?
          $t("message.upload.complete") :
          $t("message.upload.inProgress") }}
      </h3>

      <ProgressBar />

      <a
        href="javascript:void(0)"
        class="link-underline"
        @click="$emit('view-container')"
      >
        {{ $t("message.upload.viewDestinationFolder") }}
      </a>
      <div class="actions">
        <a
          ref="maximize"
          href="javascript:void(0)"
          class="toggle-notification"
          @click="toggleNotification"
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
      </div>
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
  emits: ["view-container", "close-upload"],
  computed: {
    closable() {
      return this.$store.state.uploadNotification.closable;
    },
  },
  mounted() {
    setTimeout(() => {
      this.$refs.maximize.focus();
    }, 100);
  },
  methods: {
    toggleNotification() {
      this.$store.commit("toggleUploadNotificationSize");
    },
  },
};
</script>

<style scoped lang="scss">

c-alert {
  margin: 1rem 5%;
}

h3 {
  font-size: 18px;
}

.actions a {
  margin-left: 2rem;
}

@media screen and (max-width: 840px) {
    .link-underline {
      display: none;
    }
  }

</style>
