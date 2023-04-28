import { getContainerMeta, getAccessControlMeta, getObjectsMeta } from "./api";
import { getDB } from "@/common/db";

export default function getLangCookie() {
  let matches = document.cookie.match(
    new RegExp("(?:^|; )" + "OBJ_UI_LANG" + "=([^;]*)"),
  );
  return matches ? decodeURIComponent(matches[1]) : "en";
}

function shiftSizeDivision(vallist) {
  "use strict";
  // Javascript won't let us do anything but floating point division by
  // default, so a different approach was chosen anyway.
  //  ( right shift by ten is a faster alias to division by 1024,
  //  decimal file sizes are heresy and thus can't be enabled )
  switch (vallist[0] >>> 10) {
    case 0:
      return vallist;
    default:
      vallist[0] = vallist[0] >>> 10;
      vallist[1] = vallist[1] + 1;
      return shiftSizeDivision(vallist);
  }
}

function check_duplicate(container, share, currentdetails) {
  for (let detail of currentdetails) {
    if (detail.container == container && detail.sharedTo == share) {
      return true;
    }
  }
  return false;
}

function check_acl_mismatch(acl_cur, acl_sharing) {
  // Check if the ACLs mismatch
  if (
    !("read" in acl_sharing && acl_cur.access.includes("r")) ||
    !("write" in acl_sharing && acl_cur.access.includes("w"))
  ) {
    return true;
  }
  return false;
}

function check_stale(detail, access) {
  // Check if access detail entry has become stale
  if (!(detail.sharedTo in access)) {
    return true; // is stale
  }
  // Additionally check ACL mismatch
  return check_acl_mismatch(detail, access[detail.sharedTo]);
}

export async function syncContainerACLs(client, project) {
  let acl = await getAccessControlMeta(project);

  let amount = 0;
  let aclmeta = acl.access;
  let currentsharing = await client.getShare(project);

  // Delete stale shared container access entries from the database
  for (let container of currentsharing) {
    if (!Object.keys(aclmeta).includes(container)) {
      await client.shareContainerDeleteAccess(project, container);
    }
  }

  // Refresh current sharing information
  currentsharing = await client.getShare(project);
  // Prune stale shared user access entries from the database
  for (let container of currentsharing) {
    let containerDetails = await client.getShareDetails(project, container);
    for (let detail of containerDetails) {
      if (check_stale(detail, aclmeta[container])) {
        await client.shareDeleteAccess(project, container, [detail.sharedTo]);
      }
    }
  }

  // Refresh current sharing information
  currentsharing = await client.getShare(project);
  // Sync potential new shares into the sharing database
  for (let container of Object.keys(aclmeta)) {
    let currentdetails = [];
    if (currentsharing.includes(container)) {
      currentdetails = await client.getShareDetails(project, container);
    }
    for (let share of Object.keys(aclmeta[container])) {
      if (check_duplicate(container, share, currentdetails)) {
        continue;
      }
      let accesslist = [];
      if (aclmeta[container][share].read) {
        accesslist.push("r");
      }
      if (aclmeta[container][share].write) {
        accesslist.push("w");
      }
      await client.shareNewAccess(
        project,
        container,
        [share],
        accesslist,
        acl.address,
      );
      amount++;
    }
  }
  return amount;
}

export function getHumanReadableSize(val) {
  // Get a human readable version of the size, which is returned from the
  // API as bytes, flooring to the most significant size without decimals.

  // As JS doesn't allow us to natively handle 64 bit integers, ditch all
  // unnecessary stuff from the value, we only need the significant part.
  let byteval = val > 4294967296 ? parseInt(val / 1073741824) : val;
  let count = val > 4294967296 ? 3 : 0;

  let human = shiftSizeDivision([byteval, count]);
  let ret = human[0].toString();
  switch (human[1]) {
    case 0:
      ret += " B";
      break;
    case 1:
      ret += " KiB";
      break;
    case 2:
      ret += " MiB";
      break;
    case 3:
      ret += " GiB";
      break;
    case 4:
      ret += " TiB";
      break;
  }
  return ret;
}

export async function computeSHA256(keyContent) {
  const msgUint8 = new TextEncoder().encode(keyContent);
  const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return hashHex;
}

function extractTags(meta) {
  if ("Usertags" in meta[1]) {
    return meta[1]["Usertags"].split(";");
  }
  if ("usertags" in meta[1]) {
    return meta[1]["usertags"].split(";");
  }
  return [];
}

