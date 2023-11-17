// Tar convenience functions

function calcChecksum(header) {
  let checksum = 0;
    for(let i = 0, length = 512; i < length; i++) {
      checksum += header.charCodeAt(i);
    }
  let checksumStr = checksum.toString(8).padStart(6, "0") + "\x00 ";
  return checksumStr;
}

// Add a folder to the tar archive structure
export function addTarFolder(name, prefix) {
  let path = prefix ?
    prefix + "/" + name + "/": name + "/";
  let mtime = Math.floor(Date.now() / 1000).toString(8);
  let header = "";

  if (path.length > 100 && path.length <= 512) {

    //extra header block for long path name
    let lBlock =
      "././@LongLink" + "\x00".repeat(87)
      + "0000755\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Size in octal ASCII, 11 bytes + padding NUL
      + (path.length + 1).toString(8).padStart(11, "0") + "\x00"
      // Last modification, not used, 11 bytes + padding NUL
      + "00000000000\x00"
      + "        "  // checksum placeholder
      + "L" // 1 byte type flag, L for long pathname
      + "\x00".repeat(100)  // Linked file name, 100 bytes, skip as NUL
      + "ustar "  // ustar indicator
      + " \x00"  // ustar version
      + "root".padEnd(32, "\x00") //"\x00".repeat(32)  // Owner user name
      + "root".padEnd(32, "\x00") //"\x00".repeat(32)  // Owner group name
      + "\x00".repeat(183) // skip the rest, pad to 512 bytes
    ;

    let pathBlock = path;
    //pad the path to be divisable by 512 to get full blocks
    const pathRemainder = path.length % 512;

    if (pathRemainder !== 0) {
      let padding = 512 - pathRemainder;
      pathBlock += "\x00".repeat(padding);
    }

    lBlock = lBlock.replace("        ", calcChecksum(lBlock));

    let regularBlock =
      path.substring(0, 100)  // when path too long, truncate to 99
      + "0000755\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Size in octal ASCII, 11 bytes + padding NUL
      + "00000000000\x00"
      // Last modification, not used, 11 bytes + padding NUL
      + mtime.padStart(11, "0") + "\x00"
      + "        "  // checksum placeholder
      + "5"  // 1 byte type flag, 5 for folder
      + "\x00".repeat(100)  // Linked file name, 100 bytes, skip as NUL
      + "ustar "  // ustar indicator
      + " \x00"  // ustar version
      + "\x00".repeat(32)  // Owner user name
      + "\x00".repeat(32)  // Owner group name
      + "0000000\x000000000\x00" // device major and minor numbers
      + mtime.padStart(11, "0") + "\x00" // last accessed, atime
      + mtime.padStart(11, "0") + "\x00" // last changed, ctime
      + "\x00".repeat(12) // offset
      + "\x00".repeat(102) // longnames, unused, sparse structs, isextended
      + "00000000000\x00" // real size
      + "\x00".repeat(17) // pad to 512 bytes
    ;
    regularBlock = regularBlock.replace("        ", calcChecksum(regularBlock));
    // Calculate checksum in between to ease header calculation
    header = lBlock.concat(pathBlock, regularBlock);

  } else {

    header =
      path.padEnd(100, "\x00") // Tar name, max 100 char padded with NUL
      + "0000755\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      + "00000000000\x00"  // Size in octal ASCII, 11 bytes + padding NUL
      // Last modification, 11 bytes + padding nul
      + mtime.padStart(11, "0") + "\x00"
      + "        "  // checksum placeholder
      + "5"  // 1 byte type flag, 5 for folder
      + "\x00".repeat(100)  // Linked file name, 100 bytes, skip as NUL
      + "ustar "  // ustar indicator
      + " \x00"  // ustar version
      + "\x00".repeat(32)  // Owner user name
      + "\x00".repeat(32)  // Owner group name
      + "0000000\x000000000\x00" // device major and minor numbers
      + mtime.padStart(11, "0") + "\x00" // last accessed, atime
      + mtime.padStart(11, "0") + "\x00" // last changed, ctime
      // skip as NUL the following:
      // offset[12], longnames[4], unused[1],
      // sparse[4*24], isextended[1], realsize[12]
      + "\x00".repeat(126)
      + "\x00".repeat(17) // pad to 512 bytes
    ;
    header = header.replace("        ", calcChecksum(header));
  }
  return header;
}

