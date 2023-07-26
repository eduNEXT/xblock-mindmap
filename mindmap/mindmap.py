"""XBlock to create and save Mind Maps in Open edX."""

import json
import pkg_resources

import boto3
from django.conf import settings
from django.template import Context, Template
from django.utils import translation
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblockutils.resources import ResourceLoader


AWS_BUCKET_NAME = getattr(settings, "AWS_BUCKET_NAME", None)


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

    def anonymous_user_id(self, user) -> str:
        """
        Return the anonymous user ID of the user.
        """
        return user.opt_attrs.get("edx-platform.anonymous_user_id")

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
        mind_map = self.get_mind_map()
        js_context = {'mind_map': mind_map} if mind_map else None

        html = self.render_template("static/html/mindmap.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/mindmap.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(self.runtime.local_resource_url(self, statici18n_js_url))

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

    def connect_to_s3(self):
        """
        Create a connection to S3.

        Returns:
            boto3.client: The connection to S3.
        """
        AWS_ACCESS_KEY_ID = getattr(settings, "AWS_ACCESS_KEY_ID", None)
        AWS_SECRET_ACCESS_KEY_ID = getattr(settings, "AWS_SECRET_ACCESS_KEY_ID", None)

        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY_ID,
        )

    def get_key(self) -> str:
        """
        Return the key (path) to use in S3.

        Returns:
            str: The key (path) to use in S3.
        """
        user_service = self.runtime.service(self, "user")
        user = user_service.get_current_user()
        anonymous_user_id = self.anonymous_user_id(user)
        block_id = self.location.block_id # pylint: disable=no-member
        return f"{block_id}/{anonymous_user_id}/mindmap.json"

    def file_exists(self) -> bool:
        """
        Check if the file exists in S3.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        s3_client = self.connect_to_s3()
        try:
            s3_client.head_object(Bucket=AWS_BUCKET_NAME, Key=self.get_key())
        except s3_client.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise e
        return True

    def get_mind_map(self) -> dict:
        """
        Return the mind map content.

        Returns:
            dict: The mind map content.
        """
        if not self.file_exists():
            return {}

        s3_client = self.connect_to_s3()
        response = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=self.get_key())
        json_data = response["Body"].read().decode("utf-8")
        return json.loads(json_data)

    @XBlock.json_handler
    def upload_file(self, data, suffix="") -> None: # pylint: disable=unused-argument
        """
        Uploads a mind map file to S3.

        Args:
            data (dict): The data to upload
            suffix (str, optional): Defaults to "".
        """
        s3_client = self.connect_to_s3()
        s3_client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=self.get_key(),
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
