Change Log
##########

..
   All enhancements and patches to mindmap will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
**********

2.0.0 - 2025-02-04
**********************************************

Changed
=======

* Removed support for Python 3.8 and Django 3.2
* Replaced deprecated `pkg_resources` with `importlib.resources` for better compatibility with newer Django and Python versions.
* Starting with this version, this package is no longer compatible with releases older than Redwood.


1.1.0 - 2025-01-17
**********************************************

Added
=====

* Support for Python 3.11


1.0.0 - 2024-01-29
**********************************************

Changed
=======

* Remove boto3 from requirements

0.9.0 - 2023-10-06
**********************************************

Added
=======

* Support for weighted grading.

0.8.5 - 2023-10-02
**********************************************

Changed
=======

* Add author view to the XBlock to be used in Studio.

0.8.4 - 2023-10-02
**********************************************

Changed
=======

* Consider checking both role staff and instructor

0.8.3 - 2023-10-02
**********************************************

Changed
=======

* Allow to create any number of XBlocks in the lms

0.8.2 - 2023-09-26
**********************************************

Changed
=======

* Update names and messages of the XBlock fields


0.8.1 - 2023-09-22
**********************************************

Changed
=======

* Remove score in student view when the mindmap is static


0.8.0 - 2023-09-22
**********************************************

Added
=====

* Add the ability to configure the block as scorable from Studio
* Show assignment information to students


0.7.2 - 2023-09-18
**********************************************

Changed
=======

* Fix JavaScript translations


0.7.1 - 2023-09-08
**********************************************

Added
=====

* Add instructions for use for learners and instructors


0.7.0 - 2023-08-30
**********************************************

Added
=====

* Support for grading mindmap components in LMS instructor view.
* Better grading message.

Changed
=======

* Students can't edit mindmaps after submissions.


0.6.1 - 2023-08-28
**********************************************

Changed
=======

* Fix non-draggable nodes in mindmap component when in Studio.


0.6.0 - 2023-08-24
**********************************************

Added
=====

* Support for grading mindmap components using submissions API.


0.5.0 - 2023-08-11
**********************************************

Changed
=======

* Use xblocks fields to store state


0.4.1 - 2023-08-11
**********************************************

Changed
=======

* Add translations folder in package data


0.4.0 - 2023-08-10
**********************************************

Added
=====

* Add functionality to use custom storage backends
* Add translations of es_419 and es_ES in the xblock


0.3.0 - 2023-08-04
**********************************************

Added
=====

* Add test suite for Mind Map class definition
* Add functionality to create static mind maps from Studio


0.2.0 - 2023-07-28
**********************************************

Added
=====

* Add jsMind library in the XBlock
* Add functionality for save mind maps in S3


0.1.0 - 2023-07-21
**********************************************

Added
=====

* First release on PyPI.
