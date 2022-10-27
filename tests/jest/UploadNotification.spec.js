import "@testing-library/jest-dom";
import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import VueRouter from "vue-router";
import { render } from "@testing-library/vue";
import UploadNotification from "@/components/UploadNotification.vue";

import VueI18n from "vue-i18n";
import translations from "@/common/lang";

import cModel from "@/common/csc-ui.js";
import { applyPolyfills, defineCustomElements } from "csc-ui/dist/loader";

describe("UploadNotification", () => {
  const localVue = createLocalVue();

  localVue.use(Vuex);
  localVue.use(VueRouter);
  localVue.use(VueI18n);
  localVue.directive("csc-model", cModel);

  const router = new VueRouter();

  const i18n = new VueI18n({
    locale: "en",
    messages: translations,
  });

  applyPolyfills().then(() => {
    defineCustomElements();
  });

  const store = new Vuex.Store({
    state: { active: { id: "test-id" } },
  });

  const renderProps = {store, localVue, router, i18n};

  it("should render toast when upload notification is rendered", () => {
    const { container } = render(UploadNotification, renderProps);

    const toasts = container.querySelector("c-toasts");
    expect(toasts).toBeInTheDocument();

    const progressBar = container.getElementsByClassName("progress-bar");
    expect(progressBar.length).toBe(1);
  });
});
