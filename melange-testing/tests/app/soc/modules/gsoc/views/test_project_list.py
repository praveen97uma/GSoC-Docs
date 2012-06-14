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


from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import GSoCDjangoTestCase

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class ProjectListTest(GSoCDjangoTestCase):
  """Tests project list page.
  """

  def setUp(self):
    self.init()

  def assertProjectTemplatesUsed(self, response):
    """Asserts that all the templates from the dashboard were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/projects_list/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/projects_list/_project_list.html')

  def testListProjects(self):
    self.timeline.studentsAnnounced()
    url = '/gsoc/projects/list/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertProjectTemplatesUsed(response)

    response = self.getListResponse(url, 0)
    self.assertIsJsonResponse(response)
    data = response.context['data']['']
    self.assertEqual(0, len(data))

    self.mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    self.mentor.createMentor(self.org)
    self.data.createStudentWithProject(self.org, self.mentor.profile)
    response = self.getListResponse(url, 0)
    self.assertIsJsonResponse(response)
    data = response.context['data']['']
    self.assertEqual(1, len(data))
