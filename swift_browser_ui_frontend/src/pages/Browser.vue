<template>
  <div id="mainContainer">
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

<style>
html, body {
  height: 100%;
}

#mainContainer {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.contents {
  flex: 1 0 auto;
}

.navbar .container .navbar-brand .navbar-item img {
	max-height: 2.5rem;
}

.hero-body #login-center{
    padding: 30px 20px 20px 20px;
}

.hero-body .footer {
    margin:15px 0;
    padding:0;
}

.searchBox {
    width: 30%;
    margin-left: auto;
}

.groupControls {
    margin: 0 5%;
}

.dashboard {
    margin-left: 5%;
    margin-right: 5%;
}

.footer {
  flex-shrink: 0;
}
</style>
