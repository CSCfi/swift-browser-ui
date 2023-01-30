<template>
  <div class="selectpage">
    <div class="content has-text-centered">
      <h2>{{ $t("message.select.heading" ) }}</h2>
      <p class="maintext">
        {{ $t("message.select.description") }}
      </p>
      <p
        v-for="project in projects.filter(pro => pro.tainted)"
        :key="project.id"
      >
        <b-button
          tag="a"
          expanded
          :href="'/lock/'.concat(project.id)"
          size="is-large"
          type="is-primary is-outlined"
        >
          {{ project.name }}
        </b-button>
      </p>
      <p>
        <b-button
          tag="a"
          expanded
          href="/lock/none"
          size="is-large"
          type="is-primary is-outlined"
        >
          {{ $t("message.select.unrestricted" ) }}
        </b-button>
      </p>
      <p>
        <b-field class="locale-changed block center">
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
      </p>
    </div>
  </div>
</template>

<style>
html, body {
  height: 100%;
}
.selectpage {
  width: 40%;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin: auto;
  align-content: center;
  justify-content: center;;
}
.center {
  width: 50%;
  margin: auto;
}
</style>
