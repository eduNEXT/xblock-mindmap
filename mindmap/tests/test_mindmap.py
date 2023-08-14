"""
Tests for the LimeSurveyXBlock definition class.
"""
from unittest import TestCase
from unittest.mock import Mock, patch

from mindmap.mindmap import MindMapXBlock


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
        self.xblock.is_student = Mock()
        self.xblock.is_course_staff = Mock()
        self.xblock.get_current_user = Mock()
        self.xblock.get_current_mind_map = Mock()
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
        block_id = self.xblock.scope_ids.usage_id.block_id
        editable = True
        self.xblock.is_static = False
        self.xblock.is_student.return_value = True
        self.xblock.get_current_user.return_value = self.student
        self.xblock.get_current_mind_map.return_value = mind_map
        expected_context = {
            "display_name": self.xblock.display_name,
            "in_student_view": True,
            "editable": editable,
            "xblock_id": block_id,
            "is_static": self.xblock.is_static,
            "is_static_field": self.xblock.fields["is_static"],
        }
        expected_js_context = {
            "author": self.student.full_name,
            "mind_map": mind_map,
            "editable": editable,
            "xblock_id": block_id,
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
        editable = True
        block_id = self.xblock.scope_ids.usage_id.block_id
        self.xblock.is_static = False
        self.xblock.is_student.return_value = True
        self.xblock.get_current_mind_map.return_value = None
        self.xblock.get_current_user.return_value = self.student
        expected_context = {
            "display_name": self.xblock.display_name,
            "in_student_view": True,
            "editable": editable,
            "xblock_id": block_id,
            "is_static": self.xblock.is_static,
            "is_static_field": self.xblock.fields["is_static"],
        }
        expected_js_context = {
            "author": self.student.full_name,
            "mind_map": None,
            "editable": editable,
            "xblock_id": block_id,
        }

        self.xblock.student_view()

        self.xblock.render_template.assert_called_once_with(
            "static/html/mindmap.html", expected_context,
        )
        initialize_js_mock.assert_called_once_with(
            'MindMapXBlock', json_args=expected_js_context
        )

    def test_studio_view(self):
        """
        Check studio view is rendered correctly.

        Expected result:
            - The studio view is set up for the render.
        """
        self.xblock.is_student.return_value = False
        self.xblock.is_course_staff.return_value = False
        self.xblock.fields = {"display_name": "Test Mind Map", "is_static": True}
        expected_context = {
            "display_name": self.xblock.display_name,
            "in_student_view": False,
            "editable": True,
            "xblock_id": self.xblock.scope_ids.usage_id.block_id,
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

    def test_get_current_mind_map_file_does_not_exist(self):
        """
        Check getting the current mind map when the file does not exist.

        Expected result:
            - None is returned.
        """
        self.xblock.mindmap_student_body = {}
        self.xblock.is_static = False
        self.xblock.mindmap_body = {
            "data": [{ "id": "root", "isroot": True, "topic": "Root" }]
        }

        result = self.xblock.get_current_mind_map()

        self.assertEqual(result, self.xblock.mindmap_body)

    def test_get_current_mind_map_file_found(self):
        """
        Check getting the current mind map when the file found.

        Expected result:
            - None is returned.
        """
        self.xblock.mindmap_student_body = {
            "data": [{ "id": "root", "isroot": True, "topic": "Root" }]
        }
        self.xblock.is_static = False

        result = self.xblock.get_current_mind_map()

        self.assertEqual(result, self.xblock.mindmap_student_body)
