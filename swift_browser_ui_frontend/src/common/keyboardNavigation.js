import store from "@/common/store";

export function setPrevActiveElement() {
  const prevActiveEl = document.activeElement;
  store.commit("setPreviousActiveEl", prevActiveEl);
}

export function getFocusableElements(focusableList) {
  const first = focusableList[0];
  let last = focusableList[focusableList.length - 1];
  if (last.disabled) last = focusableList[focusableList.length - 2];
  return { first, last };
}

export function addFocusClass(element) {
  element.classList.add("button-focus");
}

export function removeFocusClass(element) {
  element.removeAttribute("tabIndex");
  element.classList.remove("button-focus");
}

export function disableFocusOutsideModal (modal) {
  const nav = document.querySelector("nav");
  Array.from(nav.children).forEach((child) =>
    child.setAttribute("inert", "true"));

  const mainContent = document.getElementById("mainContent");
  Array.from(mainContent.children).forEach((child) => {
    if (child !== modal) child.setAttribute("inert", "true");
  });

  const footer = document.querySelector("footer");
  Array.from(footer.children).forEach((child) =>
    child.setAttribute("inert", "true"));
}

export function moveFocusOutOfModal(prevActiveEl, isParentEl = false,
  addFocus = true) {
  removeFocusClass(document.activeElement);
  if (isParentEl) {
    store.commit("setPreviousActiveEl", prevActiveEl);
  }
  const nav = document.querySelector("nav");
  Array.from(nav.children).forEach((child) => {
    child.removeAttribute("inert");
  });

  const mainContent = document.getElementById("mainContent");
  Array.from(mainContent.children).forEach((child) => {
    child.removeAttribute("inert");
  });

  const footer = document.querySelector("footer");
  Array.from(footer.children).forEach((child) =>
    child.removeAttribute("inert"));

  if (prevActiveEl) {
    prevActiveEl.tabIndex = "0";
    prevActiveEl?.focus();
    if (prevActiveEl === document.activeElement && addFocus) {
      addFocusClass(prevActiveEl);
    }
  }
}

/*
  Basic standard function for navigating keyboard when inside a modal.
  It doesn't apply to all modals because modals are different and
  some modals need more configs than this.
*/
export function keyboardNavigationInsideModal(
  e,
  first,
  last,
  isUploadModal,
) {
  if (e.key === "Tab" && !e.shiftKey && e.target === last) {
    if(!isUploadModal) e.preventDefault();
    first.tabIndex = "0";
    first.focus();
    if (last.classList.contains("button-focus")) removeFocusClass(last);
  } else if (e.key === "Tab" && e.shiftKey) {
    if (e.target === first) {
      e.preventDefault();
      last.tabIndex = "0";
      last.focus();
      if (last === document.activeElement) {
        addFocusClass(last);
      }
    } else if (e.target === last) {
      removeFocusClass(last);
    }
  }
}
