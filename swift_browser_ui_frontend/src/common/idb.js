// Functions for indexedDB initialization and support

import Dexie from "dexie";
import { DEV } from "@/common/globalFunctions";

let DB;
let privateModeCheckResult;

function initDB() {
  const db = new Dexie("sd-connect", { cache: "disabled" });
  db.version(1).stores({
    projects: "&id, name",
    containers: "++id, &[projectID+name], *tags, *tokens",
    preferences: "id",
  });
  db.preferences.count((count) => {
    if (count === 0) {
      db.preferences.add({ id: 1 });
    }
  });

  return db;
}

// From https://github.com/dexie/Dexie.js/issues/613#issuecomment-841608979

export function getDB() {
  if (!DB) {
    DB = initDB();
  }

  const idb = DB.backendDB();

  if (idb) {
    try {
      // Check if if connection to idb did not close in the meantime
      idb.transaction("preferences").abort();
      return DB;
    } catch (e) {
      if (DEV) console.log("DB error", e);
    }
    DB.close();
    DB = initDB();
  }

  return DB;
}

// idb doesn't work in Firefox's private mode
// https://bugzilla.mozilla.org/show_bug.cgi?id=781982
// https://bugzilla.mozilla.org/show_bug.cgi?id=1639542
// https://github.com/aws-amplify/amplify-js/blob/7477d272587212c2a3cf0e86806f8ff4a03881e0/packages/datastore/src/util.ts#L337
// https://stackoverflow.com/questions/52803941/reactjs-redux-and-dexiejs-indexeddb-error-in-incognito-mode-and-chrome-v69

const isPrivateMode = () => {
  return new Promise(resolve => {
    const dbname = "test";
    let db;

    const isPrivate = () => {
      privateModeCheckResult = false;
      resolve(true);
    };

    const isNotPrivate = async () => {
      if (db && db.result && typeof db.result.close === "function") {
        await db.result.close();
      }
      await indexedDB.deleteDatabase(dbname);
      privateModeCheckResult = true;
      return resolve(false);
    };

    if (privateModeCheckResult === true) {
      return isNotPrivate();
    }

    if (privateModeCheckResult === false) {
      return isPrivate();
    }

    if (indexedDB === null) {
      return isPrivate();
    }

    db = indexedDB.open(dbname);
    db.onerror = isPrivate;
    db.onsuccess = isNotPrivate;
  });
};

export async function checkIDB() {
  if (typeof window.indexedDB === "undefined") {
    return false;
  }

  try {
    IDBKeyRange.only([1]);
  } catch {
    if (DEV) console.log("Buggy Microsoft IndexedDB implementation");
    return false;
  }

  if (await isPrivateMode()) {
    return false;
  }

  return true;
}
