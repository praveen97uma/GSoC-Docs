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

"""Tests for slots view.
"""


from django.utils import simplejson

from tests.test_utils import GSoCDjangoTestCase

from soc.modules.gsoc.models.organization import GSoCOrganization


class SlotsTest(GSoCDjangoTestCase):
  """Tests slots page.
  """

  def setUp(self):
    self.init()

  def assertProjectTemplatesUsed(self, response):
    """Asserts that all the templates from the dashboard were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/admin/list.html')
    self.assertTemplateUsed(response,
        'v2/modules/gsoc/admin/_accepted_orgs_list.html')

  def testAllocateSlots(self):
    self.data.createHost()
    url = '/gsoc/admin/slots/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertProjectTemplatesUsed(response)

    data = self.getListData(url, 0)
    self.assertEqual(1, len(data))

    org_data = {
        "slots": "20",
        "note":"Great org",
    }
    org_name = self.org.key().name()

    data = simplejson.dumps({org_name: org_data})

    postdata = {
        'data': data,
        'button_id': 'save',
        'idx': 0,
    }
    response = self.post(url, postdata)
    self.assertResponseOK(response)

    org = GSoCOrganization.all().get()

    org_data["slots"] = 20

    self.assertPropertiesEqual(org_data, org)
