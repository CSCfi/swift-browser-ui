<template>
  <c-main>
    <c-toolbar class="relative">
      <c-csc-logo />
      {{ $t('message.program_name') }}
      <c-spacer />
      <LanguageSelector />
    </c-toolbar>
    <c-row>
      <c-flex>
        <c-container class="padding">
          <form>
            <c-login-card
              :src="require('@/assets/banner_login.png')"
            >
              <c-alert type="error" v-if="!idb">
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
            </c-login-card>
          </form>
        </c-container>
      </c-flex>
    </c-row>
    <CFooter />
  </c-main>
</template>

<style>
c-main {
  height: unset;
  min-height: 100vh;
  justify-content: space-between;
}
c-login-card {
  margin: 2rem auto;
  max-width: 55rem;
  height: 35rem;
}
c-button {
  margin-top: 2rem;
}


</style>
