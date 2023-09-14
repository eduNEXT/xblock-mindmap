"""XBlock to create and save Mind Maps in Open edX."""

from __future__ import annotations

import json
import logging

import pkg_resources
from django.core.exceptions import PermissionDenied
from django.utils import translation
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.exceptions import JsonHandlerError
from xblock.fields import Boolean, DateTime, Dict, Float, Integer, Scope, String
from xblockutils.resources import ResourceLoader

from mindmap.edxapp_wrapper.student import user_by_anonymous_id
from mindmap.edxapp_wrapper.xmodule import get_extended_due_date
from mindmap.utils import _, utcnow


log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)

ITEM_TYPE = "mindmap"
ATTR_KEY_ANONYMOUS_USER_ID = 'edx-platform.anonymous_user_id'
ATTR_KEY_USER_ROLE = 'edx-platform.user_role'


@XBlock.wants("user")
@XBlock.needs("i18n")
class MindMapXBlock(XBlock):
    """
    Mind Map XBlock provides a way to create and save mind maps in a course.
    """

    has_score = True
    icon_class = "problem"

    display_name = String(
        display_name=_("Display name"),
        default="Mind Map",
        scope=Scope.settings,
    )

    is_static = Boolean(
        help=_(
            "Whether the mind map is static or not. If it is static, the instructor can "
            "create a mind map and it will be the same for all students. If it is not "
            "static, the students can create their own mind maps."
        ),
        display_name=_("Is a static mindmap?"),
        default=False,
        scope=Scope.settings,
    )

    mindmap_body = Dict(
        help=_(
            "The mind map that will be shown to students if the"
            '"Is a static mindmap?" field is set to "True"'
        ),
        display_name=_("Mindmap body"),
        default={
            "meta": {
                "name": "Mind Map",
                "version": "0.1",
            },
            "format": "node_array",
            "data": [
                {
                    "id": "root",
                    "isroot": "true",
                    "topic": "Root",
                }
            ]
        },
        scope=Scope.settings,
    )

    mindmap_student_body = Dict(
        help=_(
            "The body of the mind map. It is a dictionary with the following structure: "
            "{'root': {'text': 'Root', 'children': [{'text': 'Child 1', 'children': []}]}}"
        ),
        display_name=_("Mindmap student body"),
        default={},
        scope=Scope.user_state,
    )

    weight = Float(
        display_name=_("Problem Weight"),
        help=_(
            "Defines the number of points each problem is worth. "
            "If the value is not set, the problem is worth the sum of the "
            "option point values."
        ),
        values={"min": 0, "step": 0.1},
        scope=Scope.settings,
    )

    points = Integer(
        display_name=_("Maximum score"),
        help=_("Maximum grade score given to assignment by instructors."),
        default=100,
        scope=Scope.settings,
    )

    submitted = Boolean(
        display_name=_("Submitted"),
        help=_("Whether the student has submitted their submission."),
        default=False,
        scope=Scope.user_state,
    )

    @property
    def block_id(self):
        """
        Return the usage_id of the block.
        """
        return str(self.scope_ids.usage_id)

    @property
    def block_course_id(self):
        """
        Return the course_id of the block.
        """
        return str(self.course_id)

    @property
    def score(self):
        """
        Return score from submissions.
        """
        return self.get_score()

    def max_score(self):
        """
        Return the maximum score.
        """
        return self.points

    def get_current_user(self):
        """
        Get the current user.
        """
        return self.runtime.service(self, "user").get_current_user()

    def is_course_staff(self, user) -> bool:
        """
        Check whether the user has course staff permissions for this XBlock.
        """
        return user.opt_attrs.get("edx-platform.user_is_staff")

    def is_student(self, user) -> bool:
        """
        Check if the user is a student.
        """
        return user.opt_attrs.get("edx-platform.user_role") == "student"

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, template_path, context=None) -> str:
        """
        Render a template with the given context. The template is translated
        according to the user's language.

        Args:
            template_path (str): The path to the template
            context(dict, optional): The context to render in the template

        Returns:
            str: The rendered template
        """
        return loader.render_django_template(
            template_path, context, i18n_service=self.runtime.service(self, 'i18n')
        )

    def get_context(self, user):
        """
        Return the context for the student view.

        Args:
            user: The current user

        Returns:
            dict: The context for the student view
        """
        in_student_view = self.is_student(user) or self.is_course_staff(user)
        if self.is_static:
            editable = False
        else:
            editable = in_student_view

        return {
            "display_name": self.display_name,
            "in_student_view": in_student_view,
            "editable": editable,
            "xblock_id": self.scope_ids.usage_id.block_id,
            "is_static": self.is_static,
            "is_static_field": self.fields["is_static"],
            "can_submit_assignment": self.submit_allowed(),
            "score": self.score,
            "max_score": self.max_score(),
        }

    def get_js_context(self, user, context):
        """
        Return the context for the student view.

        Args:
            user: The current user

        Returns:
            dict: The context for the student view
        """
        return {
            "author": user.full_name,
            "max_points": self.points,
            "mind_map": self.get_current_mind_map(),
            "editable": context["editable"],
            "xblock_id": self.scope_ids.usage_id.block_id,
        }

    def student_view(self, _context=None) -> Fragment:
        """
        The primary view of the MindMapXBlock, shown to students when viewing courses.

        Args:
            _context (dict, optional): Context for the template. Defaults to None.

        Returns:
            Fragment: The fragment to render
        """
        user = self.get_current_user()
        context = self.get_context(user)
        js_context = self.get_js_context(user, context)

        if not context["can_submit_assignment"]:
            context["editable"] = False
            js_context["editable"] = False

        if self.show_staff_grading_interface():
            context["is_instructor"] = True

        frag = self.load_fragment("mindmap", context)

        frag.add_javascript(self.resource_string("public/js/src/requiredModules.js"))
        frag.initialize_js('MindMapXBlock', json_args=js_context)

        return frag

    def studio_view(self, context=None) -> Fragment:
        """
        The studio view of the MindMapXBlock, shown to instructors.

        Args:
            context (dict, optional): Context for the template. Defaults to None.

        Returns:
            Fragment: The fragment to render
        """
        user = self.get_current_user()
        context = self.get_context(user)
        js_context = self.get_js_context(user, context)

        context.update({
            "editable": True,
            "points": self.points,
            "points_field": self.fields["points"],
            "weight": self.weight,
            "weight_field": self.fields["weight"],
        })

        frag = self.load_fragment("mindmap_edit", context)

        frag.initialize_js('MindMapXBlock', json_args=js_context)

        return frag

    def load_fragment(self, file_name, context):
        """
        Generic function to generate a fragment.
        """
        frag = Fragment()
        frag.add_content(self.render_template(f"public/html/{file_name}.html", context))
        frag.add_css(self.resource_string("public/css/mindmap.css"))
        frag.add_css(self.resource_string("public/css/submissions.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(
                self.runtime.local_resource_url(self, statici18n_js_url)
            )

        frag.add_javascript(self.resource_string(f"public/js/src/{file_name}.js"))

        return frag

    def get_current_mind_map(self) -> dict:
        """
        Return the current mind map content.

        Returns:
            dict: The current mind map content.
            None: If the file does not exist.
        """
        if self.mindmap_student_body and not self.is_static:
            return self.mindmap_student_body
        return self.mindmap_body

    def show_staff_grading_interface(self) -> bool:
        """
        Return if current user is staff and not in studio.

        Returns:
            bool: True if current user is instructor and not in studio.
        """
        in_studio_preview = self.scope_ids.user_id is None
        return self.is_instructor() and not in_studio_preview

    def is_instructor(self) -> bool:
        """
        Check if user role is instructor.

        Returns:
            bool: True if user role is instructor.
        """
        return self.get_current_user().opt_attrs.get(ATTR_KEY_USER_ROLE) == "instructor"

    @XBlock.json_handler
    def studio_submit(self, data, _suffix="") -> None:
        """
        Called when submitting the form in Studio.

        Args:
            data (dict): The necessary configuration data.
            _suffix (str, optional): Defaults to "".
        """
        self.display_name = data.get("display_name")
        self.is_static = data.get("is_static")
        self.mindmap_body = data.get("mind_map")

        # We need to validate the points and weight fields ourselves because
        # Studio doesn't do it for us.

        points = data.get("points", self.points)
        weight = data.get("weight", self.weight)
        self.points, self.weight = self.validate_score(points, weight)

    @XBlock.json_handler
    def save_assignment(self, data, _suffix="") -> dict:
        """
        Save a mind map JSON structure into the block state for the user.

        Args:
            data (dict): The necessary data to upload the file
            _suffix (str, optional): Defaults to "".

        Returns:
            dict: A dictionary containing the handler result.
        """
        self.mindmap_student_body = data.get("mind_map")
        return {
            "success": True,
        }

    @XBlock.json_handler
    def submit_assignment(self, data, _suffix="") -> dict:
        """
        Submit a student's saved submission. This prevents further saves for the
        given block, and makes the submission available to instructors for grading

        Args:
            request (Request): The request object
            _suffix (str, optional): Defaults to "".

        Returns:
            dict: A dictionary containing the handler result.
        """
        # Lazy import: import here to avoid app not ready errors
        from submissions.api import create_submission  # pylint: disable=import-outside-toplevel

        require(self.submit_allowed())

        self.mindmap_student_body = data.get("mind_map")
        answer = {
            "mindmap_student_body": json.dumps(self.mindmap_student_body),
        }
        student_item_dict = self.get_student_item_dict()
        create_submission(student_item_dict, answer)

        self.submitted = True

        return {
            "success": True,
        }

    @XBlock.json_handler
    def get_instructor_grading_data(self, _, _suffix="") -> dict:
        """Return student assignment information for display on the grading screen.

        Args:
            request (Request): The request object.
            _suffix (str, optional): Defaults to "".

        Returns:
            dict: A dictionary containing student assignment information.
        """
        require(self.is_instructor())

        def get_student_data() -> dict:
            """
            Returns a dict of student assignment information along with
            annotated file name, student id and module id, this
            information will be used on grading screen
            """
            # Lazy import: import here to avoid app not ready errors
            from submissions.models import StudentItem as SubmissionsStudent  # pylint: disable=import-outside-toplevel

            students = SubmissionsStudent.objects.filter(
                course_id=self.course_id, item_id=self.block_id
            )
            for student in students:
                submission = self.get_submission(student.student_id)
                if not submission:
                    continue
                user = user_by_anonymous_id(student.student_id)
                score = self.get_score(student.student_id)
                yield {
                    "student_id": student.student_id,
                    "submission_id": submission["uuid"],
                    "answer_body": submission["answer"],
                    "username": user.username,
                    "timestamp": submission["created_at"].strftime(
                        DateTime.DATETIME_FORMAT
                    ),
                    "score": score,
                    "submitted": self.submitted,
                }

        return {
            "assignments": list(get_student_data()),
            "max_score": self.max_score(),
            "display_name": self.display_name,
        }

    @XBlock.json_handler
    def enter_grade(self, data, _suffix="") -> dict:
        """
        Persist a score for a student given by instructors.

        Args:
            data (dict): The necessary data to enter a grade to a specific submission.
            _suffix (str, optional): Defaults to "".

        Returns:
            dict: A dictionary containing the handler result.
        """
        # Lazy import: import here to avoid app not ready errors
        from submissions.api import set_score  # pylint: disable=import-outside-toplevel

        require(self.is_instructor())

        score = int(data.get("grade"))
        uuid = data.get("submission_id")
        if not score or not uuid:
            raise JsonHandlerError(400, "Missing required parameters")
        if score > self.max_score():
            raise JsonHandlerError(400, "Score cannot be greater than max score")

        set_score(uuid, score, self.max_score())

        return {
            "success": True,
        }

    @XBlock.json_handler
    def remove_grade(self, data, _suffix="") -> dict:
        """
        Persist a score for a student given by instructors.

        Args:
            data (dict): The necessary data to remove the grade from a specific submission.
            _suffix (str, optional): Defaults to "".

        Returns:
            dict: A dictionary containing the handler result.
        """
        # Lazy import: import here to avoid app not ready errors
        from submissions.api import reset_score  # pylint: disable=import-outside-toplevel

        require(self.is_instructor())

        student_id = data.get("student_id")
        if not student_id:
            raise JsonHandlerError(400, "Missing required parameters")

        reset_score(student_id, self.block_course_id, self.block_id)

        return {
            "success": True,
        }

    @staticmethod
    def validate_score(points: int, weight: int) -> None:
        """
        Validate a score.

        Args:
            score (int): The score to validate.
            max_score (int): The maximum score.
        """
        try:
            points = int(points)
        except ValueError as exc:
            raise JsonHandlerError(400, "Points must be an integer") from exc

        if points < 0:
            raise JsonHandlerError(400, "Points must be a positive integer")

        if weight:
            try:
                weight = float(weight)
            except ValueError as exc:
                raise JsonHandlerError(400, "Weight must be a decimal number") from exc
            if weight < 0:
                raise JsonHandlerError(400, "Weight must be a positive decimal number")

        return points, weight

    def submit_allowed(self) -> bool:
        """
        Return whether student is allowed to submit an assignment.
        A student is allowed to submit an assignment if:
        - The due date has not passed for the assignment
        - The student has not already submitted
        - The student has not already received a score

        Returns:
            bool: True if student is allowed to submit an assignment.
        """
        return (
            not self.past_due()
            and self.score is None
            and not self.submitted
        )

    def get_score(self, student_id=None) -> int:
        """
        Return student's current score.

        Args:
            student_id (str, optional): The student id to get the score for.

        Returns:
            int: The student's current score.
        """
        # Lazy import: import here to avoid app not ready errors
        from submissions.api import get_score  # pylint: disable=import-outside-toplevel

        score = get_score(self.get_student_item_dict(student_id))
        if score:
            return score["points_earned"]

        return None

    def get_submission(self, student_id=None) -> dict:
        """
        Get student's most recent submission.

        Args:
            student_id (str, optional): The student id to get the submission for.

        Returns:
            dict: The student's most recent submission.
        """
        # Lazy import: import here to avoid app not ready errors
        from submissions.api import get_submissions  # pylint: disable=import-outside-toplevel

        submissions = get_submissions(
            self.get_student_item_dict(student_id)
        )
        if submissions:
            return submissions[0]

        return None

    def get_student_item_dict(self, student_id=None) -> dict:
        """
        Returns dict required by the submissions app for creating and
        retrieving submissions for a particular student.

        Args:
            student_id (str, optional): The student id to get the student item for.

        Returns:
            dict: The student item dict.
        """
        if not student_id:
            student_id = self.get_current_user().opt_attrs.get(ATTR_KEY_ANONYMOUS_USER_ID)

        return {
            "student_id": student_id,
            "course_id": self.block_course_id,
            "item_id": self.block_id,
            "item_type": ITEM_TYPE,
        }

    def past_due(self) -> bool:
        """
        Return whether due date has passed.

        Returns:
            bool: True if due date has passed.
        """
        due = get_extended_due_date(self)
        try:
            graceperiod = self.graceperiod
        except AttributeError:
            # graceperiod and due are defined in InheritanceMixin
            # It's used automatically in edX but the unit tests will need to mock it out
            graceperiod = None

        if graceperiod is not None and due:
            close_date = due + graceperiod
        else:
            close_date = due

        if close_date is not None:
            return utcnow() > close_date
        return False

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("MindMapXBlock",
             """<mindmap/>
             """),
            ("Multiple MindMapXBlock",
             """<vertical_demo>
                <mindmap/>
                <mindmap/>
                <mindmap/>
                </vertical_demo>
             """),
        ]

    @staticmethod
    def _get_statici18n_js_url():
        """
        Returns the Javascript translation file for the currently selected language, if any.
        Defaults to English if available.
        """
        locale_code = translation.get_language()
        if locale_code is None:
            return None
        text_js = 'public/js/translations/{locale_code}/text.js'
        lang_code = locale_code.split('-')[0]
        for code in (locale_code, lang_code, 'en'):
            if pkg_resources.resource_exists(
                    loader.module_name, text_js.format(locale_code=code)):
                return text_js.format(locale_code=code)
        return None

    @staticmethod
    def get_dummy():
        """
        Dummy method to generate initial i18n
        """
        return translation.gettext_noop('Dummy')


def require(assertion):
    """
    Raises PermissionDenied if assertion is not true.
    """
    if not assertion:
        raise PermissionDenied
