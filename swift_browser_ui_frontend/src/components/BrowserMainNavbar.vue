<template>
  <div id="main-navigation">
    <div class="toolbar">
      <router-link
        class="navbar-item pl-4"
        :to="{name: 'AllFolders'}"
        :aria-label="$t('label.logo')"
      >
        <c-row align="center">
          <c-csc-logo alt="CSC_Logo" />
          <h1 class="app-name">
            {{ $t("message.program_name") }}
          </h1>
        </c-row>
      </router-link>

      <c-spacer />

      <div class="desktop-menu">
        <c-menu
          v-for="item of navigationMenuItems"
          :key="item.title"
          :aria-label="item.ariaLabel"
          :items.prop="item.subs.map(subItem => ({
            name: subItem.title,
            action: () => {
              (subItem.route || subItem.href) && handleItemRoute(subItem);
              subItem.action && subItem.action();
            },
            icon: subItem.href && extLinkIcon,
          }))"
          :data-testid="item.testid"
        >
          <i
            class="mdi pr-3 menu-icon"
            :class="item.icon"
          />
          <span class="menu-active">{{ item.title }}</span>
        </c-menu>
      </div>

      <c-navigationbutton class="pr-4" />
    </div>

    <c-sidenavigation
      mobile="true"
      :menu-visible="menuVisible"
    >
      <c-sidenavigationitem
        v-for="item of navigationMenuItems"
        :key="item.title"
      >
        <div slot="main">
          <span :class="'mdi ' + item.icon" />
          {{ item.title }}
        </div>

        <div
          v-if="item.subs && item.subs.length"
          slot="subnavitem"
        >
          <c-subnavigationitem
            v-for="subItem of item.subs"
            :key="subItem.title"
            :href="subItem.href"
            :target="subItem.href && '_blank'"
            :data-testid="subItem.testid"
            @click="() => {
              (subItem.route || subItem.href) && handleItemRoute(subItem);
              subItem.action && subItem.action();
            }"
          >
            {{ subItem.title }}
            <i
              v-if="subItem.href"
              class="mdi mdi-open-in-new"
            />
          </c-subnavigationitem>
        </div>
      </c-sidenavigationitem>
    </c-sidenavigation>
  </div>
</template>

<script>
import { getProjectNumber } from "@/common/globalFunctions";
import { mdiOpenInNew } from "@mdi/js";
export default {
  name: "BrowserMainNavbar",
  props: [
    "langs",
  ],
  data() {
    return {
      menuVisible: false,
      navigationMenuItems: [],
      currentLang: "",
      extLinkIcon: mdiOpenInNew,
      projectInfoLink: "",
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
    uname () {
      return this.$store.state.uname;
    },
    locale () {
      return this.$i18n.locale;
    },
  },
  watch: {
    active () {
      this.projectInfoLink = this.$t("message.dashboard.projectInfoBaseLink")
        + getProjectNumber(this.active);
      this.setNavigationMenu();
    },
    uname () {
      this.setNavigationMenu();
    },
    locale () {
      this.setNavigationMenu();
    },
  },
  created() {
    this.currentLang = this.langs.find(i =>  i.value == this.$i18n.locale).ph;
    this.setNavigationMenu();
  },
  methods: {
    setNavigationMenu() {
      this.navigationMenuItems = [];
      const menuArr = [
        {
          title: this.currentLang,
          icon: "mdi-web",
          testid: "language-selector",
          ariaLabel: this.$t("label.language_menu"),
          subs: this.langs.map(lang => ({
            title: lang.ph,
            action: () => {
              this.$i18n.locale = lang.value;
              this.currentLang = lang.ph;
              this.setCookieLang();
            }})),
        },
        {
          title: this.$t("message.support"),
          icon: "mdi-help-circle-outline",
          testid: "support-menu",
          ariaLabel: this.$t("label.support_menu"),
          subs: [
            {
              title: this.$t("message.supportMenu.item1"),
              href: this.$t("message.supportMenu.itemLink1"),
            },
            {
              title: this.$t("message.supportMenu.item2"),
              href: this.$t("message.supportMenu.itemLink2"),
            },
            {
              title: this.$t("message.supportMenu.item3"),
              action: () => this.$store.commit("toggleTokenModal", true),
            },
            {
              title: this.$t("message.supportMenu.item4"),
              href: this.$t("message.supportMenu.itemLink4"),
            },
          ],
        },
        {
          title: this.uname,
          icon: "mdi-account",
          testid: "user-menu",
          ariaLabel: this.$t("label.project_info"),
          subs: [
            {
              title: this.$t("message.dashboard.projectInfo"),
              href: this.projectInfoLink,
            },
            {
              title: this.$t("message.logOut"),
              route: "/login/kill",
              testid: "logout",
            },
          ],
        },
      ];
      this.navigationMenuItems = menuArr;
    },
    setCookieLang: function () {
      const expiryDate = new Date();
      expiryDate.setMonth(expiryDate.getMonth() + 1);
      document.cookie = "OBJ_UI_LANG=" +
        this.$i18n.locale +
        "; path=/; expires="
        + expiryDate.toUTCString();
    },
    handleItemRoute(item) {
      if (typeof item.route === "string") {
        window.location.href = item.route;
      } else if (item.route && item.route.name !== this.$route.name) {
        this.$router.push({...item.route, params: {
          user: this.uname,
          project: this.active.id}});
      } else if (item.href) {
        window.open(item.href, "_blank");
      }
    },
  },
};
</script>

<style lang="scss" scoped>

  .toolbar {
    z-index: 31;
    color: $csc-grey;
    height: 71px;
    display: flex;
    column-gap: 12px;
    align-items: center;
    padding: 0 1rem;
    box-shadow: rgba(0, 0, 0, 0.16) 2px 4px 10px;
  }

  .app-name {
    color: $csc-grey;
    font-size: 1.25rem;
    margin-left: 2rem;
  }

  .desktop-menu {
    display: flex;
    align-items: center;
  }

  c-menu {
    z-index: 1;
  }

  @media screen and (max-width: 767px) {
    .desktop-menu {
      display: none;
    }
  }

  @media screen and (min-width: 768px) {
    c-navigationbutton {
      display: none;
    }
  }

  </style>
