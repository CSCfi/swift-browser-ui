// Functions for displaying and sorting data in tables
import { DateTime } from "luxon";

export function checkIfItemIsLastOnPage(paginationOptions){
  //Checks if item is last on page and reverts to previous page
  if(paginationOptions.currentPage - 1 === 0){
    return 1;
  }
  if(paginationOptions.itemCount ===
    (paginationOptions.currentPage - 1)
    * paginationOptions.itemsPerPage){
    return paginationOptions.currentPage-=1;
  }
  return paginationOptions.currentPage;
}

export function getHumanReadableSize(val, locale) {
  const BYTE_UNITS = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"];

  let size = val ?? 0;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < BYTE_UNITS.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  const decimalSize = size.toFixed(1);
  let result = decimalSize.toString();

  if (locale === "fi") {
    result = result.replace(".", ",");
  }

  return `${result} ${BYTE_UNITS[unitIndex]}`;
}

export function getPaginationOptions(t) {
  const itemText = count => count === 1 ? t("message.table.item")
    : t("message.table.items").toLowerCase();

  const paginationOptions = {
    itemCount: 0,
    itemsPerPage: 50,
    currentPage: 1,
    startFrom: 0,
    endTo: 49,
    textOverrides: {
      itemsPerPageText: t("message.table.itemsPerPage"),
      nextPage: t("message.table.nextPage"),
      prevPage: t("message.table.prevPage"),
      pageText: ({ start, end, count }) =>
        start + " - " + end + " / " + count + " " + itemText(count),
      pageOfText: ({ pageNumber, count }) =>
        t("message.table.page") + pageNumber + " / " + count + "",
    },
  };
  return paginationOptions;
}

export function parseDateFromNow(locale, value, t) {
  if (!value) return t("message.table.unknown_date");
  return DateTime.fromISO(value.endsWith("Z") ? value : `${value}Z`).toRelative({ locale });
}

export function parseDateTime(locale, value, t, shortDate) {
// Parse date and time into internationalized format
  if (!value) return t("message.table.unknown_date");
  let dateLocale;
  let dateOptions = {};
  // In mode DEV, the value of date is not in correct ISO format,
  // lacking 'Z' at the end after 'seconds'
  const date = new Date(value.endsWith("Z") ? value : `${value}Z`);

  switch (locale) {
    case "fi": {
      dateLocale = "fi-FI";
      break;
    }
    default: {
      dateLocale = "en-GB";
    }
  }

  shortDate ?
    dateOptions = {
      day: "numeric",
      month: "short",
      year: "numeric",
    } :
    dateOptions = {
      weekday: "short",
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    };

  const dateTimeFormat = new Intl.DateTimeFormat(
    dateLocale,
    dateOptions,
  ).format(date);

  // Replace Finnish "at" time indicator with comma
  // English version defaults to comma
  return dateTimeFormat.replace(" klo", ", ");
}

function getTimestamp(str) {
  if (str) {
    return Date.parse(str.endsWith("Z") ? str : `${str}Z`);
  } else return -1; //if null last_modified
}

export function sortItems(a, b, sortBy, sortDirection) {
  sortBy = sortBy === "size" ?
    a?.size ? "size" : "bytes" //size for dropFiles
    : sortBy === "items" ? "count"
      : sortBy === "last_activity" ? "last_modified" : sortBy;

  let valueA = a[sortBy];
  let valueB = b[sortBy];

  if (sortBy === "last_modified") {
    //get timestamp from string
    valueA = getTimestamp(valueA);
    valueB = getTimestamp(valueB);

    if (sortDirection === "asc") {
      return valueA - valueB;
    }
    return valueB - valueA;
  }

  // Handle tags as single string
  if (Array.isArray(valueA)) {
    valueA = valueA ? valueA.join(" ") : "";
    valueB = valueB ? valueB.join(" ") : "";
  }

  if (typeof valueA === "string") {
    valueA = valueA.toLowerCase();
    valueB = valueB.toLowerCase();
    if (sortDirection === "asc") {
      return valueA < valueB ? -1 : valueA > valueB ? 1 : 0;
    }
    return valueB < valueA ? -1 : valueB > valueA ? 1 : 0;
  }

  if (typeof valueA === "number") {
    if (sortDirection === "asc") {
      return valueA - valueB;
    }
    return valueB - valueA;
  }
}

export function sortObjects(objects, sortBy, sortDirection) {
  objects.sort((a, b) => sortItems(a, b, sortBy, sortDirection));
}

export function truncate(value, length) {
  if (!value) {
    return "";
  }
  return value.length > length ? value.substr(0, length) + "..." : value;
}