// Add a file to the tar archive structure
export function addTarFile(name, prefix, size) {
  let mtime = Math.floor(Date.now() / 1000).toString(8);
  let path = prefix ?
    prefix + "/" + name : name;
  let header = "";

  if (path.length > 100 && path.length <= 512) {

    //extra header block for long path name
    let lBlock =
      "././@LongLink" + "\x00".repeat(87)
      + "0000644\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Size in octal ASCII, 11 bytes + padding NUL
      + (path.length + 1).toString(8).padStart(11, "0") + "\x00"
      // Last modification, not used, 11 bytes + padding NUL
      + "00000000000\x00"
      + "        "  // checksum placeholder
      + "L" // 1 byte type flag, L for long pathname
      + "\x00".repeat(100)  // Linked file name, 100 bytes, skip as NUL
      + "ustar "  // ustar indicator
      + " \x00"  // ustar version
      + "root".padEnd(32, "\x00") //"\x00".repeat(32)  // Owner user name
      + "root".padEnd(32, "\x00") //"\x00".repeat(32)  // Owner group name
      + "\x00".repeat(183) // skip the rest, pad to 512 bytes
    ;

    let pathBlock = path;
    //pad the path to be divisable by 512 to get full blocks
    const pathRemainder = path.length % 512;

    if (pathRemainder !== 0) {
      let padding = 512 - pathRemainder;
      pathBlock += "\x00".repeat(padding);
    }

    lBlock = lBlock.replace("        ", calcChecksum(lBlock));

    let regularBlock =
      path.substring(0, 100)  // when path too long, truncate to 99
      + "0000644\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Size in octal ASCII, 11 bytes + padding NUL
      + size.toString(8).padStart(11, "0") + "\x00"
      // Last modification, not used, 11 bytes + padding NUL
      + mtime.padStart(11, "0") + "\x00"
      + "        "  // checksum placeholder
      + "0"  // 1 byte type flag, 0 for normal file
      + "\x00".repeat(100)  // Linked file name, 100 bytes, skip as NUL
      + "ustar "  // ustar indicator
      + " \x00"  // ustar version
      + "\x00".repeat(32)  // Owner user name
      + "\x00".repeat(32)  // Owner group name
      + "0000000\x000000000\x00" // device major and minor numbers
      + mtime.padStart(11, "0") + "\x00" // last accessed, atime
      + mtime.padStart(11, "0") + "\x00" // last changed, ctime
      + "\x00".repeat(12) // offset
      + "\x00".repeat(101) // longnames, unused, sparse structs
      + "0" // is extended
      + size.toString(8).padStart(11, "0") + "\x00" // real size
      + "\x00".repeat(17) // pad to 512 bytes
    ;
    regularBlock = regularBlock.replace("        ", calcChecksum(regularBlock));
    // Calculate checksum in between to ease header calculation
    header = lBlock.concat(pathBlock, regularBlock);

  } else {
    header =
      path.padEnd(100, "\x00")  // Tar name, 100 char padded with NUL
      + "0000644\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Size in octal ASCII, 11 bytes + padding NUL
      + size.toString(8).padStart(11, "0") + "\x00"
      // Last modification, not used, 11 bytes + padding NUL
      + mtime.padStart(11, "0") + "\x00"
      + "        "  // checksum placeholder
      + "0"  // 1 byte type flag, 0 for normal file
      + "\x00".repeat(100)  // Linked file name, 100 bytes, skip as NUL
      + "ustar "  // ustar indicator
      + " \x00"  // ustar version
      + "\x00".repeat(32)  // Owner user name
      + "\x00".repeat(32)  // Owner group name
      + "0000000\x000000000\x00" // device major and minor numbers
      + mtime.padStart(11, "0") + "\x00" // last accessed, atime
      + mtime.padStart(11, "0") + "\x00" // last changed, ctime
      // skip as NUL the following:
      // offset[12], longnames[4], unused[1],
      // sparse[4*24], isextended[1], realsize[12]
      + "\x00".repeat(126)
      + "\x00".repeat(17) // pad to 512 bytes
    ;

    // Calculate checksum in between to ease header calculation
    header = header.replace("        ", calcChecksum(header));
  }

  return header;
}
