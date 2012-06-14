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


"""Tests the view for GCI accepted orgs.
"""


from soc.modules.gci.models.organization import GCIOrganization

from tests.test_utils import GCIDjangoTestCase


class AcceptedOrgsPageTest(GCIDjangoTestCase):
  """Tests the page to display accepted organization.
  """

  def setUp(self):
    self.init()
    self.url = '/gci/accepted_orgs/' + self.gci.key().name()

  def assertAcceptedOrgsPageTemplatesUsed(self, response):
    """Asserts that all the required templates to render the page were used.
    """
    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/accepted_orgs/base.html')
    self.assertTemplateUsed(
        response, 'v2/modules/gci/accepted_orgs/_project_list.html')
    self.assertTemplateUsed(response, 'v2/soc/list/lists.html')
    self.assertTemplateUsed(response, 'v2/soc/list/list.html')

  def testAcceptedOrgsAreDisplayedOnlyAfterTheyAreAnnounced(self):
    """Tests that the list of accepted organizations can be accessed only after
    the organizations have been announced.
    """
    self.timeline.orgSignup()
    response = self.get(self.url)
    self.assertResponseForbidden(response)

  def testAcceptedOrgsAreDisplayedAfterOrganizationsHaveBeenAnnounced(self):
    """Tests that the list of the organizations can not be accessed before
    organizations have been announced.
    """
    self.data.createUser()
    org_properties = {
        'scope': self.gci, 'status': 'active', 'founder': self.data.user,
        'home': None,
    }
    self.seed(GCIOrganization, org_properties)
    self.seed(GCIOrganization, org_properties)
    self.timeline.orgsAnnounced()

    response = self.get(self.url)
    self.assertAcceptedOrgsPageTemplatesUsed(response)
    list_data = self.getListData(self.url, 0)
    #Third organization is self.gci
    self.assertEqual(3, len(list_data))
