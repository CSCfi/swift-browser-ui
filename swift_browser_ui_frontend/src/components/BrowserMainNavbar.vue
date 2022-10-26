<template>
  <div id="main-navigation">
    <div class="toolbar">
      <router-link
        class="navbar-item pl-4"
        :to="`/browse/${uname}/${active.id}`"
      >
        <c-csc-logo />
      </router-link>

      <router-link
        class="navbar-item app-name"
        :to="`/browse/${uname}/${active.id}`"
      >
        <b class="app-name">{{ $t("message.program_name") }}</b>
      </router-link>

      <c-spacer />

      <div class="desktop-menu">
        <c-menu
          v-for="item of navigationMenuItems"
          :key="item.title"
          :items.prop="item.subs.map(subItem => ({
            name: subItem.title,
            action: () => {
              subItem.route && handleItemRoute(subItem)
              subItem.action && subItem.action()
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
              subItem.route && handleItemRoute(subItem)
              subItem.action && subItem.action()
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
      mobileNavigationItems: [
        {
          title: "Support",
          icon: "mdi-help-circle-outline",
          subs: [
            {
              title: "Link to CSC website",
            },
          ],
        },
        {
          title: "Finnish",
          icon: "mdi-web",
          subs: [
            {
              title: "Link to CSC website",
            },
          ],
        },
        {
          title: "User name",
          icon: "mdi-account",
          subs: [
            {
              title: "Link to CSC website",
            },
          ],
        },
      ],
      currentLang: "",
      extLinkIcon: mdiOpenInNew,
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
          subs: [
            {
              title: this.$t("message.supportMenu.manual"),
              href: "https://docs.csc.fi/data/sensitive-data/",
            },
            {
              title: this.$t("message.supportMenu.billing"),
              href: "https://research.csc.fi/pricing#buc",
            },
            {
              title: this.$t("message.supportMenu.sharing"), 
              route: {name: "TokensView", params: {        
                user: this.uname, 
                project: this.active.id}},
            },
            {
              title: this.$t("message.supportMenu.about"), 
              href: "https://research.csc.fi/sensitive-data",
            },
          ],
        },
        {
          title: this.uname,
          icon: "mdi-account",
          testid: "user-menu",
          subs: [
            {
              title: this.$t("message.dashboard.project_info"),
              href: `https://my.csc.fi/myProjects/project/${this.active.id}`,
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
  @import "@/css/prod.scss";

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
    font-size: 20px;
  }
  
  .desktop-menu {
    display: flex;
    align-items: center;
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