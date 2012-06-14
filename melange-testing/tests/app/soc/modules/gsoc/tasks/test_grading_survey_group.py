#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test for the GradingSurveyGroup.
"""


import httplib
import urllib

from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import GSoCDjangoTestCase
from tests.test_utils import MailTestCase
from tests.test_utils import TaskQueueTestCase

from soc.modules.gsoc.models.grading_project_survey import GradingProjectSurvey
from soc.modules.gsoc.models.grading_project_survey_record import \
    GSoCGradingProjectSurveyRecord
from soc.modules.gsoc.models.grading_record import GSoCGradingRecord
from soc.modules.gsoc.models.grading_survey_group import GSoCGradingSurveyGroup
from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.models.project_survey import ProjectSurvey
from soc.modules.gsoc.models.project_survey_record import GSoCProjectSurveyRecord


class GradingSurveyGroupTest(MailTestCase, GSoCDjangoTestCase, TaskQueueTestCase):
  """Tests for accept_proposals task.
  """

  UPDATE_RECORDS_URL = '/tasks/gsoc/grading_record/update_records'
  UPDATE_PROJECTS_URL = '/tasks/gsoc/grading_record/update_projects'
  SEND_URL = '/tasks/gsoc/grading_record/mail_result'

  def setUp(self):
    super(GradingSurveyGroupTest, self).setUp()
    self.init()
    self.createMentor()
    self.createStudent()
    self.createSurveys()

  def createMentor(self):
    """Creates a new mentor.
    """
    profile_helper = GSoCProfileHelper(self.gsoc, self.dev_test)
    profile_helper.createOtherUser('mentor@example.com')
    self.mentor = profile_helper.createMentor(self.org)

  def createStudent(self):
    """Creates a Student with a project.
    """
    profile_helper = GSoCProfileHelper(self.gsoc, self.dev_test)
    profile_helper.createOtherUser('student@example.com')
    self.student = profile_helper.createStudentWithProject(self.org,
                                                           self.mentor)
    self.project = GSoCProject.all().ancestor(self.student).get()

  def createSurveys(self):
    """Creates the surveys and records required for the tests.
    """
    survey_values = {
        'author': self.founder,
        'title': 'Title',
        'modified_by': self.founder,
        'link_id': 'link_id',
        'scope': self.gsoc,
        'scope_path': self.gsoc.key().id_or_name()}

    self.project_survey = ProjectSurvey(key_name='key_name',
                                        **survey_values)
    self.project_survey.put()

    self.grading_survey = GradingProjectSurvey(key_name='key_name',
                                               **survey_values)
    self.grading_survey.put()

    record_values = {
        'user': self.student.user,
        'org': self.org,
        'project': self.project,
        'survey': self.project_survey}
    self.project_survey_record = GSoCProjectSurveyRecord(**record_values)
    self.project_survey_record.put()

    self.grading_survey = GradingProjectSurvey(**survey_values)
    self.grading_survey.put()

    record_values = {
        'user': self.student.user,
        'org': self.org,
        'project': self.project,
        'survey': self.grading_survey,
        'grade': True}
    self.grading_survey_record = GSoCGradingProjectSurveyRecord(
        **record_values)
    self.grading_survey_record.put()

    group_values = {
        'name': 'Survey Group Name',
        'grading_survey': self.grading_survey,
        'student_survey': self.project_survey,
        'program': self.gsoc}
    self.survey_group = GSoCGradingSurveyGroup(**group_values)
    self.survey_group.put()

    record_values = {
        'grading_survey_group': self.survey_group,
        'mentor_record': self.grading_survey_record,
        'student_record': self.project_survey_record,
        'grade_decision': 'pass'}
    self.grading_record = GSoCGradingRecord(parent=self.project,
                                            **record_values)
    self.grading_record.put()

  def testCreateGradingRecord(self):
    """Test creating a GradingRecord.
    """
    self.grading_record.delete()

    post_data = {
        'group_key': self.survey_group.key().id_or_name()
        }

    response = self.post(self.UPDATE_RECORDS_URL, post_data)

    self.assertEqual(response.status_code, httplib.OK)
    self.assertTasksInQueue(n=1, url=self.UPDATE_RECORDS_URL)

    record = GSoCGradingRecord.all().get()
    self.assertFalse(record is None)
    self.assertEqual(record.grade_decision, 'pass')

  def testUpdateGradingRecord(self):
    """Test updating a GradingRecord.
    """
    self.grading_record.grade_decision = 'undecided'
    self.grading_record.put()

    post_data = {
        'group_key': self.survey_group.key().id_or_name()
        }

    response = self.post(self.UPDATE_RECORDS_URL, post_data)

    self.assertEqual(response.status_code, httplib.OK)
    self.assertTasksInQueue(n=1, url=self.UPDATE_RECORDS_URL)

    record = GSoCGradingRecord.all().get()
    self.assertFalse(record is None)
    self.assertEqual(record.grade_decision, 'pass')

  def testUpdateProject(self):
    """Test updating a Project with a GradingRecord's result.
    """
    post_data = {
        'group_key': self.survey_group.key().id_or_name(),
        }

    response = self.post(self.UPDATE_PROJECTS_URL, post_data)

    self.assertEqual(response.status_code, httplib.OK)
    self.assertTasksInQueue(n=1, url=self.UPDATE_PROJECTS_URL)

    project = GSoCProject.all().get()
    self.assertFalse(project is None)
    self.assertEqual(project.passed_evaluations, [self.grading_record.key()])
    self.assertEqual(1, project.parent().student_info.passed_evaluations)

  def testUpdateProjectWithSendMail(self):
    """Test updating a Project with a GradingRecord's result and sending mail.
    """
    post_data = {
        'group_key': self.survey_group.key().id_or_name(),
        'send_mail': True,
        }

    response = self.post(self.UPDATE_PROJECTS_URL, post_data)

    self.assertEqual(response.status_code, httplib.OK)
    self.assertTasksInQueue(n=1, url=self.UPDATE_PROJECTS_URL)
    self.assertTasksInQueue(n=1, url=self.SEND_URL)

    project = GSoCProject.all().get()
    self.assertFalse(project is None)
    self.assertEqual(project.passed_evaluations, [self.grading_record.key()])
    self.assertEqual(1, project.parent().student_info.passed_evaluations)

  def testSendMail(self):
    """Test sending mail about a GradingRecord's result.
    """
    post_data = {
        'record_key': str(self.grading_record.key())
        }

    response = self.post(self.SEND_URL, post_data)

    self.assertEqual(response.status_code, httplib.OK)
    # URL explicitly added since the email task is in there
    self.assertTasksInQueue(n=0, url=self.SEND_URL)
    self.assertEmailSent(to=self.student.email)
