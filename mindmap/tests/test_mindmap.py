"""
Tests for the LimeSurveyXBlock definition class.
"""
import datetime
import json
from http import HTTPStatus
from unittest import TestCase
from unittest.mock import Mock, patch

import ddt
from xblock.fields import DateTime

from mindmap.mindmap import MindMapXBlock


class MindMapXBlockTestMixin(TestCase):
    """
    Mixin for the MindMapXBlock test suite.
    """

    def setUp(self) -> None:
        """
        Set up the test suite.
        """
        self.xblock = MindMapXBlock(
            runtime=Mock(), field_data=Mock(), scope_ids=Mock(),
        )
        self.editable_mind_map = True
        self.mind_map = {"data": [{ "id": "root", "isroot": True, "topic": "Root" }]}
        self.student = Mock(student_id="test-student-id", full_name="Test Student")
        self.anonymous_user_id = "test-anonymous-user-id"
        self.xblock.get_current_mind_map = Mock()
        self.xblock.render_template = Mock(return_value="Test render")
        self.xblock.resource_string = Mock()
        self.xblock.submit_allowed = Mock(return_value=True)
        self.xblock.past_due = Mock(return_value=False)
        self.xblock.get_score = Mock(return_value=0)
        self.xblock.get_current_user = Mock(return_value=self.student)
        self.xblock.show_staff_grading_interface = Mock(return_value=False)
        self.xblock.display_name = "Test MindMap"
        self.xblock.points = 100
        self.xblock.weight = 1
        self.xblock.has_score = True
        self.xblock.submission_status = "Not attempted"
        self.xblock.course_id = "test-course-id"


