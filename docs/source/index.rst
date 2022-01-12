.. swift-browser-ui documentation master file, created by
   sphinx-quickstart on Fri Jun 28 13:30:19 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Object browser for CSC Pouta
============================

A Web UI object browser for object storage back-ends using Openstack Keystone
for authentication (e.g. `CSC Pouta <https://docs.csc.fi/cloud/pouta/>`_).
It uses federated login via `HAKA <https://rr.funet.fi/haka/>`_, via the
endpoints provided by `OpenStack Keystone <https://docs.openstack.org/keystone/latest/>`_.

Out of the box the ``swift-browser-ui`` offers:

* UI for browsing `SWIFT objects <https://docs.openstack.org/swift/latest/>`_;
* support for additional features like uploading files >5GiB in size;
* support for federated authentication of an user with their HAKA credentials
  using OpenStack Keystone;
* UI based on `Vue.js <https://vuejs.org/>`_ with `Buefy framework <https://buefy.org>`_;
* asynchronous web server.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

    Setup Instructions         <instructions>
    Usage & Examples           <usage>
    Deployment                 <deploy>
    Architecture               <tech>
    User Interface             <ui>
    Sharing Backend            <sharing>
    Access Request Backend     <request>
    Upload, Download and Copy  <runner>
    Python Modules             <code>
    Testing                    <testing>
    Tools / Miscellaneous      <tools>


.. note:: ``swift-browser-ui`` and all it sources are released under *MIT License*.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
