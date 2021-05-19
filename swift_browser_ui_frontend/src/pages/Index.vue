<!-- Using the index page as a template for all the error pages as well, to -->
<!-- reduce the need to write things again unnecessarily. Could have made -->
<!-- things into components, but that would break the language support and -->
<!-- make index page development more difficult. -->
<template>
  <div class="indexpage">
    <div class="contents">
      <div>
        <a 
          href="#"
          class="center"
        >
          <img
            src="@/assets/logo.svg"
            :alt="$t('message.cscOrg')"
          >
        </a>
      </div>
      <div>
        <h2 class="is-csc-secondary">{{ $t("message.program_name") }}</h2>
        <p>{{ $t("message.program_description") }}</p>
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
        <b-message
          v-if="uidown"
          :title="$t('message.error.UIdown')"
          type="is-warning"
          has-icon
        >
          {{ $t('message.error.UIdown_text') }}
        </b-message>
      </div>
      <div
        v-if="!forbid"
        class="buttons"
      >
        <a
          class="button is-primary center"
          href="/login"
        >{{ $t("message.index.logIn") }}</a>
      </div>
      <div
        v-if="notindex"
        class="buttons"
      >
        <a
          class="button is-primary center"
          href="/"
        >{{ $t("message.error.frontPage") }}</a>
      </div>
      <b-field class="locale-changer center">
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
      <div class="content has-text-centered">
        <p>
          {{ $t("message.devel") }}
          <a
            href="https://csc.fi"
            :alt="$t('message.cscOrg')"
          >{{ $t("message.cscOrg") }}</a>
        </p>              
      </div>
    </div>
  </div>
</template>

<style scoped>
.indexpage {
  width: 40%;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin: auto;
}
.contents {
  flex: 1 0 auto;
}
.center {
  width: 50%;
  margin: auto;
}
</style>
