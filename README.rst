Mind Map XBlock
#################

|status-badge| |license-badge| |ci-badge|

Purpose
*******

Mind Map XBlock is a pluggable extension to the Open edX platform that allows course creators to build a learning experience in which students can visualize and easily edit Mind Maps within a course unit.

It leverages the `jsMind`_ open source javascript library to visualize and edit mind maps on htmls canvas and svg.

.. _jsMind: https://github.com/hizzgdev/jsmind

The Mind Map Xblock component can be used to build and display a mind map for learners to explore a particular concept, or to have learners build their own Mind map which can then be graded by course staff members.

This Xblock has been created as an open source contribution to the Open edX platform and has been funded by the Unidigital project 2023. 

`XBlock`_ is the Open edX component architecture for building custom learning interactives.

.. _XBlock: https://openedx.org/r/xblock


Enabling the XBlock in a course
*******************************

When the xblock has been installed, you can enable the Mind Map XBlock for a particular course in STUDIO through the advanced settings.

1. From the main page of a specific course, navigate to ``Settings → Advanced Settings`` from the top menu.
2. Check for the ``Advanced Module List`` policy key, and add ``"mindmap"`` to the policy value list.
3. Click the "Save changes" button.

.. image:: https://github.com/eduNEXT/xblock-mindmap/assets/64033729/52b644de-4cd4-4971-abba-83f08e7aacdb



Adding a Mind map Component to a course unit
********************************************

.. image:: https://github.com/eduNEXT/xblock-mindmap/assets/33465240/268e97fc-9411-4581-aec6-5f949980442f

Fields
======
- **Display name (String)**: Name of the component.
- **Is a static mindmap? (Boolean)**: If this option is set to True, the course creator will provide the Mind map and learners will only be able to explore them but not edit them.  If set to False, the course creator can provide an initial version of the Mind map that learners will be able to modify and submit for grading.
- **Mindmap**: Instructors will be able to use a visual editor to create the mind map.


Using the jsMind interface
**************************
Each Mind Map can be explored or edited using the mouse or with keyboard shortcuts.

Using the mouse
===============
- Click on a node to select it.
- Double-click on a node to change the legend and click elsewhere to apply the changes.
- Drag the node to move it to a different part of the structure.
- Click the circle next to one node to expand or collapse its child nodes.

With the keyboard
=================
- ``Enter``: Create a new brother node for the selected node.
- ``Ctrl + Enter``: Create a new child node for the selected node.
- ``F2``: Edit the legend for the selected node and hit Enter to apply the changes.
- ``Delete``: Delete the selected node.
- ``Space``: Expand or collapse any children of the selected node.



View from Learning Management System (LMS)
******************************************

Learners can explore the Mind Map and when configured to be graded they can also edit it and submit it to be graded by the course instructors.

.. image:: https://github.com/eduNEXT/xblock-mindmap/assets/64033729/67be4ebf-4d0e-44c8-ac61-173756da01d1



Grading a submitted Mind Map
*****************************

Course instructors can provide a grade for each submitted Mind Map in a course, by accessing the grading interface directly from the LMS view.


Experimenting with this Xblock in the Workbench
************************************************
You can see the Mind Map in action in the XBlock Workbench. Running the Workbench requires having docker running.

.. code:: bash

    git clone git@github.com:eduNEXT/xblock-mindmap
    cd xblock-mindmap
    virtualenv -p python3.8 venv && source venv/bin/activate
    make upgrade
    make install
    make dev.run

Once the process is done, you can interact with the Mind Map XBlock in the Workbench by navigating to http://localhost:8000

For details regarding how to deploy this or any other XBlock in the Open edX platform, see the `installing-the-xblock`_ documentation.

.. _installing-the-xblock: https://edx.readthedocs.io/projects/xblock-tutorial/en/latest/edx_platform/devstack.html#installing-the-xblock

Getting Help
=============

If you're having trouble, the Open edX community has active discussion forums available at https://discuss.openedx.org where you can connect with others in the community.

Also, real-time conversations are always happening on the Open edX community Slack channel. You can request a `Slack invitation`_, then join the `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this repository with as many details about the issue you are facing as you can provide.

https://github.com/eduNEXT/xblock-mindmap/issues


Documentation
=============


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

This project is currently accepting all types of contributions, bug fixes, security fixes, maintenance
work, or new features.  However, please make sure to have a discussion about your new feature idea with
the maintainers prior to beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing your idea.

Translations
============
You can help by translating this component. Follow the steps below:

1. Create a folder for the translations in ``locale/``, eg: ``locale/es_419/LC_MESSAGES/``, and create
   your ``text.po`` file with all the translations.
2. Run ``make compile_translations``, this will generate the ``.mo`` file.
3. Create a pull request with your changes!


Reporting Security Issues
*************************

Please do not report a potential security issues in public. Please email security@edunext.co.

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
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
