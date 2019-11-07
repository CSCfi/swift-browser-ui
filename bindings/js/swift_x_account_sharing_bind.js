// Swift cross account container sharing API JavaScript bindings module.

class SwiftXAccountSharing {
  // Swift cross account sharing backend client.
  
  constructor (
    address
  ) {
    this.address = address;
  }

  _parseListString (
    toParse
  ) {
    // Parse the JS list into comma separated values in string.
    let ret = "";
    toParse.forEach(user => {
      ret = ret.concat(user, ",");
    });
    return ret.slice(0, ret.length - 1);
  }

  async getAccess (
    username
  ) {
    // List the containers the user has been given access to.
    let url = new URL("/access/".concat(username), this.address);
    let containers = fetch(
      url, {method: "GET"}
    ).then(
      (resp) => {return resp.json();}
    );
    return containers;
  }

  async getAccessDetails (
    username,
    container,
    owner
  ) {
    // Get details from a container the user has been given access to.
    let url = new URL(
      "/access/".concat(username, "/", container), this.address
    );
    url.searchParams.append("owner", owner);
    let details = fetch(
      url, {method: "GET"}
    ).then(
      (resp) => {return resp.json();}
    );
    return details;
  }

  async getShare (
    username
  ) {
    // List the containers the user has shared to another user / users.
    let url = new URL("/share/".concat(username), this.address);
    let shared = fetch(
      url, {method: "GET"}
    ).then(
      (resp) => {return resp.json();}
    );
    return shared;
  }

  async getShareDetails(
    username,
    container
  ) {
    // Get details from a container the user has given access to.
    let url = new URL(
      "/share/".concat(username, "/", container), this.address
    );
    let details = fetch(
      url, {method: "GET"}
    ).then(
      (resp) => {return resp.json();}
    );
    return details;
  }

  async shareNewAccess(
    username,
    container,
    userlist,
    accesslist,
    address
  ) {
    // Upload details about a new share action.
    let url = new URL(
      "/share/".concat(username, "/", container), this.address
    );
    url.searchParams.append("user", this._parseListString(userlist));
    url.searchParams.append("access", this._parseListString(accesslist));
    url.searchParams.append("address", address);
    let shared = fetch(
      url, {method: "POST"}
    ).then(
      (resp) => {return resp.json();}
    );
    return shared;
  }

  async shareEditAccess(
    username,
    container,
    userlist,
    accesslist
  ) {
    // Edit the details of an existing share action.
    let url = new URL(
      "/share/".concat(username, "/", container), this.address
    );
    url.searchParams.append("user", this._parseListString(userlist));
    url.searchParams.append("access", this._parseListString(accesslist));
    let shared = fetch(
      url, {method: "PATCH"}
    ).then(
      (resp) => {return resp.json();}
    );
    return shared;
  }

  async shareDeleteAccess(
    username,
    container,
    userlist
  ) {
    // Delete the details of an existing share action.
    let url = new URL(
      "/share/".concat(username, "/", container), this.address
    );
    url.searchParams.append("user", this._parseListString(userlist));
    let deleted = fetch(
      url, {method: "DELETE"}
    ).then(
      (resp) => {
        if (resp.status == 204) {return true;}
        if (resp.status == 404) {return false;}
      }
    );
    return deleted;
  }    
}

export default SwiftXAccountSharing;
  