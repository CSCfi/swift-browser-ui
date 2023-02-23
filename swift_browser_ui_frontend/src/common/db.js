import Dexie from "dexie";

export function initDB() {
  const db = new Dexie("sd-connect");
  db.version(1).stores({
    projects: "&id, name",
    containers: "++id, &[projectID+name], *tags, *tokens",
    objects: "++id, &[containerID+name], *tags, *tokens",
    preferences: "id",
  });
  db.preferences.count(count => {
    if (count === 0) {
      db.preferences.add({id: 1});
    }
  });

  return db;
}