class TestMindMapXBlock(MindMapXBlockTestMixin):
    """
    Test suite for the MindMapXBlock definition base views.
    """

    initialize_js_mock = patch("mindmap.mindmap.Fragment.initialize_js")

    @initialize_js_mock
    def test_student_view_with_mind_map(self, initialize_js_mock: Mock):
        """
        Check student view is rendered correctly with a mind map.

        Expected result:
            - The student view is set up for the render with the student.
        """
        self.xblock.is_static = False
        self.xblock.get_current_user.return_value.opt_attrs = {
            "edx-platform.user_role": "student",
        }
        self.xblock.get_current_user.return_value = self.student
        self.xblock.get_current_mind_map.return_value = self.mind_map
        expected_context = {
            "display_name": self.xblock.display_name,
            "in_student_view": True,
            "editable": self.editable_mind_map,
            "xblock_id": self.xblock.scope_ids.usage_id.block_id,
            "is_static": self.xblock.is_static,
            "is_static_field": self.xblock.fields["is_static"],
            "can_submit_assignment": True,
            "score": 0,
            "max_score": self.xblock.max_score(),
            "has_score": True,
            "has_score_field": self.xblock.fields["has_score"],
            "submission_status": self.xblock.submission_status,
        }
        expected_js_context = {
            "author": self.student.full_name,
            "mind_map": self.mind_map,
            "editable": self.editable_mind_map,
            "xblock_id": self.xblock.scope_ids.usage_id.block_id,
            "max_points": self.xblock.points,
        }

        self.xblock.student_view()

        self.xblock.render_template.assert_called_once_with(
            "public/html/mindmap.html", expected_context,
        )
        initialize_js_mock.assert_called_once_with(
            'MindMapXBlock', json_args=expected_js_context
        )

    @initialize_js_mock
    def test_student_view_empty_mind_map(self, initialize_js_mock: Mock):
        """
        Check student view is rendered correctly with an empty mind map (None)

        Expected result:
            - The student view is set up for the render with the student.
        """
        self.xblock.is_static = False
        self.xblock.get_current_user.return_value.opt_attrs = {
            "edx-platform.user_role": "student",
        }
        self.xblock.get_current_mind_map.return_value = None
        expected_context = {
            "display_name": self.xblock.display_name,
            "in_student_view": True,
            "editable": self.editable_mind_map,
            "xblock_id": self.xblock.scope_ids.usage_id.block_id,
            "is_static": self.xblock.is_static,
            "is_static_field": self.xblock.fields["is_static"],
            "can_submit_assignment": True,
            "score": 0,
            "max_score": self.xblock.max_score(),
            "has_score": True,
            "has_score_field": self.xblock.fields["has_score"],
            "submission_status": self.xblock.submission_status,
        }
        expected_js_context = {
            "author": self.student.full_name,
            "mind_map": None,
            "editable": self.editable_mind_map,
            "xblock_id": self.xblock.scope_ids.usage_id.block_id,
            "max_points": self.xblock.points,
        }

        self.xblock.student_view()

        self.xblock.render_template.assert_called_once_with(
            "public/html/mindmap.html", expected_context,
        )
        initialize_js_mock.assert_called_once_with(
            'MindMapXBlock', json_args=expected_js_context
        )

    def test_static_mind_map_in_student_view(self):
        """
        Check student view is rendered correctly with a static mind map.

        Expected result:
            - The student view is set up for the render with the student.
        """
        self.xblock.is_static = True
        self.xblock.get_current_user.return_value.opt_attrs = {
            "edx-platform.user_role": "student",
        }
        self.xblock.get_current_mind_map.return_value = self.mind_map
        self.xblock.is_static = True
        expected_context = {
            "display_name": self.xblock.display_name,
            "in_student_view": True,
            "editable": False,
            "xblock_id": self.xblock.scope_ids.usage_id.block_id,
            "is_static": self.xblock.is_static,
            "is_static_field": self.xblock.fields["is_static"],
            "can_submit_assignment": True,
            "score": 0,
            "max_score": self.xblock.max_score(),
            "has_score": True,
            "has_score_field": self.xblock.fields["has_score"],
            "submission_status": self.xblock.submission_status,
        }

        self.xblock.student_view()

        self.xblock.render_template.assert_called_once_with(
            "public/html/mindmap.html", expected_context,
        )

    def test_student_view_for_instructor(self):
        """
        Check student view is rendered correctly for an instructor.

        Expected result:
            - The student view is set up for the render with the instructor.
        """
        self.xblock.is_static = False
        self.xblock.get_current_user.return_value.opt_attrs = {
            "edx-platform.user_is_staff": True,
        }
        self.xblock.is_course_staff = True
        self.xblock.get_current_mind_map.return_value = self.mind_map
        self.xblock.show_staff_grading_interface.return_value = True
        expected_context = {
            "display_name": self.xblock.display_name,
            "in_student_view": True,
            "editable": self.editable_mind_map,
            "xblock_id": self.xblock.scope_ids.usage_id.block_id,
            "is_static": self.xblock.is_static,
            "is_static_field": self.xblock.fields["is_static"],
            "can_submit_assignment": True,
            "score": 0,
            "max_score": self.xblock.max_score(),
            "is_instructor": True,
            "has_score": True,
            "has_score_field": self.xblock.fields["has_score"],
            "submission_status": self.xblock.submission_status,
        }

        self.xblock.student_view()

        self.xblock.render_template.assert_called_once_with(
            "public/html/mindmap.html", expected_context,
        )

    def test_studio_view(self):
        """
        Check studio view is rendered correctly.

        Expected result:
            - The studio view is set up for the render.
        """
        self.xblock.get_current_user.return_value.opt_attrs = {}
        self.xblock.fields = {
            "display_name": "Test Mind Map",
            "is_static": True,
            "points": 100,
            "weight": 1,
            "has_score": True,
        }
        expected_context = {
            "display_name": self.xblock.display_name,
            "in_student_view": False,
            "editable": self.editable_mind_map,
            "xblock_id": self.xblock.scope_ids.usage_id.block_id,
            "is_static": self.xblock.is_static,
            "is_static_field": self.xblock.fields["is_static"],
            "can_submit_assignment": True,
            "score": 0,
            "points": 100,
            "points_field": self.xblock.fields["points"],
            "weight": 1,
            "weight_field": self.xblock.fields["weight"],
            "max_score": self.xblock.max_score(),
            "has_score": True,
            "has_score_field": self.xblock.fields["has_score"],
            "submission_status": self.xblock.submission_status,
        }

        self.xblock.studio_view()

        self.xblock.render_template.assert_called_once_with(
            "public/html/mindmap_edit.html", expected_context,
        )

    @initialize_js_mock
    def test_student_not_allowed_submission(self, initialize_js_mock: Mock):
        """
        Check student view when a student cannot submit since it is not allowed.

        Why:
            - The student should not be able to submit when the assignment is past due.
            - The student should not be able to submit when the assignment when they
            have already submitted.
            - The student should not be able to submit when the assignment have been
            graded.

        Expected result:
            - The student cannot submit using the student view.
        """
        block_id = self.xblock.scope_ids.usage_id.block_id
        self.xblock.is_static = False
        self.xblock.get_current_user.return_value.opt_attrs = {
            "edx-platform.user_role": "student",
        }
        self.xblock.get_current_mind_map.return_value = self.mind_map
        self.xblock.submit_allowed.return_value = False
        expected_context = {
            "display_name": self.xblock.display_name,
            "in_student_view": True,
            "editable": False,
            "xblock_id": block_id,
            "is_static": self.xblock.is_static,
            "is_static_field": self.xblock.fields["is_static"],
            "can_submit_assignment": False,
            "score": 0,
            "max_score": self.xblock.max_score(),
            "has_score": True,
            "has_score_field": self.xblock.fields["has_score"],
            "submission_status": self.xblock.submission_status,
        }
        expected_js_context = {
            "author": self.student.full_name,
            "mind_map": self.mind_map,
            "editable": False,
            "xblock_id": block_id,
            "max_points": self.xblock.points,
        }

        self.xblock.student_view()

        self.xblock.render_template.assert_called_once_with(
            "public/html/mindmap.html", expected_context,
        )
        initialize_js_mock.assert_called_once_with(
            'MindMapXBlock', json_args=expected_js_context
        )

