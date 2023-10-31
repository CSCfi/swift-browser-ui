// Name check function to help prevent prototype pollution via container names

// Check that the parameter isn't trying to modify prototype
export function checkPollutingName(name) {
  return name === "__proto__" || name === "constructor" || name === "prototype"
}