export async function getTagsForContainer(
  project, containerName, signal, owner) {
  let meta = await getContainerMeta(project, containerName, signal, owner);
  return extractTags(meta);
}

function extractBytes(meta) {
  if ("X-Container-Bytes-Used" in meta[1]) {
    return meta[1]["X-Container-Bytes-Used"];
  }
  return "";
}

function extractObjectCount(meta) {
  if ("X-Container-Object-Count" in meta[1]) {
    return meta[1]["X-Container-Object-Count"];
  }
  return "";
}

export async function getMetadataForSharedContainer(
  project,
  containerName,
  signal,
  owner,
) {
  let meta = await getContainerMeta(project, containerName, signal, owner);
  const bytes = extractBytes(meta);
  const count = extractObjectCount(meta);
  return { bytes: Number(bytes), count: Number(count) };
}

export async function getTagsForObjects(
  project,
  containerName,
  objectList,
  url,
  signal,
  owner,
) {
  let meta = await getObjectsMeta(
    project,
    containerName,
    objectList,
    url,
    signal,
    owner,
  );

  meta.map((item) => (item[1] = extractTags(item)));
  return meta;
}

export function makeGetObjectsMetaURL(project, container, objects) {
  return new URL(
    "/api/meta/".concat(
      encodeURI(project),
      "/",
      encodeURI(container),
      "?objects=",
      encodeURI(objects.join(",")),
    ),
    document.location.origin,
  );
}

export const taginputConfirmKeys = ["Tab", "Enter", " ", ",", ";", ".", ":"];

export function truncate(value, length) {
  if (!value) {
    return "";
  }
  return value.length > length ? value.substr(0, length) + "..." : value;
}

const SEGMENT_REGEX = /^\.segments(.*)$/;
const DATA_PREFIX = "data/";

export function filterSegments(objects) {
  // Calculate the size of segmented objects before filtering
  // Only works if segments come before the object in the array
  let segmentedObjSizes = {};
  objects.forEach((obj) => {
    const name = obj.name.replace(DATA_PREFIX, "");
    const nameFromSegment = SEGMENT_REGEX.exec(name);
    if (nameFromSegment === null && name in segmentedObjSizes) {
      obj.bytes = segmentedObjSizes[name];
      return;
    }
    if (nameFromSegment === null) {
      return;
    }
    if (!(nameFromSegment[1] in segmentedObjSizes)) {
      segmentedObjSizes[nameFromSegment[1]] = 0;
    }
    segmentedObjSizes[nameFromSegment[1]] += obj.bytes;
  });
  return objects.filter((o) => o.name.match(SEGMENT_REGEX) === null);
}

export const tokenizerRE = "[^\\p{L}\\d]";

export function tokenize(text, ignoreSmallerThan = 2) {
  // splits with non-word and non-digit chars
  const re = new RegExp(tokenizerRE, "u");
  const split = text.toLowerCase().split(re);

  // filters out small words and duplicates
  const result = split.filter(
    (item, index) =>
      item.length >= ignoreSmallerThan && split.indexOf(item) === index,
  );
  return result;
}

export const DEV = import.meta.env.MODE === "development";

export function sortObjects(objects, sortBy, sortDirection) {
  sortBy = sortBy === "size" ? "bytes"
    : sortBy === "items" ? "count" : sortBy;

  objects.sort((a, b) => {
    let valueA = a[sortBy];
    let valueB = b[sortBy];

    // Handle tags as single string
    if (Array.isArray(valueA)) {
      valueA = valueA.join(" ");
      valueB = valueB.join(" ");
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
  });
}

// Parse date and time into internationalized format
export function parseDateTime(locale, value, shortDate) {
  let dateLocale;
  const date = new Date(value);
  let dateOptions = {};

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

// Find the segments container matching a container (if it exists) and
// correctly update the container size using the size of the segments
// container.
export function addSegmentContainerSize(container, containers) {
  let segments = containers.find(el => el.name.match(`${container.name}_segments`));
  if (segments !== undefined) {
    container.bytes = segments.bytes;
  }
}

// Find the segments of an object and
// update the original objects size accordingly
export async function getSegmentObjects(projectID, container) {
  const segment_container = await getDB().containers.get({
    projectID,
    name: `${container.name}_segments`,
  });

  return await getDB()
    .objects.where({ containerID: segment_container.id })
    .toArray();
}
