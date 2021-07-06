<!-- Using the index page as a template for all the error pages as well, to -->
<!-- reduce the need to write things again unnecessarily. Could have made -->
<!-- things into components, but that would break the language support and -->
<!-- make index page development more difficult. -->
<template>
  <div class="indexpage">
    <div>
      <div class="block has-text-centered">
        <a 
          href="#"
          class="center"
        >
          <img
            src="@/assets/logo.svg"
            class="csc-logo"
            :alt="$t('message.cscOrg')"
          >
        </a>
      </div>
      <div class="content has-text-centered">
        <h2 class="title is-4 is-csc-secondary">
          {{ $t("message.program_name") }}
        </h2>
        <p>{{ $t("message.program_description") }}</p>
      </div>
      <div class="content has-text-centered">
        <h2 class="title is-4 is-csc-secondary">
          CSC Login
        </h2>
      </div>
      <form
        method="POST"
        action="/login/credentials"
      >
        <b-field
          class="center"
          label="Username"
        >
          <b-input />
        </b-field>
        <b-field
          class="center"
          label="Password"
        >
          <b-input />
        </b-field>
        <b-field
          class="center"
        >
          <b-input type="submit" />
        </b-field>
      </form>
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
      <div id="loginform" />
      <div class="block has-text-centered">
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

<style>
html, body {
  height: 100%;
}
.indexpage {
  width: 40%;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin: auto;
  align-content: center;
  justify-content: center;
}
.center {
  width: 50%;
  margin: auto;
}
.csc-logo {
  justify-content: center;
}
</style>
