from django.test import TestCase
from minos import models
from minos.views import question_views


class QuestionTestCase(TestCase):
    def setUp(self):
        self.json_response = {
            'running_time': '.04\n',
            'errors': '',
            'output': 'Hello, Test'
        }

    def test_extract_compilebox_results_passing(self):
        test_case = models.TestCase(standard_out='Hello, Test', error_viewable=True)
        passed_str, message = question_views.extract_compilebox_results(self.json_response, test_case, '', 0)

        self.assertEquals(passed_str, 'true')
        self.assertEquals(message, 'Test Case 1 Passed.')

    def test_extract_compilebox_results_failing_not_viewable(self):
        test_case = models.TestCase(standard_out='bad output', error_viewable=False)

        passed_str, message = question_views.extract_compilebox_results(self.json_response, test_case, '', 0)

        self.assertEquals(passed_str, 'false')
        self.assertEquals(message, 'Test Case 1 Failed.')

    def test_extract_compilebox_results_failing_viewable(self):
        test_case = models.TestCase(standard_out='Real Output', error_viewable=True)

        passed_str, message = question_views.extract_compilebox_results(self.json_response, test_case, '', 0)

        self.assertEquals(passed_str, 'false')
        self.assertEquals(message, 'Test Case 1 Failed.\\n\\n'
                                   'Expected Output:\\nReal Output\\n\\n'
                                   'Actual Output:\\nHello, Test')
