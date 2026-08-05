// Save log entries to session storage for log file creation

import { DEV } from "./globalFunctions";

const STORAGE_KEY = "sd-connect-log";
const MAX_ENTRIES = 1000;

export function captureConsole() {
  const originalConsole = {
    log: console.log,
    warn: console.warn,
    error: console.error,
    debug: console.debug,
  };

  // Only error and warn level msgs output to console in PROD

  console.log = (...args) => {
    saveConsoleEntry("INFO", args);
    if (DEV) originalConsole.log.apply(console, args);
  };

  console.warn = (...args) => {
    saveConsoleEntry("WARN", args);
    originalConsole.warn.apply(console, args);
  };

  console.error = (...args) => {
    saveConsoleEntry("ERROR", args);
    originalConsole.error.apply(console, args);
  };

  console.debug = (...args) => {
    saveConsoleEntry("DEBUG", args);
    if (DEV) originalConsole.debug.apply(console, args);
  };
}

export function getLogs() {
  return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "[]");
}

export function saveConsoleEntry(level, entry) {
  const logs = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "[]");
  const date = new Date().toISOString();
  const message = entry.map((e) => formatEntry(e)).join(" ");
  logs.push(`[${date}] [${level}] ${message}`);

  if (logs.length > MAX_ENTRIES) {
    logs.shift();
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(logs));
}

function formatEntry(entry) {
  if (typeof entry === "string") {
    return entry;
  } else {
    return JSON.stringify(entry);
  }
}
