Mind Map XBlock
#################

|status-badge| |license-badge| |ci-badge|

Purpose
*******

`XBlock`_ is the Open edX component architecture for building custom learning interactives.

.. _XBlock: https://openedx.org/r/xblock

Mind Map XBlock allows students to create and edit Mind Maps in a course.


Getting Started
***************
You can see the Mind Map in action in the XBlock Workbench. Running the Workbench requires
having docker running.

.. code:: bash

    git clone git@github.com:eduNEXT/xblock-mindmap
    cd xblock-mindmap
    virtualenv -p python3.8 venv && source venv/bin/activate
    make upgrade
    make install
    make dev.run

You can interact with the MindMapXBlock in the Workbench by navigating to http://localhost:8000

For details regarding how to deploy this or any other XBlock in the LMS instance, see the `installing-the-xblock`_ documentation.

.. _installing-the-xblock: https://edx.readthedocs.io/projects/xblock-tutorial/en/latest/edx_platform/devstack.html#installing-the-xblock


Using the jsMind library
************************
jsMind library can be used with the mouse or with certain keyboard shortcuts, which allow you to
interact with the mind map.

With the mouse
==============
- Click the node to select it.
- Double-click the node to edit it.
- Drag the node to move it.
- Click the circle to expand or collapse the child nodes.

With the keyboard
=================
- ``Ctrl + Enter``: Create a new child node for the selected node.
- ``Enter``: Create a new brother node for the selected node.
- ``F2``: Edit the selected node.
- ``Delete``: Delete the selected node.
- ``Space``: Expand or collapse the selected node.


Enabling in Studio
******************

You can enable the Mind Map XBlock in the studio through the advanced settings.

.. image:: https://github.com/eduNEXT/xblock-mindmap/assets/64033729/52b644de-4cd4-4971-abba-83f08e7aacdb

1. From the main page of a specific course, navigate to ``Settings → Advanced Settings`` from the top menu.
2. Check for the ``Advanced Module List`` policy key, and add ``"mindmap"`` to the policy value list.
3. Click the "Save changes" button.


Configuring Component
*********************

.. image:: https://github.com/eduNEXT/xblock-mindmap/assets/64033729/8a6da9d7-10d3-4803-a085-e84a68e2f066

Fields
======
- **Display name (String)**: Name of the component.


View from Learning Management System (LMS)
******************************************

.. image:: https://github.com/eduNEXT/xblock-mindmap/assets/64033729/67be4ebf-4d0e-44c8-ac61-173756da01d1

The student observes the component from the LMS and will be able to create, save and edit a mind map.


Getting Help
************

Documentation
=============

If you're having trouble, we have discussion forums at https://discuss.openedx.org where you can
connect with others in the community.

Our real-time conversations are on Slack. You can request a `Slack invitation`_, then join our
`community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this repository with as many details
about the issue you are facing as you can provide.

https://github.com/eduNEXT/xblock-limesurvey/issues

For more information about these options, see the `Getting Help`_ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/
.. _Getting Help: https://openedx.org/getting-help


License
*******

The code in this repository is licensed under the AGPL-3.0 unless otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.


Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes, security fixes, maintenance
work, or new features.  However, please make sure to have a discussion about your new feature idea with
the maintainers prior to beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing your idea.


The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/


Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@edunext.co.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/xblock-mindmap.svg
    :target: https://pypi.python.org/pypi/xblock-mindmap/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/eduNEXT/xblock-mindmap/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/eduNEXT/xblock-mindmap/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/eduNEXT/xblock-mindmap/coverage.svg?branch=main
    :target: https://codecov.io/github/eduNEXT/xblock-mindmap?branch=main
    :alt: Codecov

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/xblock-mindmap.svg
    :target: https://pypi.python.org/pypi/xblock-mindmap/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/eduNEXT/xblock-mindmap.svg
    :target: https://github.com/eduNEXT/xblock-mindmap/blob/main/LICENSE.txt
    :alt: License

.. TODO: Choose one of the statuses below and remove the other status-badge lines.
.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
