"""XBlock to create and save Mind Maps in Open edX."""

from __future__ import annotations

import logging

import pkg_resources
from django.utils import translation
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Boolean, Dict, Scope, String
from xblockutils.resources import ResourceLoader

from mindmap.utils import _

log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


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

    mindmap_body = Dict(
        help=_(
            "The body of the mind map. It is a dictionary with the following structure: "
            "{'root': {'text': 'Root', 'children': [{'text': 'Child 1', 'children': []}]}}"
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
                    "topic": "Root"}
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

        frag = self.load_fragment("mindmap", context)

        frag.add_javascript(self.resource_string("static/js/src/requiredModules.js"))
        frag.initialize_js('MindMapXBlock', json_args=self.get_js_context(user, context))

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
        context.update({
            "editable": True
        })

        frag = self.load_fragment("mindmap_edit", context)

        frag.initialize_js('MindMapXBlock', json_args=self.get_js_context(user, context))

        return frag

    def load_fragment(self, file_name, context):
        """
        Generic function to generate a fragment.
        """
        frag = Fragment()
        frag.add_content(self.render_template(f"static/html/{file_name}.html", context))
        frag.add_css(self.resource_string("static/css/mindmap.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(
                self.runtime.local_resource_url(self, statici18n_js_url)
            )

        frag.add_javascript(self.resource_string(f"static/js/src/{file_name}.js"))

        return frag

    def get_current_mind_map(self) -> dict:
        """
        Return the current mind map content.

        Args:


        Returns:
            dict: The current mind map content.
            None: If the file does not exist.
        """
        if self.mindmap_student_body and not self.is_static:
            return self.mindmap_student_body
        return self.mindmap_body

    @XBlock.json_handler
    def upload_file(self, data, _suffix="") -> None:
        """
        Uploads a mind map file to S3.

        Args:
            data (dict): The necessary data to upload the file
            _suffix (str, optional): Defaults to "".
        """
        self.mindmap_student_body = data.get("mind_map")
        return {"success": True}

    @XBlock.json_handler
    def studio_submit(self, data, _suffix=""):
        """
        Called when submitting the form in Studio.
        """
        self.display_name = data.get("display_name")
        self.is_static = data.get("is_static")
        self.mindmap_body = data.get("mind_map")

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
