<template>
  <c-main>
    <MainToolbar />
    <c-row
      class="title-row"
      align="center"
      justify="center"
    >
      <h1 class="title is-1">
        {{ $t('accessibilityPage.title') }}
      </h1>
    </c-row>
    <div class="content">
      <div class="intro-text">
        <p>{{ $t("accessibilityPage.intro1") }}</p>
        <p>{{ $t("accessibilityPage.intro2") }}</p>
      </div>
      <article>
        <h3 class="title is-3">
          {{ $t("accessibilityPage.part1.heading") }}
        </h3>
        <p>{{ $t("accessibilityPage.part1.text") }}</p>
      </article>
      <article>
        <h3 class="title is-3">
          {{ $t("accessibilityPage.part2.heading") }}
        </h3>
        <p>{{ $t("accessibilityPage.part2.text") }}</p>
        <div
          v-for="(item, index) in $tm('accessibilityPage.part2.subparts')"
          :key="index"
        >
          <h5 class="title is-4">
            {{ item.heading }}
          </h5>
          <h6 class="title is-6">
            {{ $t("accessibilityPage.part2.subheading1") }}
          </h6>
          <ul>
            <li>{{ item.text1 }}</li>
          </ul>
          <h6 class="title is-6">
            {{ $t("accessibilityPage.part2.subheading2") }}
          </h6>
          <ul>
            <li>{{ item.text2 }}</li>
          </ul>
        </div>
      </article>
      <article>
        <h3 class="title is-3">
          {{ $t("accessibilityPage.part3.heading") }}
        </h3>
        <h5 class="title is-5">
          {{ $t("accessibilityPage.part3.subheading") }}
        </h5>
        <p>{{ $t("accessibilityPage.part3.text1") }}</p>
        <ul
          v-for="(text, index) in $tm('accessibilityPage.part3.text2')"
          :key="index"
        >
          <li>{{ text.list }}</li>
        </ul>
      </article>
      <article>
        <h3 class="title is-3">
          {{ $t("accessibilityPage.part4.heading") }}
        </h3>
        <i18n-t
          keypath="accessibilityPage.part4.text"
          tag="p"
        >
          <template #authorityName>
            <a
              :href="$t('accessibilityPage.part4.authorityLink')"
              target="_blank"
            >
              {{ $t("accessibilityPage.part4.authorityName") }}
              <i class="mdi mdi-open-in-new" />
            </a>
          </template>
        </i18n-t>
      </article>
      <article>
        <h3 class="title is-3">
          {{ $t("accessibilityPage.part5.heading") }}
        </h3>
        <p
          v-for="(text, index) in $tm('accessibilityPage.part5.text')"
          :key="index"
        >
          {{ text.list }}
        </p>
      </article>
      <article>
        <h3 class="title is-3">
          {{ $t("accessibilityPage.part6.heading") }}
        </h3>
        <h6 class="title is-6">
          {{ $t("accessibilityPage.part6.subheading") }}
        </h6>
        <p>{{ $t("accessibilityPage.part6.text1") }}</p>
        <ul
          v-for="(text, index) in $tm('accessibilityPage.part6.text2')"
          :key="index"
        >
          <li>{{ text.list }}</li>
        </ul>
      </article>
    </div>
    <CFooter />
  </c-main>
</template>

<script>
export default {};
</script>

<style lang="scss" scoped>
c-main {
  height: unset;
  min-height: 100vh;
  justify-content: space-between;
  background-color: $white;
}
.content {
  height: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  z-index: 1;
  margin: 0 20%;
  padding: 1rem 0 4rem 0;
  :deep(.title), p, li, h3, h5, h6 {
    color: $csc-dark;
  }
  :deep(.title) { margin: 0 !important}
  & h3 { line-height: 4rem !important; }
  & h5, h6 { line-height: 3rem !important; }
  & p { line-height: 1.55rem !important; }
}

c-row {
  margin: 1rem 0;
  &.title-row {
    margin: 0;
    padding: 2rem 0;
    background-color: $csc-primary;
    & h1 {
      margin: 0;
      color: $white;
    }
  }
}
.intro-text {
  margin-top: 2rem;
}

article {
  margin-top: 1rem;
  &:nth-child(4) h3:first-child{
    line-height: 2.5rem !important;
  }
}

ul {
  margin-bottom: 1rem;
  & li {
    list-style-type: square;
    line-height: 1.5rem;
  }
}
</style>
