<!-- Using the index page as a template for all the error pages as well, to -->
<!-- reduce the need to write things again unnecessarily. Could have made -->
<!-- things into components, but that would break the language support and -->
<!-- make index page development more difficult. -->
<template>
  <div class="main">
    <c-toolbar class="relative">
      <c-csc-logo alt="CSC-Logo" />
      {{ $t('message.program_name') }}
      <c-spacer />
      <LanguageSelector />
    </c-toolbar>
    <div class="container">
      <form
        method="POST"
        action="/login/credentials"
      >
        <c-login-card
          :src="bannerUrl"
        >
          <c-alert
            v-if="!idb"
            type="error"
          >
            <p>{{ $t('message.error.idb_text') }}</p>
          </c-alert>
          <c-login-card-title>
            {{ $t('message.pwdlogin.header') }}
          </c-login-card-title>
          <c-login-card-content>
            <p>{{ $t('message.pwdlogin.description') }}</p>
            <c-text-field
              v-control
              name="username"
              :label="$t('message.pwdlogin.uname')"
              type="text"
            />
            <c-text-field
              v-control
              name="password"
              :label="$t('message.pwdlogin.pwd')"
              type="password"
            />
          </c-login-card-content>
          <c-login-card-actions>
            <c-button
              type="submit"
            >
              <c-icon :path="mdiLogin" />
              {{ $t('message.index.logIn') }}
            </c-button>
            <input
              type="submit"
              style="display:none"
            >
          </c-login-card-actions>
          <c-spacer />
        </c-login-card>
      </form>
    </div>
    <CFooter />
  </div>
</template>

<style>

c-login-card {
  margin-right: auto;
  margin-left: auto;
  width: 55rem;
}
c-button {
  margin-top: 2rem;
}

</style>
