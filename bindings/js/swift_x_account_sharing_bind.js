// Swift cross account container sharing API JavaScript bindings module.

function parse_list_string (to_parse) {
    // Parse the JS list into comma separated values in string.
    let ret = "";
    to_parse.forEach(user => {
        ret = ret.concat(user, ",");
    });
    return ret.slice(0, ret.length - 1);
}

export async function x_account_api_get_access (
    username
) {
    // List the containers the user has been given access to.
    let url = new URL("/access/".concat(username), document.location);
    let containers = fetch(
        url, {method: "GET"}
    ).then(
        (resp) => {return resp.json();}
    );
    return containers;
};

export async function x_account_api_get_access_details(
    username,
    container,
    owner
) {
    // Get details from a container the user has been given access to.
    let url = new URL(
        "/access/".concat(username, "/", container), document.location
    );
    url.searchParams.append("owner", owner);
    let details = fetch(
        url, {method: "GET"}
    ).then(
        (resp) => {return resp.json();}
    );
    return details;
};

export async function x_account_api_get_share(
    username
) {
    // List the containers the user has shared to another user / users.
    let url = new URL("/share/".concat(username), document.location);
    let shared = fetch(
        url, {method: "GET"}
    ).then(
        (resp) => {return resp.json()}
    );
    return shared;
};

export async function x_account_api_get_share_details(
    username,
    container
) {
    // Get details from a container the user has given access to.
    let url = new URL(
        "/share/".concat(username, "/", container), document.location
    );
    let details = fetch(
        url, {method: "GET"}
    ).then(
        (resp) => {return resp.json()}
    );
    return details;
};

export async function x_account_api_share_new_access(
    username,
    container,
    userlist,
    accesslist,
    address
) {
    // Upload details about a new share action.
    let url = new URL(
        "/share/".concat(username, "/", container), document.location
    );
    url.searchParams.append("user", parse_list_string(userlist));
    url.searchParams.append("access", parse_list_string(accesslist));
    url.searchParams.append("address", address);
    let shared = fetch(
        url, {method: "POST"}
    ).then(
        (resp) => {return resp.json()}
    );
    return shared;
}

export async function x_account_api_share_edit_access(
    username,
    container,
    userlist,
    accesslist
) {
    // Edit the details of an existing share action.
    let url = new URL(
        "/share/".concat(username, "/", container), document.location
    );
    url.searchParams.append("user", parse_list_string(userlist));
    url.searchParams.append("access", parse_list_string(accesslist));
    let shared = fetch(
        url, {method: "PATCH"}
    ).then(
        (resp) => {return resp.json()}
    );
    return shared;
}

export async function x_account_api_share_delete_access(
    username,
    container,
    userlist
) {
    // Delete the details of an existing share action.
    let url = new URL(
        "/share/".concat(username, "/", container), document.location
    );
    url.searchParams.append("user", parse_list_string(userlist));
    let deleted = fetch(
        url, {method: "DELETE"}
    ).then(
        (resp) => {
            if (resp.status == 204) {return true};
            if (resp.status == 404) {return false};
        }
    )
    return deleted;
}
