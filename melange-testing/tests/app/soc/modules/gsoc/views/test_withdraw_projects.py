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

"""Tests for withdraw projects view.
"""


import httplib
import urllib

from django.utils import simplejson

from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import GSoCDjangoTestCase
from tests.timeline_utils import GSoCTimelineHelper


class WithdrawProjectsTest(GSoCDjangoTestCase):
  """Test withdraw projects page
  """

  def setUp(self):
    self.init()

  def assertWithdrawProjects(self, response):
    """Asserts that all templates from the withdraw projects page were used
    and all contexts were passed
    """
    self.assertTrue('base_layout' in response.context)
    self.assertTrue('cbox' in response.context)
    if response.context['cbox']:
      self.assertGSoCColorboxTemplatesUsed(response)
      self.assertEqual(response.context['base_layout'],
        'v2/modules/gsoc/base_colorbox.html')
    else:
      self.assertGSoCTemplatesUsed(response)
      self.assertEqual(response.context['base_layout'],
        'v2/modules/gsoc/base.html')

    self.assertTemplateUsed(response,
        'v2/modules/gsoc/withdraw_projects/base.html')
    self.assertTemplateUsed(response,
        'v2/modules/gsoc/withdraw_projects/_project_list.html')

  def testWithdrawProjects(self):
    self.data.createHost()
    self.timeline.studentsAnnounced()

    url = '/gsoc/withdraw_projects/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertWithdrawProjects(response)

    # list response without any projects
    response = self.getListResponse(url, 0)
    self.assertIsJsonResponse(response)
    data = response.context['data']['']
    self.assertEqual(0, len(data))

    # list response with projects
    mentor_profile_helper = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor_profile_helper.createOtherUser('mentor@example.com')
    mentor = mentor_profile_helper.createMentor(self.org)
    self.data.createStudentWithProposal(self.org, mentor)
    self.data.createStudentWithProject(self.org, mentor)

    response = self.getListResponse(url, 0)
    self.assertIsJsonResponse(response)
    data = response.context['data']['']
    self.assertEqual(1, len(data))
