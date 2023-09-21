from mindmap.mindmap import SubmissionStatus


def update_student_submission_status(*args, **kwargs):
    """Update the submission status for a student after resetting their score."""
    from submissions.api import get_submissions  # pylint: disable=import-outside-toplevel
    from submissions.api import create_submission

    student_item_dict = {
        "student_id": kwargs.get("anonymous_user_id"),
        "item_id": kwargs.get("item_id"),
        "item_type": "mindmap",
        "course_id": kwargs.get("course_id"),
    }
    submissions = get_submissions(student_item_dict)
    if not submissions:
        return

    student_submission = submissions[0]
    new_answer = student_submission.get("answer")
    new_answer["submission_status"] = SubmissionStatus.NOT_ATTEMPTED.value

    create_submission(student_item_dict, new_answer)
