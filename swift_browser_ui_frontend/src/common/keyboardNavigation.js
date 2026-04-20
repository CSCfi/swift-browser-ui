const FOCUSABLE_SELECTORS = "c-button:not([disabled]), c-icon-button:not([disabled]), " +
  "c-link:not([disabled]), c-text-field:not([disabled]), input:not([disabled])";
const WITH_NESTED_SELECTORS = "c-data-table";

/**
 * Get a list of focusable elements within a given ref
 * @param {HTMLElement} ref
 * @returns a list of focusable elements
 */
function getFocusableElements(ref) {
  const focusableList = Array.from(
    ref.querySelectorAll(FOCUSABLE_SELECTORS.concat(" ,", WITH_NESTED_SELECTORS)));
  let finalList = [];

  focusableList.forEach((el) => {
    // Skip hidden elements
    if (el.offsetParent !== null) {
      if (WITH_NESTED_SELECTORS.includes(el.tagName.toLowerCase())) {
        const nestedEls = Array.from(el.shadowRoot.querySelectorAll(FOCUSABLE_SELECTORS));
        if (nestedEls.length) {
          finalList.push(...nestedEls);
        }
      } else {
        finalList.push(el);
      }
    }
  });
  return finalList;
}

/**
 * Moves keyboard focus between first and last focusable elements
 * @param {KeyboardEvent} e - keydown event
 * @param {HTMLElement} first - first focusable modal element
 * @param {HTMLElement} last - last focusable modal element
 */
function keyboardNavigationInsideModal(
  e,
  first,
  last,
) {
  if (e.key === "Tab" && !e.shiftKey &&
    (e.target === last || e.target?.shadowRoot?.activeElement === last)) {
    first.tabIndex = "0";
    first.focus();
  } else if (e.key === "Tab" && e.shiftKey &&
      (e.target === first || e.target?.shadowRoot?.activeElement === first)) {
    last.tabIndex = "0";
    last.focus();
  }
}

/**
 * Function for restricting keyboard navigation to modal's content
 * @param {KeyboardEvent} e - keydown event
 * @param {HTMLElement} ref - modal c-card ref
 */
export function captureKeyboardNavInsideModal(e, ref) {
  if (e.key !== "Tab") return;

  const focusableEls = getFocusableElements(ref);
  const first = focusableEls[0];
  const last = focusableEls[focusableEls.length - 1];
  keyboardNavigationInsideModal(e, first, last);
}
