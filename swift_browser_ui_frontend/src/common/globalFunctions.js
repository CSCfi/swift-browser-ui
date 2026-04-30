// Miscellaneous global functions

import useStore from "@/common/store";
import { checkBucketExists, awsHeadObject } from "@/common/s3commands";
import { checkCorsFlag, updateCorsFlag } from "./idbFunctions";
import { awsAddBucketCors } from "./api";
import { NEW_VERSION_DATE } from "../../config/config";

export const DEV = import.meta.env.MODE === "development";

export function getProjectNumber(project) {
  if (project.name) {
    const splitProjectName = project.name.split("_");
    return splitProjectName.length > 1 ? splitProjectName[1] : "";
  } else {
    return "";
  }
}

export function getPrefix(route) {
  // Get current pseudofolder prefix
  if (route.query.prefix == undefined) {
    return "";
  }
  return `${route.query.prefix}/`;
}

export function getFolderName(folderName, route) {
  // Get the name of the currently displayed pseudofolder
  let endregex = new RegExp("/.*$");
  return folderName.replace(getPrefix(route), "").replace(endregex, "");
}

export function isFile(path, route) {
  // Return true if path represents a file in the active prefix context
  return path.replace(getPrefix(route), "").match("/") ? false : true;
}

function isLowerCaseOrNum(char) {
  return /[\p{L}0-9]/u.test(char) && char === char.toLowerCase();
}

export async function validateBucketName(input) {
  let result = {
    lowerCaseOrNum: undefined,
    inputLength: undefined,
    alphaNumHyphen: undefined,
    ownable: undefined,
  };
  if (!input) return result;

  result.lowerCaseOrNum = isLowerCaseOrNum(input[0]) &&
    isLowerCaseOrNum(input[input.length - 1]);
  result.inputLength = input.length >= 3 && input.length <= 63;
  result.alphaNumHyphen = !!input.match(/^[a-z0-9-]+$/g);

  if (result.lowerCaseOrNum && result.inputLength && result.alphaNumHyphen) {
    const bucketExists = await checkBucketExists(input);
    // In undefined case allow user to attempt bucket creation
    result.ownable = !bucketExists;
  } else {
    result.ownable = false;
  }
  return result;
}

export function timeout(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
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

export function getCurrentISOtime(time) {
  return time ? new Date(time).toISOString() : new Date().toISOString();
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

export async function checkAndAddBucketCors(projectID, bucket) {
  if (!projectID || !bucket) throw new Error("Missing projectID and/or bucket for CORS check");
  const corsAdded = await checkCorsFlag(projectID, bucket);
  if (corsAdded === false) {
    if (DEV) console.log("Adding CORS for", bucket);
    try {
      await awsAddBucketCors(projectID, bucket);
      await updateCorsFlag(projectID, [bucket], true);
    } catch {
      if (DEV) console.log(`Failed to add CORS to bucket ${bucket}`);
    }
  }
}

/** TAGS */

export const taginputConfirmKeys = ["Enter", " ", ",", ";", ".", ":"];

export function addNewTag (event, currentTags, onBlur) {
  if (taginputConfirmKeys.includes(event.key) || onBlur) {
    event.preventDefault();
    const newTag = event.target.value.trim();
    event.target.value = "";
    if (newTag !== "" && !currentTags.includes(newTag)) {
      currentTags.push(newTag);
    }
  }
  return currentTags;
}

export function deleteTag (event, tag, currentTags) {
  event.preventDefault();
  return currentTags.filter(el => el !== tag);
}

/** TOASTS */

export function addErrorToastOnMain(msg) {
  document.querySelector("#container-error-toasts")
    .addToast(
      { progress: false,
        type: "error",
        duration: 6000,
        message: msg },
    );
}

export function moveToast(toastToMove, otherElement, restore) {
  //restore toast to original position or
  //move toast above another element
  if (toastToMove && restore) {
    toastToMove.style.marginBottom = "0";
  }
  else if (toastToMove && otherElement){
    const h = otherElement.getBoundingClientRect().height;
    toastToMove.style.marginBottom = h + "px";
  }
}

/** MODALS */

export function toggleCreateBucketModal() {
  const store = useStore();
  store.toggleCreateBucketModal(true);
}

export function toggleEditTagsModal(objectName, containerName) {
  const store = useStore();
  if (objectName) {
    store.setObjectName(objectName);
  }
  if (containerName) {
    store.setBucketName(containerName);
  }
  store.toggleEditTagsModal(true);
}

export function toggleCopyBucketModal(bucketName, sourceProjectId) {
  const store = useStore();
  if (bucketName) {
    store.setBucketName(bucketName);
  }
  if (sourceProjectId) {
    store.setSourceProjectId(sourceProjectId);
  }
  store.toggleCopyBucketModal(true);
}

export function toggleDeleteModal(objects, containerName) {
  const store = useStore();
  if (objects) {
    store.setDeletableObjects(objects);
  }
  if (containerName) {
    store.setBucketName(containerName);
  }
  store.toggleDeleteModal(true);
}

/**
 * Function to determine if bucket breaks S3
 * Used to determine if bucket actions will fail before bucket is converted
 * @param {String} bucketName
 * @returns bool
 */
export function checkBucketBreaksS3(bucketName) {
  // If the bucket contains whitespace or non-Latin letters, it's guaranteed to break S3
  return !/^[a-zA-Z0-9_.-]+$/.test(bucketName);
}

/**
 * Function to determine if bucket was created with v3
 * @param {Object} bucket
 * @returns bool
 */
export function checkBucketCreatedV3(bucket) {
  return Date.parse(bucket.created) > NEW_VERSION_DATE;
}

/**
 * Function to determine the severity of conversion need
 * Adapted from sd-connect-s3-migrate
 * @param {Array} buckets in project
 * @param {Object} bucket the conversion need of which is being determined
 * @returns int between 0-2 to reflect none, end-of-year, urgent
 */
export function getRecommendedAction(buckets, bucket) {
  if (checkBucketBreaksS3(bucket.name)) {
    return 2;
  }

  // If the bucket doesn't have any bytes, but has content, it has likely
  // been filled with swift large objects
  if (!bucket.bytes && bucket.count) {
    return 1;
  }

  // If the bucket has a matching segemnts bucket with content, it likely
  // contains swift large objects
  if (buckets.find((nb) => nb.name == `${bucket.name}_segments`)?.count > 0) {
    return 1;
  }

  // If the bucket name is too long, it will likely have to be truncated
  if (bucket.name.length < 3 || bucket.name.length > 63) {
    return 1;
  }

  // If the bucket doesn't start with lowercase alphanumeric, it should
  // probably be migrated
  if (!isLowerCaseOrNum(bucket.name[0]) || !isLowerCaseOrNum(bucket.name[bucket.name.length - 1])) {
    return 1;
  }

  // If the bucket contains non-alphanumeric characters, it should probably
  // be migrated with a conforming name
  if (!bucket.name.match(/^[a-z0-9-]+$/g)) {
    return 1;
  }

  // No need to migrate buckets created with V3
  if (checkBucketCreatedV3(bucket)) {
    return 0;
  }
  return 1;
}
