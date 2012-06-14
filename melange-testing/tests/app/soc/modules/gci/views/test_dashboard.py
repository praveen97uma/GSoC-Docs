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


"""Tests the view for GCI Dashboard.
"""


from django.utils import simplejson as json

from tests.test_utils import GCIDjangoTestCase


class DashboardTest(GCIDjangoTestCase):
  """Tests the GCI Dashboard components.
  """

  def setUp(self):
    self.init()
    self.url = '/gci/dashboard/' + self.gci.key().name()

  def assertDashboardTemplatesUsed(self, response):
    """Asserts that all the templates from the dashboard were used.
    """
    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/dashboard/base.html')

  def assertDashboardComponentTemplatesUsed(self, response):
    """Asserts that all the templates to render a component were used.
    """
    self.assertDashboardTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/dashboard/list_component.html')
    self.assertTemplateUsed(response, 'v2/modules/gci/dashboard/component.html')
    self.assertTemplateUsed(response, 'v2/soc/list/lists.html')
    self.assertTemplateUsed(response, 'v2/soc/list/list.html')

  def testDashboardAsHost(self):
    self.data.createHost()
    url = '/gci/dashboard/' + self.gci.key().name()
    response = self.get(url)
    self.assertResponseOK(response)
    self.assertDashboardComponentTemplatesUsed(response)

  def testDashboardAsMentorWithTask(self):
    self.data.createMentorWithTask('Open', self.org)
    url = '/gci/dashboard/' + self.gci.key().name()
    response = self.get(url)
    self.assertDashboardComponentTemplatesUsed(response)
    response = self.getListResponse(url, 1)
    self.assertIsJsonResponse(response)
    data = json.loads(response.content)
    self.assertEqual(1, len(data['data']['']))
