"""
Tests for the LimeSurveyXBlock definition class.
"""
import json
from unittest import TestCase
from unittest.mock import Mock, patch

from django.core.files.storage import default_storage
from django.test.utils import override_settings

from mindmap.mindmap import MindMapXBlock
from mindmap.utils import get_mindmap_storage


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
    def test_student_view_with_mind_map(self, initialize_js_mock: Mock):
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
            "static/html/mindmap.html", expected_context,
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
            "static/html/mindmap.html", expected_context,
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
        expected_context = {
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
            "static/html/mindmap.html", expected_context,
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
        expected_context = {
            "in_student_view": False,
            "is_static": False,
            "error_message": None,
        }
        expect_js_context = {"author": self.student.full_name}

        self.xblock.student_view()

        self.xblock.get_current_mind_map.assert_not_called()
        self.xblock.render_template.assert_called_once_with(
            "static/html/mindmap.html", expected_context,
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
            "static/html/mindmap_edit.html", expected_context,
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

    @patch("mindmap.mindmap.get_mindmap_storage")
    def test_get_current_mind_map_file_not_found(self, mindmap_storage_mock: Mock):
        """
        Check getting the current mind map when the file is not found.

        Expected result:
            - None is returned.
        """
        path_prefix = 'test-anonymous-user-id'
        mindmap_storage_mock.return_value.open.side_effect = IOError

        result = self.xblock.get_current_mind_map(path_prefix)

        self.assertIsNone(result)

    @patch("mindmap.mindmap.get_mindmap_storage")
    def test_get_current_mind_map_file_found(self, mindmap_storage_mock: Mock):
        """
        Check getting the current mind map when the file is not found.

        Expected result:
            - None is returned.
        """
        mind_map = {"data": [{ "id": "root", "isroot": True, "topic": "Root" }]}
        path_prefix = 'test-anonymous-user-id'
        mindmap_storage_mock.return_value.open.return_value = Mock(
            read=Mock(return_value=json.dumps(mind_map).encode("utf-8"))
        )

        result = self.xblock.get_current_mind_map(path_prefix)

        self.assertEqual(result, mind_map)


class TestUtils(TestCase):
    """
    Test suite for utils of the MindMapXBlock.
    """

    def setUp(self):
        self.storage_mock = Mock()
        self.storage_class_mock = Mock(return_value=self.storage_mock)

    @override_settings(MINDMAP_BLOCK_STORAGE=None)
    def test_get_mindmap_storage_default(self):
        result = get_mindmap_storage()
        self.assertEqual(result, default_storage)

    @patch("mindmap.utils.get_storage_class", autospec=True)
    def test_get_mindmap_storage_custom(self, mock_get_storage_class):
        mock_get_storage_class.return_value = self.storage_class_mock

        result = get_mindmap_storage()

        self.assertEqual(result, self.storage_mock)
        self.storage_class_mock.assert_called_once_with(bucket_name="test-bucket-name")
