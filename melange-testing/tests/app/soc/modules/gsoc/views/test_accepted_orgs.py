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


"""Tests the view for GSoC accepted orgs.
"""


from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.seeder.logic.seeder import logic as seeder_logic

from tests.test_utils import GSoCDjangoTestCase


class AcceptedOrgsPageTest(GSoCDjangoTestCase):
  """Tests the page to display accepted organization.
  """
  
  def setUp(self):
    self.init()
    self.url1 = '/gsoc/accepted_orgs/' + self.gsoc.key().name()
    self.url2 = '/gsoc/program/accepted_orgs/' + self.gsoc.key().name()
    self.url3 = '/program/accepted_orgs/' + self.gsoc.key().name()
    
  def assertAcceptedOrgsPageTemplatesUsed(self, response):
    """Asserts that all the required templates to render the page were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/accepted_orgs/base.html')
    self.assertTemplateUsed(response, 
                            'v2/modules/gsoc/accepted_orgs/_project_list.html')
    self.assertTemplateUsed(response, 'v2/soc/_program_select.html')
    self.assertTemplateUsed(response, 
                            'v2/modules/gsoc/accepted_orgs/_project_list.html') 
    self.assertTemplateUsed(response, 'v2/soc/list/lists.html') 
    self.assertTemplateUsed(response, 'v2/soc/list/list.html')
    
  def testAcceptedOrgsAreDisplayedOnlyAfterTheyAreAnnounced(self):
    """Tests that the list of accepted organizations can be accessed only after
    the organizations have been announced.
    """
    self.timeline.orgSignup()
    response = self.get(self.url3)
    self.assertResponseForbidden(response)
    
    response = self.get(self.url2)
    self.assertResponseForbidden(response)
    
    response = self.get(self.url1)
    self.assertResponseForbidden(response)
    
  def testAcceptedOrgsAreDisplayedAfterOrganizationsHaveBeenAnnounced(self):
    """Tests that the list of the organizations can not be accessed before 
    organizations have been announced.
    """
    org_properties = {'scope': self.gsoc, 'status': 'active'}
    seeder_logic.seed(GSoCOrganization, org_properties)
    seeder_logic.seed(GSoCOrganization, org_properties)
    self.timeline.orgsAnnounced()
    
    response = self.get(self.url1)
    self.assertResponseOK(response)
    self.assertAcceptedOrgsPageTemplatesUsed(response)
    list_data = self.getListData(self.url1, 0)
    #Third organization is self.gsoc
    self.assertEqual(len(list_data), 3)
    
    response = self.get(self.url2)
    self.assertResponseOK(response)
    self.assertAcceptedOrgsPageTemplatesUsed(response)
    list_data = self.getListData(self.url2, 0)
    self.assertEqual(len(list_data), 3)

    response = self.get(self.url3)
    self.assertResponseOK(response)
    self.assertAcceptedOrgsPageTemplatesUsed(response)
    list_data = self.getListData(self.url3, 0)
    self.assertEqual(len(list_data), 3)

