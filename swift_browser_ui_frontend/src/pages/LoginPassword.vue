<!-- Using the index page as a template for all the error pages as well, to -->
<!-- reduce the need to write things again unnecessarily. Could have made -->
<!-- things into components, but that would break the language support and -->
<!-- make index page development more difficult. -->
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
          <form
            method="POST"
            action="/login/credentials"
          >
            <c-login-card
              :src="require('@/assets/banner_login.png')"
            >
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
                  <i
                    slot="icon"
                    class="mdi mdi-login"
                  />
                  {{ $t('message.index.logIn') }}
                </c-button>
              </c-login-card-actions>
              <c-login-card-content v-if="!idb">
                <p>
                  <strong>{{ $t('message.error.idb') }}</strong>
                </p>
              </c-login-card-content>
            </c-login-card>
          </form>
        </c-container>
      </c-flex>
    </c-row>
   
  </c-main>
</template>

<style>
c-main { 
  height: unset; 
  min-height: 100vh 
}
c-login-card { 
  margin: 2rem auto;
  max-width: 55rem;
  height: 35rem; 
}
c-button {
  margin-top: 2rem;
}
footer {
  background-color: var(--csc-light-grey);
  color: var(--csc-dark-grey);
  padding: 1rem 0 1rem;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
}
footer h5 {
  font-weight: bold;
}
footer p {
  font-size: 0.875rem;
  line-height: 1rem;
}
footer c-flex {
  display: flex;
  justify-content: space-around;
  text-align: center;
}
</style>
