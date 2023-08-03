"""
Tests for the LimeSurveyXBlock definition class.
"""
import json
from unittest import TestCase
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError
from django.test.utils import override_settings

from mindmap.mindmap import (
    MindMapXBlock,
    MisconfiguredMindMapService,
)


class TestMindMapXBlock(TestCase):
    """
    Test suite for the MindMapXBlock definition class.
    """

    def setUp(self) -> None:
        """
        Set up the test suite.
        """
        self.xblock = MindMapXBlock(
            runtime=Mock(), field_data=Mock(), scope_ids=Mock()
        )
        self.student = Mock()
        self.anonymous_user_id = "test-anonymous-user-id"
        self.xblock.anonymous_user_id = Mock()
        self.xblock.user_is_staff = Mock()
        self.xblock.is_student = Mock()
        self.xblock.get_current_user = Mock()
        self.xblock.get_current_mind_map = Mock()
        self.xblock.anonymous_user_id = Mock()
        self.xblock.render_template = Mock(return_value="Test render")
        self.xblock.resource_string = Mock()
        self.xblock.display_name = "Test MindMap"

    @patch("mindmap.mindmap.Fragment.initialize_js")
    def test_student_view_with_mind_map(self, initialize_js_mock):
        """
        Check student view is rendered correctly with a mind map.

        Expected result:
            - The student view is set up for the render with the student.
        """
        mind_map = {"data": [{ "id": "root", "isroot": True, "topic": "Root" }]}
        self.xblock.is_static = False
        self.xblock.anonymous_user_id.return_value = self.anonymous_user_id
        self.xblock.is_student.return_value = True
        self.xblock.user_is_staff.return_value = False
        self.xblock.get_current_user.return_value = self.student
        self.xblock.get_current_mind_map.return_value = mind_map
        expected_context = {
            "in_student_view": True,
            "is_static": False,
            "error_message": None,
        }
        expected_js_context = {
            "author": self.student.full_name,
            "mind_map": mind_map,
            "editable": True,
        }

        self.xblock.student_view()

        self.xblock.render_template.assert_called_once_with(
            "static/html/mindmap.html", expected_context
        )
        initialize_js_mock.assert_called_once_with(
            'MindMapXBlock', json_args=expected_js_context
        )

    @patch("mindmap.mindmap.Fragment.initialize_js")
    def test_student_view_empty_mind_map(self, initialize_js_mock):
        """
        Check student view is rendered correctly with an empty mind map (None)

        Expected result:
            - The student view is set up for the render with the student.
        """
        self.xblock.is_static = False
        self.xblock.anonymous_user_id.return_value = self.anonymous_user_id
        self.xblock.is_student.return_value = True
        self.xblock.user_is_staff.return_value = False
        self.xblock.get_current_mind_map.return_value = None
        self.xblock.get_current_user.return_value = self.student
        expected_context = {
            "in_student_view": True,
            "is_static": False,
            "error_message": None,
        }
        expected_js_context = {
            "mind_map": None,
            "author": self.student.full_name,
            "editable": True,
        }

        self.xblock.student_view()

        self.xblock.render_template.assert_called_once_with(
            "static/html/mindmap.html", expected_context
        )
        initialize_js_mock.assert_called_once_with(
            'MindMapXBlock', json_args=expected_js_context
        )

    @patch("mindmap.mindmap.Fragment.initialize_js")
    def test_student_view_from_studio_is_static(self, initialize_js_mock: Mock):
        """
        Check student view is rendered correctly in studio when the mind map is static.

        Expected result:
            - The student view is set up for the render with the student.
        """
        self.xblock.is_static = True
        self.xblock.anonymous_user_id.return_value = self.anonymous_user_id
        self.xblock.user_is_staff.return_value = False
        self.xblock.is_student.return_value = False
        self.xblock.get_current_user.return_value = self.student
        self.xblock.get_current_mind_map.return_value = None
        expect_context = {
            "in_student_view": False,
            "is_static": True,
            "error_message": None,
        }
        expect_js_context = {
            "author": self.student.full_name,
            "mind_map": None,
            "editable": True,
        }

        self.xblock.student_view()

        self.xblock.render_template.assert_called_once_with(
            "static/html/mindmap.html", expect_context
        )
        initialize_js_mock.assert_called_once_with(
            "MindMapXBlock", json_args=expect_js_context
        )

    @patch("mindmap.mindmap.Fragment.initialize_js")
    def test_student_view_from_studio_is_not_static(self, initialize_js_mock: Mock):
        """
        Check student view is rendered correctly in
        studio when the mind map is not static.

        Expected result:
            - In studio a message is rendered instead of the mind map.
        """
        self.xblock.is_static = False
        self.xblock.anonymous_user_id.return_value = self.anonymous_user_id
        self.xblock.user_is_staff.return_value = False
        self.xblock.is_student.return_value = False
        self.xblock.get_current_user.return_value = self.student
        expect_context = {
            "in_student_view": False,
            "is_static": False,
            "error_message": None,
        }
        expect_js_context = {"author": self.student.full_name}

        self.xblock.student_view()

        self.xblock.get_current_mind_map.assert_not_called()
        self.xblock.render_template.assert_called_once_with(
            "static/html/mindmap.html", expect_context
        )
        initialize_js_mock.assert_called_once_with(
            "MindMapXBlock", json_args=expect_js_context
        )

    def test_studio_view(self):
        """
        Check studio view is rendered correctly.

        Expected result:
            - The studio view is set up for the render.
        """
        self.xblock.fields = {"display_name": "Test Mind Map", "is_static": True}
        expected_context = {
            "display_name": self.xblock.display_name,
            "is_static": self.xblock.is_static,
            "is_static_field": self.xblock.fields["is_static"],
        }

        self.xblock.studio_view()

        self.xblock.render_template.assert_called_once_with(
            "static/html/mindmap_edit.html", expected_context
        )


