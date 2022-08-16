import "@testing-library/jest-dom";
import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import VueRouter from "vue-router";
import {render} from "@testing-library/vue";
import UploadNotification from "@/components/UploadNotification.vue";

describe("UploadNotification", () => {
  let store;
  let state;

  const localVue = createLocalVue();

  localVue.use(Vuex);
  localVue.use(VueRouter);

  const router = new VueRouter();

  beforeEach(() => {
    state = {
      active: { id: "test-id" },
    };

    store = new Vuex.Store({
      state,
    });
  });

  it("should render with testing library", () => {
    const $t = () => {};

    const {container} =  render(UploadNotification, {
      store,
      localVue,
      router,
      mocks: { $t },
    });

    const progressBar = container.getElementsByClassName("progress-bar");
    expect(progressBar.length).toBe(1);
  });
});
