<template>
  <div id="main-navigation">
    <div class="toolbar">
      <router-link
        v-if="uname && active?.id"
        :to="{name: 'AllBuckets', params: {user: uname, project: active.id }}"
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
            icon: subItem.href && mdiOpenInNew,
          }))"
          :data-testid="item.testid"
        >
          <c-icon :path="item.icon" size="36"
            class="pr-3 menu-icon"
          />
          <span class="menu-active">{{ item.title }}</span>
        </c-menu>
      </div>

      <c-navigation-button class="pr-4" />
    </div>

    <c-side-navigation
      mobile="true"
      :key="sideNavKey"
    >
      <c-side-navigation-item
        v-for="item of navigationMenuItems"
        :key="item.title"
        :data-testid="item.testid + '-mobile'"
      >
        <c-icon :path="item.icon" />
        {{ item.title }}
          <c-sub-navigation-item
            v-for="subItem of item.subs"
            :key="subItem.title"
            :href="subItem.href"
            :target="subItem.href && '_blank'"
            :data-testid="subItem.testid + '-mobile'"
            @click="() => {
              (subItem.route || subItem.href) && handleItemRoute(subItem);
              subItem.action && subItem.action();
            }"
          >
            {{ subItem.title }}
            <c-icon
              v-if="subItem.href"
              :path="mdiOpenInNew"
            />
          </c-sub-navigation-item>
      </c-side-navigation-item>
    </c-side-navigation>
  </div>
</template>

<script>
import { getProjectNumber } from "@/common/globalFunctions";
import { mdiOpenInNew, mdiWeb, mdiHelpCircleOutline, mdiAccount } from "@mdi/js";

export default {
  name: "BrowserMainNavbar",
  props: [
    "langs",
  ],
  data() {
    return {
      navigationMenuItems: [],
      currentLang: "",
      projectInfoLink: "",
      mdiOpenInNew,
      sideNavKey: 0,
    };
  },
  computed: {
    active () {
      return this.$store.active;
    },
    uname () {
      return this.$store.uname;
    },
    locale () {
      return this.$i18n.locale;
    },
  },
  watch: {
    active () {
      this.projectInfoLink = this.$t("message.supportMenu.projectInfoBaseLink")
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
      const menuArr = [
        {
          title: this.currentLang,
          icon: mdiWeb,
          testid: "language-selector",
          ariaLabel: this.$t("label.language_menu"),
          subs: this.langs
            .filter(lang => lang.ph != this.currentLang)
            .map(lang => ({
              title: lang.ph,
              action: () => {
                this.$i18n.locale = lang.value;
                this.currentLang = lang.ph;
                this.setCookieLang();
              }})),
        },
        {
          title: this.$t("message.support"),
          icon: mdiHelpCircleOutline,
          id: "support-menu",
          testid: "support-menu",
          ariaLabel: this.$t("label.support_menu"),
          subs: [
            {
              title: this.$t("message.supportMenu.userGuide"),
              href: this.$t("message.supportMenu.userGuideLink"),
            },
            {
              title: this.$t("message.supportMenu.projectInfo"),
              href: this.projectInfoLink,
            },
            {
              title: this.$t("message.supportMenu.createAPIKeys"),
              action: () => this.openAPIKeyModal(),
            },
          ],
        },
        {
          title: this.uname,
          icon: mdiAccount,
          testid: "user-menu",
          ariaLabel: this.$t("label.user_menu"),
          subs: [
            {
              title: this.$t("message.logOut"),
              route: "/login/kill",
              testid: "logout",
            },
          ],
        },
      ];
      this.navigationMenuItems = menuArr;
      this.sideNavKey++;
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
    openAPIKeyModal() {
      this.$store.toggleAPIKeyModal(true);
    },
  },
};
</script>

<style scoped>

.toolbar {
  z-index: 31;
  color: var(--csc-grey);
  height: 71px;
  display: flex;
  column-gap: 12px;
  align-items: center;
  padding: 0 1rem;
  box-shadow: rgba(0, 0, 0, 0.16) 2px 4px 10px;
}

.app-name {
  color: var(--csc-grey);
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
  c-navigation-button, c-side-navigation {
    display: none;
  }
}

</style>
