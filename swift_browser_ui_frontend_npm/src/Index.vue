<!-- Using the index page as a template for all the error pages as well, to -->
<!-- reduce the need to write things again unnecessarily. Could have made -->
<!-- things into components, but that would break the language support and -->
<!-- make index page development more difficult. -->
<template>
  <div class="hero is-fullheight">
    <div class="hero-body">
      <div class="container">
        <div class="columns is-centered">
          <div
            id="login-center"
            class="column is-4-desktop is-3-widescreen box"
          >
            <div class="columns is-centered">
              <a href="#">
                <img
                  src="./assets/csc_logo.svg"
                  :alt="$t('message.cscOrg')"
                >
              </a>
            </div>
            <div>
              <b-message
                v-if="unauth"
                :title="$t('message.error.Unauthorized')"
                type="is-warning"
                has-icon
              >
                {{ $t('message.error.Unauthorized_text') }}
              </b-message>
              <b-message
                v-if="forbid"
                :title="$t('message.error.Forbidden')"
                type="is-danger"
                has-icon
              >
                {{ $t('message.error.Forbidden_text') }}
              </b-message>
              <b-message
                v-if="notfound"
                :title="$t('message.error.Notfound')"
                type="is-warning"
                has-icon
              >
                {{ $t('message.error.Notfound_text') }}
              </b-message>
            </div>
            <div
              v-if="!forbid"
              class="buttons"
            >
              <a
                class="button is-primary is-fullwidth"
                href="/login"
              >{{ $t("message.index.logIn") }}</a>
            </div>
            <div
              v-if="notindex"
              class="buttons"
            >
              <a
                class="button is-primary is-fullwidth"
                href="/"
              >{{ $t("message.error.frontPage") }}</a>
            </div>
            <b-field class="locale-changer">
              <b-select
                v-model="$i18n.locale"
                placeholder="Language"
                icon="earth"
                expanded
                @input="setCookieLang ()"
              >
                <option
                  v-for="lang in langs"
                  :key="lang.value"
                  :value="lang.value"
                >
                  {{ lang.ph }}
                </option>
              </b-select>
            </b-field>
            <footer class="footer">
              <div class="content has-text-centered">
                <p>
                  <strong>{{ $t("message.program_name") }}</strong>
                  {{ $t("message.devel") }}
                  <a
                    href="https://csc.fi"
                    :alt="$t('message.cscOrg')"
                  >{{ $t("message.cscOrg") }}</a>
                </p>
              </div>
            </footer>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hero-body #login-center{
    padding: 30px 20px 20px 20px;
}

.hero-body .footer {
    margin:15px 0;
    padding:0;
}
</style>
