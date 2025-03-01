"""XBlock to create and save Mind Maps in Open edX."""

from __future__ import annotations

import json
import logging
from enum import Enum

from importlib.resources import files as importlib_files
from django.core.exceptions import PermissionDenied
from django.utils import translation
from web_fragments.fragment import Fragment
from xblock.completable import CompletableXBlockMixin
from xblock.core import XBlock
from xblock.exceptions import JsonHandlerError
from xblock.fields import Boolean, DateTime, Dict, Integer, Scope, String
from xblockutils.resources import ResourceLoader

from mindmap.edxapp_wrapper.student import (
    user_by_anonymous_id,
    student_module as StudentModule,
)
from mindmap.edxapp_wrapper.xmodule import get_extended_due_date
from mindmap.utils import _, utcnow

log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)

ITEM_TYPE = "mindmap"
ATTR_KEY_ANONYMOUS_USER_ID = 'edx-platform.anonymous_user_id'
ATTR_KEY_USER_ROLE = 'edx-platform.user_role'


class SubmissionStatus(Enum):
    """Submission status enum"""
    NOT_ATTEMPTED = _("Not attempted")
    SUBMITTED = _("Submitted")
    COMPLETED = _("Completed")


@XBlock.wants("user")
@XBlock.needs("i18n")
class MindMapXBlock(XBlock, CompletableXBlockMixin):
    """
    Mind Map XBlock provides a way to create and save mind maps in a course.
    """

    has_score = Boolean(
        display_name=_("Is scorable?"),
        help=_(
            "Whether the component is scorable. If is scorable, the student "
            "can submit the mind map and receive a score from the instructor. "
            "If it is not scorable, the student only can save the mind map. "
            "WARNING: Changing from scorable to not scorable, the progress "
            "of the students who have already been assigned a grade will not "
            "be reset."
        ),
        default=True,
        scope=Scope.settings,
    )

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

    weight = Integer(
        display_name=_("Problem Weight"),
        help=_(
            "Defines the number of points this problem is worth. If "
            "the value is not set, the problem is worth one point."
        ),
        default=10,
        scope=Scope.settings,
    )

    raw_score = Integer(
        display_name=_("Raw score"),
        help=_("The raw score for the assignment."),
        default=None,
        scope=Scope.user_state,
    )

    points = Integer(
        display_name=_("Maximum score"),
        help=_("Maximum grade score given to assignment by staff."),
        default=100,
        scope=Scope.settings,
    )

    submission_status = String(
        display_name=_("Submission status"),
        help=_("The submission status of the assignment."),
        default=SubmissionStatus.NOT_ATTEMPTED.value,
        scope=Scope.user_state,
    )

    has_author_view = True

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

    def get_weighted_score(self, student_id=None):
        """
        Return weighted score from submissions.
        """
        # Lazy import: import here to avoid app not ready errors
        from submissions.api import get_score  # pylint: disable=import-outside-toplevel

        score = get_score(self.get_student_item_dict(student_id))
        if score:
            return score["points_earned"]

        return None

    def max_score(self):
        """
        Return the maximum score.
        """
        return self.weight

    def get_current_user(self):
        """
        Get the current user.
        """
        return self.runtime.service(self, "user").get_current_user()

    @property
    def is_student(self) -> bool:
        """
        Check if the current user is a student.
        """
        return self.get_current_user().opt_attrs.get("edx-platform.user_role") == "student"

    @property
    def is_course_team(self) -> bool:
        """
        Check if the user is part of the course team (instructor or staff).
        """
        user = self.get_current_user()
        is_course_staff = user.opt_attrs.get("edx-platform.user_is_staff")
        is_instructor = user.opt_attrs.get(ATTR_KEY_USER_ROLE) == "instructor"
        return is_course_staff or is_instructor

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        return importlib_files(__package__).joinpath(path).read_text(encoding="utf-8")

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

    def get_context(self, in_student_view=False):
        """
        Return the context for the student view.

        Args:
            user: The current user

        Returns:
            dict: The context for the student view
        """
        if self.is_static:
            editable = False
        else:
            editable = in_student_view or self.is_course_team

        context = {
            "display_name": self.display_name,
            "has_score": self.has_score,
            "is_static": self.is_static,
            "has_score_field": self.fields["has_score"],
            "is_static_field": self.fields["is_static"],
            "in_student_view": in_student_view,
            "editable": editable,
            "xblock_id": self.scope_ids.usage_id.block_id,
            "submission_status": self.submission_status,
        }

        if self.has_score:
            context.update({
                "can_submit_assignment": self.submit_allowed(),
                "raw_score": self.raw_score,
                "max_raw_score": self.points,
                "weight": self.weight,
                "weighted_score": self.get_weighted_score(),
            })

        return context

    def get_js_context(self, user, context):
        """
        Return the context for the student view.

        Args:
            user: The current user

        Returns:
            dict: The context for the student view
        """
        return {
            "raw_score": self.raw_score,
            "weighted_score": self.get_weighted_score(),
            "author": user.full_name,
            "max_raw_score": self.points,
            "weight": self.weight,
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
        context = self.get_context(in_student_view=True)
        js_context = self.get_js_context(user, context)

        if context["has_score"] and not context["can_submit_assignment"]:
            context["editable"] = False
            js_context["editable"] = False

        if self.is_course_team:
            context["is_instructor"] = True

        frag = self.load_fragment("mindmap", context)

        frag.add_javascript(self.resource_string("public/js/src/requiredModules.js"))
        frag.initialize_js('MindMapXBlock', json_args=js_context)

        return frag

    def author_view(self, _context=None) -> Fragment:
        """
        The primary view of the MindMapXBlock, shown to authors in Studio.

        Args:
            _context (dict, optional): Context for the template. Defaults to None.

        Returns:
            Fragment: The fragment to render
        """
        user = self.get_current_user()
        context = self.get_context()
        js_context = self.get_js_context(user, context)
        context["editable"] = False
        js_context["editable"] = False

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
        context = self.get_context()
        js_context = self.get_js_context(user, context)

        context.update({
            "editable": True,
            "points": self.points,
            "points_field": self.fields["points"],
            "weight": self.weight,
            "weight_field": self.fields["weight"],
        })
        js_context.update({
            "editable": True,
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
        self.has_score = data.get("has_score")
        self.icon_class = "problem" if self.has_score else ITEM_TYPE # pylint: disable=attribute-defined-outside-init

        # We need to validate the points and weight fields ourselves because
        # Studio doesn't do it for us.
        if self.has_score:
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
        self.emit_completion(1)

        self.submission_status = SubmissionStatus.SUBMITTED.value

        return {
            "success": True,
        }

    def get_or_create_student_module(self, user):
        """
        Gets or creates a StudentModule for the given user for this block

        Returns:
            StudentModule: A StudentModule object
        """
        # pylint: disable=no-member
        student_module, created = StudentModule().objects.get_or_create(
            course_id=self.course_id,
            module_state_key=self.location,
            student=user,
            defaults={
                "state": "{}",
                "module_type": self.category,
            },
        )
        if created:
            log.info(
                "Created student module %s [course: %s] [student: %s]",
                student_module.module_state_key,
                student_module.course_id,
                student_module.student.username,
            )
        return student_module

    @XBlock.json_handler
    def get_instructor_grading_data(self, _, _suffix="") -> dict:
        """Return student assignment information for display on the grading screen.

        Args:
            request (Request): The request object.
            _suffix (str, optional): Defaults to "".

        Returns:
            dict: A dictionary containing student assignment information.
        """
        require(self.is_course_team)

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
                student_module = self.get_or_create_student_module(user)
                state = json.loads(student_module.state)
                raw_score = self.get_raw_score(student.student_id)

                if state.get("submission_status") in [
                    SubmissionStatus.COMPLETED.value, SubmissionStatus.SUBMITTED.value
                ]:
                    yield {
                        "module_id": student_module.id,
                        "student_id": student.student_id,
                        "submission_id": submission["uuid"],
                        "answer_body": submission["answer"],
                        "username": user.username,
                        "timestamp": submission["created_at"].strftime(
                            DateTime.DATETIME_FORMAT
                        ),
                        "raw_score": state.get("raw_score", raw_score),
                        "max_raw_score": self.points,
                        "weight": self.weight,
                        "weighted_score": self.get_weighted_score(student.student_id),
                        "submission_status": state.get("submission_status"),
                    }

        return {
            "assignments": list(get_student_data()),
            "max_raw_score": self.points,
            "weight": self.weight,
            "display_name": self.display_name,
        }

    def get_student_module(self, module_id):
        """
        Returns a StudentModule that matches the given id

        Args:
            module_id (int): The module id

        Returns:
            StudentModule: A StudentModule object
        """
        return StudentModule().objects.get(pk=module_id)

    def update_student_state(self, module_id: int, submission_status: str, raw_score: int=None) -> None:
        """
        Updates the state of a student.

        Args:
            module_id (int): The module id
            submission_status (str): The submission status
        """
        module = self.get_student_module(module_id)
        state = json.loads(module.state)
        state["submission_status"] = submission_status
        if raw_score is not None:
            state["raw_score"] = raw_score
        module.state = json.dumps(state)
        module.save()

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

        require(self.is_course_team)

        raw_score = int(data.get("grade", 0))
        uuid = data.get("submission_id")
        if not uuid:
            raise JsonHandlerError(400, "Missing required parameters")
        if raw_score > self.points:
            raise JsonHandlerError(400, "Score cannot be greater than max score")

        set_score(uuid, round((raw_score / self.points) * self.weight), self.weight)

        self.update_student_state(
            data.get("module_id"), SubmissionStatus.COMPLETED.value, raw_score=raw_score,
        )

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

        require(self.is_course_team)

        student_id = data.get("student_id")
        if not student_id:
            raise JsonHandlerError(400, "Missing required parameters")

        reset_score(student_id, self.block_course_id, self.block_id)

        self.update_student_state(
            data.get("module_id"), SubmissionStatus.SUBMITTED.value
        )

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
                weight = int(weight)
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
            and self.raw_score is None
            and self.submission_status == SubmissionStatus.NOT_ATTEMPTED.value
        )

    def get_raw_score(self, student_id=None) -> int:
        """
        Return student's current score.

        Args:
            student_id (str, optional): The student id to get the score for.

        Returns:
            int: The student's current score.
        """
        weighted_score = self.get_weighted_score(student_id)
        if weighted_score:
            return round((weighted_score * self.points) / self.weight)

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
        for code in (translation.to_locale(locale_code), lang_code, 'en'):
            if importlib_files(__package__).joinpath(text_js.format(locale_code=code)).exists():
                return text_js.format(locale_code=code)
        return None


def require(assertion):
    """
    Raises PermissionDenied if assertion is not true.
    """
    if not assertion:
        raise PermissionDenied
