"""XBlock to create and save Mind Maps in Open edX."""

from __future__ import annotations

import json
import logging
from http import HTTPStatus
from typing import Tuple

import boto3
import pkg_resources
from django.conf import settings
from django.template import Context, Template
from django.utils import translation
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblockutils.resources import ResourceLoader

log = logging.getLogger(__name__)


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
class MindMapXBlock(XBlock):
    """
    Mind Map XBlock provides a way to create and save mind maps in a course.
    """
    display_name = String(
        display_name="Display Name",
        default="Mind Map",
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

    def student_view(self, _context=None) -> Fragment:
        """
        The primary view of the MindMapXBlock, shown to students when viewing courses.

        Args:
            _context (dict, optional): Context for the template. Defaults to None.

        Returns:
            Fragment: The fragment to render
        """
        user = self.get_current_user()
        anonymous_user_id = self.anonymous_user_id(user)
        show_mindmap = self.is_student(user) or self.user_is_staff(user)
        js_context = {
            "author": user.full_name,
            "hasMindMap": True
        }
       
        error_message = None

        if show_mindmap:
            try:
                mind_map = self.get_current_mind_map(anonymous_user_id)
                js_context.update({"mind_map": mind_map})
            except Exception as error: # pylint: disable=broad-except
                log.exception("Error while setting up student view of MindMapXBlock")
                error_message = str(error)

        context = {"show_mindmap": show_mindmap, "error_message": error_message}

        html = self.render_template("static/html/mindmap.html", context)
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/mindmap.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(self.runtime.local_resource_url(self, statici18n_js_url))
        
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
        }

        html = self.render_template("static/html/mindmap_edit.html", context)
        frag = Fragment(html)
        frag.add_css(self.resource_string("static/css/mindmap.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(self.runtime.local_resource_url(self, statici18n_js_url))

        frag.add_javascript(self.resource_string("static/js/src/mindmapEdit.js"))
        frag.initialize_js("MindMapXBlock")
        return frag

    @staticmethod
    def connect_to_s3() -> Tuple[boto3.client, str]:
        """
        Create a connection to S3.

        Raises:
            MisconfiguredMindMapService: If the AWS settings are not configured.

        Returns:
            Tuple[boto3.client, str]: The S3 client and the bucket name.
        """
        aws_access_key_id = getattr(settings, "AWS_ACCESS_KEY_ID", None)
        aws_secret_access_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
        aws_bucket_name = getattr(settings, "FILE_UPLOAD_STORAGE_BUCKET_NAME", None)

        if not aws_access_key_id or not aws_secret_access_key or not aws_bucket_name:
            raise MisconfiguredMindMapService("AWS settings not configured")

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        return s3_client, aws_bucket_name

    def get_file_key(self, anonymous_user_id: str) -> str:
        """
        Return the key (path) to save and retrieve the file in S3.

        Returns:
            str: The key (path) to use in S3.
        """
        block_id = self.location.block_id # pylint: disable=no-member
        return f"mindmaps/{block_id}/{anonymous_user_id}/mindmap.json"

    def file_exists_in_s3(self, anonymous_user_id: str) -> bool:
        """
        Check if the file exists in S3.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        s3_client, aws_bucket_name = self.connect_to_s3()
        try:
            s3_client.head_object(
                Bucket=aws_bucket_name,
                Key=self.get_file_key(anonymous_user_id)
            )
        except s3_client.exceptions.ClientError as error:
            if int(error.response["Error"]["Code"]) == HTTPStatus.NOT_FOUND:
                return False
            log.error(error)
            raise error
        return True

    def get_current_mind_map(self, anonymous_user_id: str) -> dict | None:
        """
        Return the current mind map content.

        Returns:
            dict: The mind map content.
        """
        if not self.file_exists_in_s3(anonymous_user_id):
            return None

        s3_client, aws_bucket_name = self.connect_to_s3()
        try:
            response = s3_client.get_object(
                Bucket=aws_bucket_name,
                Key=self.get_file_key(anonymous_user_id)
            )
            json_data = response["Body"].read().decode("utf-8")
        except s3_client.exceptions.ClientError as error:
            raise error
        return json.loads(json_data)

    @XBlock.json_handler
    def upload_file(self, data, suffix="") -> None: # pylint: disable=unused-argument
        """
        Uploads a mind map file to S3.

        Args:
            data (dict): The data to upload
            suffix (str, optional): Defaults to "".
        """
        user = self.get_current_user()
        anonymous_user_id = self.anonymous_user_id(user)
        s3_client, aws_bucket_name = self.connect_to_s3()

        s3_client.put_object(
            Bucket=aws_bucket_name,
            Key=self.get_file_key(anonymous_user_id),
            Body=data.get("mind_map")
        )

    @XBlock.json_handler
    def studio_submit(self, data, suffix=""):  # pylint: disable=unused-argument
        """
        Called when submitting the form in Studio.
        """
        self.display_name = data.get("display_name")

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
            loader = ResourceLoader(__name__)
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
