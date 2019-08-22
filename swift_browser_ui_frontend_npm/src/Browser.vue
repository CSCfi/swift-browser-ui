<template>
  <div>
    <BrowserNavbar
      :langs="langs"
      :multiple-projects="multipleProjects"
      :projects="projects"
      :active="active"
    />
    <div
      class="breadcrumb"
      aria-label="breadcrumbs"
    >
      <ul
        id="breadcrumb-list"
        style="margin-left:5%;margin-top:1%;"
      >
        <BreadcrumbListElement
          v-for="item in getRouteAsList ()"
          :key="item.alias"
          :alias="item.alias"
          :address="item.address"
        />
      </ul>
    </div>
    <router-view />
    <b-loading
      :is-full-page="isFullPage"
      :active.sync="isLoading"
      :can-cancel="false"
    />
    <footer
      id="footer"
      class="footer"
    >
      <div class="content has-text-centered">
        <p>
          <span class="has-text-weight-bold">
            {{ $t("message.program_name") }}
          </span> {{ $t("message.devel") }}
          <a 
            href="https://csc.fi"
            :alt="$t('message.cscOrg')"
          >{{ $t("message.cscOrg") }}</a>
        </p>
      </div>
    </footer>
  </div>
</template>
