// Tar convenience functions

// Add a folder to the tar archive structure
export function addTarFolder(name, prefix) {
  let mtime = Math.floor(Date.now() / 1000).toString(8);

  let header =
      name.padEnd(100, "\x00") // Tar name, max 100 char padded with NUL
      + "0000755\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      + "00000000000\x00"  // Size in octal ASCII, 11 bytes + padding NUL
      + mtime.padStart(11, "0") + "\x00" // Last modification, 11 bytes + padding nul
      + "        "  // checksum placeholder
      + "5"  // 1 byte type flag, 5 for folder
      + "\x00".repeat(100)  // Linked file name, 100 bytes, skip as NUL
      + "ustar\x00"  // ustar indicator
      + "00"  // ustar version
      + "\x00".repeat(32)  // Owner user name
      + "\x00".repeat(32)  // Owner group name
      + "0000000\x000000000\x00" // device major and minor numbers
      + prefix.padEnd(155, "\x00")  // prefix padded to 155
      + "\x00".repeat(12)  // pad to 512 bytes
    ;

  // Calculate checksum in between to ease header calculation
  let checksum = 0;
  for(let i = 0, length = 512; i < length; i++) {
    checksum += header.charCodeAt(i);
  }
  let checksumStr = checksum.toString(8).padStart(6, "0") + "\x00 ";
  header = header.replace("        ", checksumStr);

  return header;
}

// Add a file to the tar archive structure
export function addTarFile(name, prefix, size) {
  console.log(prefix);
  console.log(name);
  console.log(size);
  let mtime = Math.floor(Date.now() / 1000).toString(8);

  let header =
      name.padEnd(100, "\x00")  // Tar name, 100 char max padded with NUL
      + "0000644\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Size in octal ASCII, 11 bytes + padding NUL
      + size.toString(8).padStart(11, "0") + "\x00"
      + mtime.padStart(11, "0") + "\x00"  // Last modification, not used, 11 bytes + padding NUL
      + "        "  // checksum placeholder
      + "0"  // 1 byte type flag, 0 for normal file
      + "\x00".repeat(100)  // Linked file name, 100 bytes, skip as NUL
      + "ustar\x00"  // ustar indicator
      + "00"  // ustar version
      + "\x00".repeat(32)  // Owner user name
      + "\x00".repeat(32)  // Owner group name
      + "0000000\x000000000\x00" // device major and minor numbers
      + prefix.padEnd(155, "\x00")  // prefix padded to 155
      + "\x00".repeat(12) // pad to 512 bytes
    ;

  // Calculate checksum in between to ease header calculation
  let checksum = 0;
  for(let i = 0, length = 512; i < length; i++) {
    checksum += header.charCodeAt(i);
  }
  let checksumStr = checksum.toString(8).padStart(6, "0") + "\x00 ";
  header = header.replace("        ", checksumStr);

  return header;
}