@ddt.ddt
class TestMindMapXBlockHandlers(MindMapXBlockTestMixin):
    """
    Test suite for the MindMapXBlock JSON handlers.
    """

    def setUp(self) -> None:
        """
        Set up the test suite.
        """
        super().setUp()
        self.data = {
            "display_name": "Test Mind Map",
            "mind_map": self.mind_map,
            "is_static": True,
            "points": 100,
            "weight": 1,
        }
        self.request = Mock(
            body=json.dumps(self.data).encode("utf-8"),
            method="POST",
            status_code_success=HTTPStatus.OK,
        )
        self.student_id = "test-student-id"
        self.grade = 100
        self.submission_id = "test-submission-id"

    def test_studio_submit(self):
        """
        Check studio submit handler.

        Expected result:
            - The studio view is rendered with the appropriate values.
        """
        self.xblock.studio_submit(self.request)

        self.assertEqual(self.data["display_name"], self.xblock.display_name)
        self.assertEqual(self.data["mind_map"], self.xblock.mindmap_body)
        self.assertEqual(self.data["is_static"], self.xblock.is_static)
        self.assertEqual(self.data["points"], self.xblock.points)
        self.assertEqual(self.data["weight"], self.xblock.weight)

    @ddt.data(
        {"points": "/-100", "weight": 1},
        {"points": 100, "weight": ".-0.5"},
        {"points": "/100", "weight": "/0.5"},
    )
    def test_studio_submit_badly_formatted(self, bad_formatted_data: dict):
        """
        Check studio submit handler with badly formatted data.

        Expected result:
            - The studio view raises an error.
        """
        data = {
            "display_name": "Test Mind Map",
            "mindmap_body": self.mind_map,
            "is_static": True,
            "has_score": True,
        }
        data.update(bad_formatted_data)
        self.request.body = json.dumps(data).encode("utf-8")

        response = self.xblock.studio_submit(self.request)

        self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)

    def test_save_assignment(self):
        """
        Check save assignment JSON handler.

        Expected result:
            - The view returns 200 status code.
            - The mind map is saved.
        """
        response = self.xblock.save_assignment(self.request)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(self.data["mind_map"], self.xblock.mindmap_student_body)

    @patch("submissions.api.create_submission")
    def test_submit_assignment(self, create_submission_mock: Mock):
        """
        Check submit assignment handler.

        Expected result:
            - The student view is rendered with the appropriate values.
        """
        expected_student_item_dict = {
            "item_id": self.xblock.block_id,
            "item_type": "mindmap",
            "student_id": self.xblock.get_current_user().opt_attrs.get(),
            "course_id": self.xblock.block_course_id,
        }
        expected_answer = {
            "mindmap_student_body": json.dumps(self.data["mind_map"]),
        }

        response = self.xblock.submit_assignment(self.request)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        create_submission_mock.assert_called_once_with(
            expected_student_item_dict,
            expected_answer,
        )

    @patch("mindmap.mindmap.MindMapXBlock.get_student_module")
    @patch("submissions.api.set_score")
    def test_enter_grade(self, set_score_mock: Mock, get_student_module_mock: Mock):
        """
        Check enter grade handler.

        Expected result:
            - The student view is rendered with the appropriate values.
        """
        self.request.body = json.dumps(
            {
                "grade": self.grade,
                "submission_id": self.submission_id
            }
        ).encode("utf-8")
        self.xblock.get_current_user.return_value.opt_attrs = {
            "edx-platform.user_is_staff": True,
        }
        get_student_module_mock.return_value = Mock(state='{"test-state": "mindmap"}')

        response = self.xblock.enter_grade(self.request)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        set_score_mock.assert_called_once_with(
            self.submission_id,
            self.grade,
            self.xblock.max_score(),
        )

    @patch("mindmap.mindmap.MindMapXBlock.get_student_module")
    @patch("submissions.api.reset_score")
    def test_remove_grade(self, reset_score_mock: Mock, get_student_module_mock: Mock):
        """
        Check remove grade handler.

        Expected result:
            - The student view is rendered with the appropriate values.
        """
        self.request.body = json.dumps({"student_id": self.student_id}).encode("utf-8")
        self.xblock.get_current_user.return_value.opt_attrs = {
            "edx-platform.user_is_staff": True,
        }
        get_student_module_mock.return_value = Mock(state='{"test-state": "mindmap"}')

        response = self.xblock.remove_grade(self.request)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        reset_score_mock.assert_called_once_with(
            self.student_id,
            self.xblock.block_course_id,
            self.xblock.block_id,
        )

    @patch("mindmap.mindmap.MindMapXBlock.get_or_create_student_module")
    @patch("mindmap.mindmap.user_by_anonymous_id")
    @patch("submissions.models.StudentItem")
    def test_get_instructor_grading_data(
        self,
        student_item_mock: Mock,
        user_by_anonymous_id_mock: Mock,
        get_or_create_student_module_mock: Mock,
    ):
        """
        Check get instructor grading data handler.

        Expected result:
            - The student view is rendered with the appropriate values.
        """
        self.xblock.get_score.return_value = 50
        student_item_mock.objects.filter.return_value = [
            Mock(
                grade=self.xblock.score,
                student_id=self.student.student_id,
            ),
        ]
        current_datetime = datetime.datetime.now()
        module_id = 1
        self.xblock.get_submission = Mock(return_value={
            "uuid": "test-submission-id",
            "answer": {
                "mindmap_student_body": json.dumps(self.data["mind_map"]),
            },
            "created_at": current_datetime,
        })
        self.xblock.get_current_user.return_value.opt_attrs = {
            "edx-platform.user_is_staff": True,
        }
        user_by_anonymous_id_mock.return_value = Mock(username=self.student.student_id)
        self.xblock.submission_status = "Submitted"
        expected_result = {
            "assignments": [
                {
                    "module_id": module_id,
                    "student_id": self.student.student_id,
                    "submission_id": "test-submission-id",
                    "answer_body": {
                        "mindmap_student_body": json.dumps(self.data["mind_map"])
                    },
                    "username": self.student.student_id,
                    "timestamp": current_datetime.strftime(DateTime.DATETIME_FORMAT),
                    "score": 50,
                    "submission_status": self.xblock.submission_status,

                },
            ],
            "display_name": self.xblock.display_name,
            "max_score": self.xblock.max_score(),
        }
        get_or_create_student_module_mock.return_value = Mock(
            state='{"submission_status": "Submitted"}', id=module_id,
        )

        response = self.xblock.get_instructor_grading_data(self.request)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertDictEqual(expected_result, response.json)  # pylint: disable=no-member


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
