#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for dashboard view.
"""


from django.utils import simplejson as json

from tests.profile_utils import GSoCProfileHelper
from tests.survey_utils import SurveyHelper
from tests.test_utils import GSoCDjangoTestCase


class DashboardTest(GSoCDjangoTestCase):
  """Tests dashboard page.
  """

  def setUp(self):
    self.init()

  def assertDashboardTemplatesUsed(self, response):
    """Asserts that all the templates from the dashboard were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/dashboard/base.html')

  def assertDashboardComponentTemplatesUsed(self, response):
    """Asserts that all the templates to render a component were used.
    """
    self.assertDashboardTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/dashboard/list_component.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/dashboard/component.html')
    self.assertTemplateUsed(response, 'v2/soc/list/lists.html')
    self.assertTemplateUsed(response, 'v2/soc/list/list.html')

  def testDasbhoardNoRole(self):
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardTemplatesUsed(response)

  def testDashboardAsLoneUser(self):
    self.data.createProfile()
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardTemplatesUsed(response)

  def testDashboardAsStudent(self):
    self.data.createStudent()
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardComponentTemplatesUsed(response)
    response = self.getListResponse(url, 1)
    self.assertIsJsonResponse(response)

  def testDashboardAsStudentWithProposal(self):
    mentor = GSoCProfileHelper(
        self.gsoc, self.dev_test).createOtherUser(
        'mentor@example.com').createMentor(self.org)
    self.data.createStudentWithProject(self.org, mentor)
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardComponentTemplatesUsed(response)
    response = self.getListResponse(url, 1)
    self.assertIsJsonResponse(response)

  def testDashboardAsStudentWithProject(self):
    mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor.createOtherUser('mentor@example.com').createMentor(self.org)
    self.data.createStudentWithProject(self.org, mentor.profile)
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardComponentTemplatesUsed(response)
    response = self.getListResponse(url, 2)
    self.assertIsJsonResponse(response)

  def testDashboardAsStudentWithEval(self):
    mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor.createOtherUser('mentor@example.com').createMentor(self.org)
    self.data.createStudentWithProject(self.org, mentor.profile)
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardComponentTemplatesUsed(response)
    response = self.getListResponse(url, 3)
    self.assertResponseForbidden(response)

    response = self.get(url)
    self.assertDashboardComponentTemplatesUsed(response)
    self.evaluation = SurveyHelper(self.gsoc, self.dev_test)
    self.evaluation.createStudentEvaluation(override={'link_id': 'midterm'})
    response = self.getListResponse(url, 3)
    self.assertIsJsonResponse(response)
    data = json.loads(response.content)
    self.assertEqual(len(data['data']['']), 1)

    self.evaluation.createStudentEvaluation(override={'link_id': 'final'})
    response = self.getListResponse(url, 3)
    self.assertIsJsonResponse(response)
    data = json.loads(response.content)
    self.assertEqual(len(data['data']['']), 2)

  def testDashboardAsHost(self):
    self.data.createHost()
    mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor.createOtherUser('mentor@example.com').createMentor(self.org)
    student = GSoCProfileHelper(self.gsoc, self.dev_test)
    student.createOtherUser('student@example.com')
    student.createStudentWithProject(self.org, mentor.profile)

    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardTemplatesUsed(response)

  def testDashboardAsOrgAdmin(self):
    self.data.createOrgAdmin(self.org)
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardComponentTemplatesUsed(response)
    response = self.getListResponse(url, 5)
    self.assertIsJsonResponse(response)

  def testDashboardAsMentor(self):
    self.data.createMentor(self.org)
    self.timeline.studentsAnnounced()
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardComponentTemplatesUsed(response)
    response = self.getListResponse(url, 4)
    self.assertIsJsonResponse(response)

  def testDashboardAsMentorWithProject(self):
    self.timeline.studentsAnnounced()
    student = GSoCProfileHelper(self.gsoc, self.dev_test)
    student.createOtherUser('student@example.com').createStudent()
    self.data.createMentorWithProject(self.org, student.profile)
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardComponentTemplatesUsed(response)
    response = self.getListResponse(url, 4)
    self.assertIsJsonResponse(response)

  def testDashboardRequest(self):
    self.data.createHost()
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.getListResponse(url, 7)
    self.assertIsJsonResponse(response)
    response = self.getListResponse(url, 8)
    self.assertIsJsonResponse(response)
