from typing import List
from .api_models import PreviousSubmission

class InMemorySubmissionStore:
    def __init__(self):
        self.submissions = []

    def add_submission(self, submission: PreviousSubmission):
        self.submissions.append(submission)

    def get_recent_submissions(self, count) -> List[PreviousSubmission]:
        return self.submissions[-count:]