<template>
  <div class="main">
    <MainToolbar />
    <div class="container">
      <form>
        <c-login-card :src="bannerUrl">
          <c-alert
            v-if="!idb"
            type="error"
          >
            <p>{{ $t('message.error.idb_text') }}</p>
          </c-alert>
          <c-login-card-title>
            {{ $t('message.program_name') }}
          </c-login-card-title>
          <c-login-card-content>
            <p>{{ $t('message.program_description') }}</p>
          </c-login-card-content>
          <c-login-card-actions>
            <c-button
              size="large"
              :loading="loading"
              :disabled="!idb"
              @click="loginButtonClick"
              @keyup.enter="loginButtonClick"
            >
              {{ $t('message.indexOIDC.logIn') }}
            </c-button>
          </c-login-card-actions>
          <c-spacer />
        </c-login-card>
      </form>
    </div>
    <CFooter />
  </div>
</template>

<script>
export default {
  methods: {
    loginButtonClick: function() {
      this.loading = true;
      window.location.pathname = this.$t("message.indexOIDC.href");
    },
  },
};
</script>

<style>

c-login-card {
  margin-right: auto;
  margin-left: auto;
  max-width: 55rem;
}
c-button {
  margin-top: 2rem;
}

</style>
