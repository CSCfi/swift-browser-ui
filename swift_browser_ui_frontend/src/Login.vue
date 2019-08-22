<template>
  <div>
    <h2>Object browser login progress</h2>
    <p class="maintext">
      <br>The current login process requires you to log in by fetching an
      unscoped token from the Openstack's keystone API. The server will handle
      scoping the token, logging in to the Openstack API, fetching all
      necessary information and revoking the token upon leaving the site.
      The login process currently goes as follows:
      <ol id="manlist">
        <li>
          Open a new tab and hit <b>F12</b> to open the console on said tab
        </li>
        <li>
          Open the <b>Network</b> tab on the console
        </li>
        <li>
          Open <a href="https://pouta.csc.fi:5001/v3/OS-FEDERATION/identity_providers/haka/protocols/saml2/auth">
            this link
          </a>
          in the new tab to begin authentication to Openstack and fetch an
          unscoped token.
        </li>
        <li>
          In the <b>Network</b> tab click open the last response visible on
          the console
        </li>
        <li>
          Copy the contents of the <b>X-Subject-Token</b> header from the response
        </li>
      </ol>
    </p>
    <p class="maintext">
      After successfully copying the response token id header, paste it in the
      following form's text field
    </p>
    <form
      id="retform"
      method="POST"
      action="/login/return"
    >
      <b>{{ formname }}</b><br>
      <input
        id="inputbox"
        type="text"
        name="token"
      ><br>
      <input type="submit">
    </form>
  </div>
</template>

<style>
#loginwindow {
    width: 70ch;
    margin-left: auto;
    margin-right: auto;
    margin-top: 7%;
}

h2 {
    font-family: sans-serif;
    text-align: center;
}

.maintext {
    font-family: sans-serif;
    text-align: justify;
    line-height: 1.5;
}

#manlist {
    text-align: justify;
    font-family: monospace;
    line-height: 1.4;
}

li {
    text-align: left;
}

a {
    color: black;
}

a:hover {
    background: pink;
    color: black;
}

form {
    text-align: center;
    line-height: 2.5;
    font-family: sans-serif;
}

#inputbox {
    width: 40ch;
}
</style>
