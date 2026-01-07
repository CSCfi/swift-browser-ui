import { DateTime } from "luxon";
import { getDB } from "@/common/db";
import { getBucketPolicyStatements, awsHeadObject } from "./s3commands";

export default function getLangCookie() {
  let matches = document.cookie.match(
    new RegExp("(?:^|; )" + "OBJ_UI_LANG" + "=([^;]*)"),
  );
  return matches ? decodeURIComponent(matches[1]) : "en";
}

export async function deleteStaleSharedContainers (store) {
  const project = store.state.active.id;
  const aclmeta = acl.access;
  const client = store.state.client;

  const currentsharing = await client.getShare(project);

  if (currentsharing.length > 0) {
    // Delete stale shared container access entries from the database
    for (let container of currentsharing) {
      if (!Object.keys(aclmeta).includes(container)) {
        await client.shareContainerDeleteAccess(project, container);
      }
    }
  }

  return { project, client, acl, aclmeta };
}

export async function syncBucketPolicies(store) {
  // Sync bucket policies to sharind DB according to s3 bucket policies
  const project = store.state.active.id;
  const client = store.state.client;

  const buckets = await getDB()
    .containers
    .where({ projectID : project })
    .toArray();
  const bucketnames = buckets.map(b => b.name);

  // Refresh current sharing information
  let currentSharingDB = await client.getShare(project);
  // Prune any entries outside of current up-to-date bucket list
  for (let container of currentSharingDB) {
    if (!bucketnames.includes(container)) {
      const shareDetails = await client.getShareDetails(project, container);
      const shares = shareDetails.map(item => item.sharedTo);
      await client.shareDeleteAccess(project, container, shares);
    }
  }

  // Check bucket policies and sync sharing db
  for (let bucket of bucketnames) {
    // Get sharing information for bucket
    const shareDetails = await client.getShareDetails(project, bucket);
    let statements = [];
    try {
      statements = await getBucketPolicyStatements(bucket);
    } catch (e) {
      if (DEV) console.log(e.message);
    }
    // Build dict of current share recipients and their access rights (from db)
    let currentPolicies = {};
    for (let shareDetail of shareDetails) {
      const shareRecipient = shareDetail.sharedTo;
      const sharePolicy = {
        read: shareDetail.access.includes("r"),
        write: shareDetail.access.includes("w"),
      };
      currentPolicies[shareRecipient] = sharePolicy;
    }

    // Keep track of unused shares
    let toBeDeleted = Object.keys(currentPolicies);

    // compare current sharing db data with s3 bucketpolicy data, prune old data
    for (let statement of statements) {
      const principal = statement.Principal.AWS;
      if (principal === undefined) {
        continue;
      }
      const shareID = principal.match(/::([0-9a-fA-F]+):root$/)[1];
      const currentPolicy = currentPolicies[shareID];
      const bucketPolicy = {
        read: statement.Action.includes("s3:GetObject"),
        write: statement.Action.includes("s3:PutObject"),
      };

      toBeDeleted = toBeDeleted.filter(item => item !== shareID);

      if (
        bucketPolicy.read == currentPolicy?.read &&
        bucketPolicy.write == currentPolicy?.write
      ) {
        // Policies match, no action needed
        continue;
      }

      let accesslist = [];
      if (bucketPolicy.read) {
        accesslist.push("r");
      }
      if (bucketPolicy.write) {
        accesslist.push("w");
      }

      if (currentPolicies?.shareID) {
        // Existing shares need to be edited
        await client.shareEditAccess(
          project,
          bucket,
          [shareID],
          accesslist,
          "none",
        );
      } else {
        await client.shareNewAccess(
          project,
          bucket,
          [shareID],
          accesslist,
          "none",
        );
      }
    }
    // delete unusued shares
    if (toBeDeleted.length !== 0) {
      await client.shareDeleteAccess(project, bucket, toBeDeleted);
    }
  }
}

export function getHumanReadableSize(val, locale) {
  const BYTE_UNITS = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"];

  let size = val;
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

  if (meta) {
    meta.map((item) => {
      item[0] = item[0].includes("%2C") ?
        item[0].replace(/%2C/g, ",") : item[0];
      item[1] = extractTags(item);
    });
  }

  return meta;
}

export function makeGetObjectsMetaURL(project, container, objects) {
  /* encodeURI() doesn't encode comma ",".
    Therefore, if an object name contains comma ","
    replace it with URL-encoded "%2C"
  */

  for (let i = 0; i< objects.length; i++) {
    if (objects[i].includes(",")) {
      objects[i] = objects[i].replace(/,/g, "%2C");
    }
  }

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

export const taginputConfirmKeys = ["Enter", " ", ",", ";", ".", ":"];

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
  // don't use whole path for objects
  const shortName = text.split("/").slice(-2).join("/").toLowerCase();
  // splits with non-word and non-digit chars
  const re = new RegExp(tokenizerRE, "u");
  const split = shortName.split(re);

  // filters out small words and duplicates
  const result = split.filter(
    (item, index) =>
      item.length >= ignoreSmallerThan && split.indexOf(item) === index,
  );
  //if split too small to use, add unsplit name
  if (result.length === 0) result.push(shortName);
  return result;
}

export const DEV = import.meta.env.MODE === "development";

export function getTimestamp(str) {
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

// Parse date and time into internationalized format
export function parseDateTime(locale, value, t, shortDate) {
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

export function parseDateFromNow(locale, value, t) {
  if (!value) return t("message.table.unknown_date");
  return DateTime.fromISO(value.endsWith("Z") ? value : `${value}Z`).toRelative({ locale });
}

// Find the segments container matching a container (if it exists) and
// correctly update the container size using the size of the segments
// container.
export function addSegmentContainerSize(container, containers) {
  let segments = containers.find(el => el.name === `${container.name}_segments`);
  if (segments !== undefined) {
    container.bytes += segments.bytes;
  }
}

export function sortContainer(containers) {
  // sort "_segments" bucket before original bucket
  return containers.sort((a, b) => {
    if (a.name === `${b.name}_segments`) {
      return -1;
    } else if (b.name === `${a.name}_segments`) {
      return 1;
    }
  });
}


// Ensure that the objects that are marked as empty actually are
// This is required for v2 object compatibility
export async function ensureObjectSizes(
  bucket,
  objects,
) {
  return await Promise.all(objects.map(async(object) => {
    // If the object size is 0, try correcting the object size by forcing
    // content parsing in s3 storage
    if (object.bytes == 0) {
      const objectMetadata = await awsHeadObject(bucket, object.name);
      object.bytes = objectMetadata.ContentLength;
    }
    // Otherwise just return the object as is
    return object;
  }));
}
