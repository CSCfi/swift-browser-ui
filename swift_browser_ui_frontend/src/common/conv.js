export default function getLangCookie () {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + "OBJ_UI_LANG" + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : "en";
}

function shiftSizeDivision (vallist) {
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

export function getHumanReadableSize (val) {
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

export function recursivePruneCache (object_cache) {
  // Prune the object_cache until the cache is < 250000 objects in total
  if (getNestedObjectTotal(object_cache) > 250000) {
    delete object_cache[Object.keys(object_cache)[0]];
    return recursivePruneCache(object_cache);
  }
  return object_cache;
}

function getNestedObjectTotal (nested) {
  // Get the size of a object containing arrays, in the amount of total
  // array elements
  let ret = 0;
  for (var key in nested) {
    ret += nested[key].length;
  }
  return ret;
}
