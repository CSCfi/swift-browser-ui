import Dexie from "dexie";

export function initDB() {
  const db = new Dexie("sd-connect");
  db.version(1).stores({
    projects: "&id, name",
    containers: "++id, &[projectID+name]",
    objects: "++id, &[containerID+name]",
    preferences: "id",
  });
  
  return db;
}