class TestMindMapUtilities(TestCase):
    """
    Test suite for the MindMapXBlock utilities methods.
    """

    def setUp(self) -> None:
        """
        Set up the test suite.
        """
        self.xblock = MindMapXBlock(
            runtime=Mock(), field_data=Mock(), scope_ids=Mock()
        )

    @override_settings(
        AWS_ACCESS_KEY_ID=None,
        AWS_SECRET_ACCESS_KEY=None,
        AWS_BUCKET_NAME=None,
    )
    def test_mindmap_service_not_configured(self):
        """
        When the Mind Map service is not configured, an exception is raised.

        Expected result:
            - An exception is raised.
        """
        with self.assertRaises(MisconfiguredMindMapService):
            self.xblock.connect_to_s3()

    @patch("mindmap.mindmap.boto3.client")
    def test_connect_to_s3(self, s3_client_mock):
        """
        Check connecting to S3.

        Expected result:
            - A connection is made to S3.
        """
        s3_client, bucket_name = self.xblock.connect_to_s3()
        expected_result = (
            s3_client_mock.return_value, "test-file-upload-storage-bucket-name"
        )

        self.assertEqual(expected_result, (s3_client, bucket_name))

    @patch("mindmap.mindmap.boto3.client")
    def test_get_current_mind_map_file_not_found(self, s3_client_mock: Mock):
        """
        Check getting the current mind map when the file is not found.

        Expected result:
            - None is returned.
        """
        suffix = 'test-anonymous-user-id'
        s3_client_mock.return_value.get_object.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchKey'}}, 'HeadObject'
        )

        result = self.xblock.get_current_mind_map(suffix)

        self.assertIsNone(result)

    @patch("mindmap.mindmap.boto3.client")
    def test_get_current_mind_map_file_found(self, s3_client_mock: Mock):
        """
        Check getting the current mind map when the file is found.

        Expected result:
            - The mind map is returned.
        """
        mind_map = {"data": [{ "id": "root", "isroot": True, "topic": "Root" }]}
        s3_client_mock.return_value.get_object.return_value = {
            "Body": Mock(read=Mock(return_value=json.dumps(mind_map).encode("utf-8")))
        }
        suffix = 'test-anonymous-user-id'

        result = self.xblock.get_current_mind_map(suffix)

        self.assertEqual(result, mind_map)
