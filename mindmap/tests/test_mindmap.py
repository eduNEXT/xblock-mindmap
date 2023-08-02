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
        self.xblock = MindMapXBlock(runtime=Mock(), field_data=Mock(), scope_ids=Mock())
        self.student = Mock()
        self.anonymous_user_id = "test-anonymous-user-id"
        self.xblock.get_current_user = Mock()
        self.xblock.get_current_mind_map = Mock()
        self.xblock.anonymous_user_id = Mock()
        self.xblock.render_template = Mock(return_value="Test render")
        self.xblock.resource_string = Mock()
        self.xblock.display_name = "Test MindMap"

    @patch("mindmap.mindmap.Fragment.initialize_js")
    def test_student_view_with_mind_map(self, initialize_js_mock):
        """
        Check student view is rendered correctly.

        Expected result:
            - The student view is set up for the render with the student.
        """
        mind_map = {"data": "content"}
        self.xblock.get_current_user.return_value = self.student
        self.xblock.get_current_mind_map.return_value = mind_map
        self.xblock.anonymous_user_id.return_value = self.anonymous_user_id
        expected_js_context = {"mind_map": mind_map, "author": self.student.full_name}

        self.xblock.student_view()

        initialize_js_mock.assert_called_once_with(
            'MindMapXBlock', json_args=expected_js_context
        )

    @patch("mindmap.mindmap.Fragment.initialize_js")
    def test_student_view_empty_mind_map(self, initialize_js_mock):
        """
        Check student view is rendered correctly.

        Expected result:
            - The student view is set up for the render with the student.
        """
        self.xblock.get_current_mind_map.return_value = None
        self.xblock.get_current_user.return_value = self.student
        self.xblock.anonymous_user_id.return_value = self.anonymous_user_id
        expected_js_context = {"mind_map": None, "author": self.student.full_name}

        self.xblock.student_view()

        initialize_js_mock.assert_called_once_with(
            'MindMapXBlock', json_args=expected_js_context
        )

    def test_studio_view(self):
        """
        Check studio view is rendered correctly.

        Expected result:
            - The studio view is set up for the render.
        """
        self.xblock.fields = {"display_name": "Test Mind Map"}
        expected_context = {"display_name": self.xblock.display_name}

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
        self.xblock = MindMapXBlock(runtime=Mock(), field_data=Mock(), scope_ids=Mock())

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
    def test_file_exists_in_s3_existing_file(self, s3_client_mock: Mock):
        """
        Check if the file exists in S3 when it does.

        Expected result:
            - True is returned.
        """
        s3_client_mock.head_object.return_value = {}
        anonymous_user_id = 'test-anonymous-user-id'

        result = self.xblock.file_exists_in_s3(anonymous_user_id)

        self.assertTrue(result, "The file should exist in S3")

    @patch("mindmap.mindmap.boto3.client")
    def test_file_does_not_exist(self, s3_client_mock: Mock):
        """
        Check if the file exists in S3 when it doesn't.

        Expected result:
            - False is returned.
        """
        s3_client_mock.head_object.side_effect = ClientError(
            {'Error': {'Code': '404'}}, 'HeadObject'
        )
        self.xblock.connect_to_s3 = Mock(
            return_value=(s3_client_mock, 'test-file-upload-storage-bucket-name')
        )
        anonymous_user_id = 'test-anonymous-user-id'

        result = self.xblock.file_exists_in_s3(anonymous_user_id)

        self.assertFalse(result, "The file should not exist in S3")

    def test_get_current_mind_map_file_not_found(self):
        """
        Check getting the current mind map when the file is not found.

        Expected result:
            - None is returned.
        """
        self.xblock.file_exists_in_s3 = Mock(return_value=False)
        anonymous_user_id = 'test-anonymous-user-id'

        result = self.xblock.get_current_mind_map(anonymous_user_id)

        self.assertIsNone(result)

    @patch("mindmap.mindmap.boto3.client")
    def test_get_current_mind_map_file_found(self, s3_client_mock: Mock):
        """
        Check getting the current mind map when the file is found.

        Expected result:
            - The mind map is returned.
        """
        mind_map = {"data": [{ "id": "root", "isroot": True, "topic": "Root" }]}
        s3_client_mock.get_object.return_value = {
            "Body": Mock(read=Mock(
                return_value=json.dumps(mind_map).encode("utf-8"))
            )
        }
        self.xblock.connect_to_s3 = Mock(
            return_value=(s3_client_mock, 'test-file-upload-storage-bucket-name')
        )
        self.xblock.file_exists_in_s3 = Mock(return_value=True)
        anonymous_user_id = 'test-anonymous-user-id'

        result = self.xblock.get_current_mind_map(anonymous_user_id)

        self.assertEqual(result, mind_map)
