"""XBlock to create and save Mind Maps in Open edX."""

from __future__ import annotations

import json
import logging

import pkg_resources
from django.core.files.base import ContentFile
from django.template import Context, Template
from django.utils import translation
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Boolean, Scope, String
from xblockutils.resources import ResourceLoader

from mindmap.utils import get_mindmap_storage, _

log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


class MisconfiguredMindMapService(Exception):
    """Exception raised when the MindMap service is misconfigured."""

    def init__(self, message="Mind Map service is misconfigured"):
        """
        Initialize the exception.

        Args:
            message (str, optional): The error message for the misconfigured mind map service error.
        """
        super().__init__(message)


@XBlock.wants("user")
@XBlock.needs("i18n")
class MindMapXBlock(XBlock):
    """
    Mind Map XBlock provides a way to create and save mind maps in a course.
    """
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

    def get_current_user(self):
        """
        Get the current user.
        """
        return self.runtime.service(self, "user").get_current_user()

    def anonymous_user_id(self, user) -> str:
        """
        Return the anonymous user ID of the user.
        """
        return user.opt_attrs.get("edx-platform.anonymous_user_id")

    def user_is_staff(self, user) -> bool:
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

    def render_template(self, template_path: str, context=None) -> str:
        """
        Render the template with the provided context.

        Args:
            template_path (str): The path to the template
            context(dict, optional): The context to render in the template

        Returns:
            str: The rendered template
        """
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    def get_student_view_context(self, user):
        """
        Return the context for the student view.

        Args:
            user: The current user

        Returns:
            dict: The context for the student view
        """
        anonymous_user_id = self.anonymous_user_id(user)
        in_student_view = self.is_student(user) or self.user_is_staff(user)
        path_prefix = (
            anonymous_user_id
            if in_student_view and not self.is_static
            else "instructor"
        )
        editable = in_student_view != self.is_static

        return {
            "in_student_view": in_student_view,
            "path_prefix": path_prefix,
            "editable": editable,
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
        student_view_context = self.get_student_view_context(user)
        js_context = {"author": user.full_name}
        error_message = None

        if student_view_context["in_student_view"] or self.is_static:
            try:
                mind_map = self.get_current_mind_map(
                    student_view_context["path_prefix"]
                )
                js_context.update(
                    {"mind_map": mind_map, "editable": student_view_context["editable"]}
                )
            except Exception as error: # pylint: disable=broad-except
                log.exception("Error while setting up student view of MindMapXBlock")
                error_message = str(error)

        context = {
            "in_student_view": student_view_context["in_student_view"],
            "is_static": self.is_static,
            "error_message": error_message,
        }

        frag = Fragment()
        frag.add_css(self.resource_string("static/css/mindmap.css"))
        frag.add_content(loader.render_django_template(
            "static/html/mindmap.html",
            context,
            i18n_service=self.runtime.service(self, 'i18n')
        ))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(
                self.runtime.local_resource_url(self, statici18n_js_url)
            )

        frag.add_javascript(self.resource_string("static/js/src/requiredModules.js"))
        frag.add_javascript(self.resource_string("static/js/src/mindmap.js"))
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
        context = {
            "display_name": self.display_name,
            "is_static": self.is_static,
            "is_static_field": self.fields["is_static"],
        }

        frag = Fragment()
        frag.add_content(loader.render_django_template(
            "static/html/mindmap_edit.html",
            context,
            i18n_service=self.runtime.service(self, 'i18n')
        ))
        frag.add_css(self.resource_string("static/css/mindmap.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(
                self.runtime.local_resource_url(self, statici18n_js_url)
            )

        frag.add_javascript(self.resource_string("static/js/src/mindmapEdit.js"))
        frag.initialize_js("MindMapXBlock")
        return frag

    def get_file_key(self, path_prefix: str) -> str:
        """
        Return the key (path) to save and retrieve the file in S3.

        Args:
            path_prefix (str):
                The path prefix to use in the key (path).
                In the case of students, it is the anonymous user ID.

        Returns:
            str: The key (path) to use in S3.
        """
        block_id = self.scope_ids.usage_id.block_id

        if path_prefix == "instructor":
            return f"mindmaps/instructors/{block_id}/mindmap.json"

        return f"mindmaps/students/{block_id}/{path_prefix}/mindmap.json"

    def get_current_mind_map(self, path_prefix: str) -> dict | None:
        """
        Return the current mind map content.

        Args:
            path_prefix (str): The path prefix to use in the key (path).

        Returns:
            dict: The current mind map content.
            None: If the file does not exist.
        """
        mindmap_storage = get_mindmap_storage()

        try:
            file = mindmap_storage.open(self.get_file_key(path_prefix))
            json_data = file.read().decode("utf-8")
        except IOError:
            return None
        return json.loads(json_data)

    @XBlock.json_handler
    def upload_file(self, data, _suffix="") -> None:
        """
        Uploads a mind map file to S3.

        Args:
            data (dict): The necessary data to upload the file
            _suffix (str, optional): Defaults to "".
        """
        if data.get("path_prefix") == "student":
            user = self.get_current_user()
            data["path_prefix"] = self.anonymous_user_id(user)

        mindmap_storage = get_mindmap_storage()

        mindmap_storage.save(
            self.get_file_key(data.get("path_prefix")),
            ContentFile(data.get("mind_map").encode("utf-8"))
        )

    @XBlock.json_handler
    def studio_submit(self, data, _suffix=""):
        """
        Called when submitting the form in Studio.
        """
        self.display_name = data.get("display_name")
        self.is_static = data.get("is_static")

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
