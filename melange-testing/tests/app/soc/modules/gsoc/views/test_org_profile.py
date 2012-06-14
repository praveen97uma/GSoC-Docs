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


"""Tests for GSoC Organization profile related views.
"""


from google.appengine.ext import db

from soc.modules.seeder.logic.seeder import logic as seeder_logic

from tests.test_utils import GSoCDjangoTestCase

#TODO(Praveen): Test r'profile/organization/%s$' % url_patterns.PROGRAM when
#org creation is implemented.

class OrgProfilePageTest(GSoCDjangoTestCase):
  """Tests the view for organization profile page.
  """

  def setUp(self):
    self.init()

  def assertOrgProfilePageTemplatesUsed(self, response):
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/org_profile/base.html')

  #TODO(Praveen): Activate this test as soon as the timeline checks are in place.
  """
  def testOrgProfilePageOffSeason(self):
    '''Tests that it is forbidden to create or edit an org profile during off 
    season.
    '''
    self.timeline.offSeason()
    self.data.createOrgAdmin(self.org)
    #Profile creation URL is not implemented currently.
    url = '/gsoc/profile/organization/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertResponseForbidden(response)

    url = '/gsoc/profile/organization/' + self.org.key().name()
    response = self.get(url)
    self.assertResponseForbidden(response)
  """
  
  def testAUserNotLoggedInIsRedirectedToLoginPage(self):
    """Tests that a user who is not logged in is redirected to its login page.
    """
    import os
    current_logged_in_account = os.environ.get('USER_EMAIL', None)
    try:
      os.environ['USER_EMAIL'] = ''
      #TODO(Praveen): Activate code below when org profile creation is implemented.
      #url = '/gsoc/profile/organization/' + self.gsoc.key().name()
      #response = self.get(url)
      #self.assertResponseRedirect(response)

      url = '/gsoc/profile/organization/' + self.org.key().name()
      response = self.get(url)
      self.assertResponseRedirect(response)
      expected_redirect_address = 'https://www.google.com/accounts/Login?'\
          +'continue=http%3A//Foo%3A8080' + url
      actual_redirect_address = response.get('location', None)
      self.assertEqual(expected_redirect_address, actual_redirect_address)
    finally:
      if current_logged_in_account is None:
        del os.environ['USER_EMAIL']
      else:
        os.environ['USER_EMAIL'] = current_logged_in_account

  def testAUserWithoutProfileIsForbiddenToEditAnOrgProfilePage(self):
    """Tests that a user without a profile can not edit an org profile.
    """
    self.timeline.kickoff()
    url = '/gsoc/profile/organization/' + self.org.key().name()
    self.data.createUser()
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testOnlyACorrectOrgAdminCanEditAnrOrgProfilePage(self):
    """Tests that only the assigned org admin for an organization can edit the
    org profile.
    """
    self.timeline.orgSignup()
    #make the current user to be a mentor for self.org and test for 403.
    self.data.createMentor(self.org)
    url = '/gsoc/profile/organization/' + self.org.key().name()
    self.timeline.orgSignup()
    response = self.get(url)
    self.assertResponseForbidden(response)

    from soc.modules.gsoc.models.organization import GSoCOrganization
    other_organization = seeder_logic.seed(GSoCOrganization)
    self.data.createOrgAdmin(other_organization)
    url = '/gsoc/profile/organization/' + self.org.key().name()
    response = self.get(url)
    self.assertResponseForbidden(response)

    #make the current logged in user to be admin for self.org.
    self.data.createOrgAdmin(self.org)
    self.gsoc.allocations_visible = False
    self.gsoc.put()

    url = '/gsoc/profile/organization/' + self.org.key().name()
    response = self.get(url)
    self.assertResponseOK(response)
    self.assertOrgProfilePageTemplatesUsed(response)

    context = response.context
    self.assertEqual(context['page_name'], 'Organization profile')
    self.assertTrue('org_home_page_link' in context)
    self.assertTrue('page_name' in context)
    self.assertFalse('slot_transfer_page_link' in context)

    self.gsoc.allocations_visible = True
    self.gsoc.put()
    response = self.get(url)
    self.assertResponseOK(response)
    self.assertOrgProfilePageTemplatesUsed(response)
    self.assertTrue('slot_transfer_page_link' in response.context)

    self.timeline.studentsAnnounced()
    response = self.get(url)
    self.assertResponseOK(response)
    self.assertOrgProfilePageTemplatesUsed(response)
    self.assertFalse('slot_transfer_page_link' in response.context)
    
  def test404IsReturnedWhenOrgDoesNotExists(self):
    """Tests that when an org admin tries to access the profile page for an
    org which does not exists a 404 is shown.
    """
    self.data.createOrgAdmin(self.org)
    suffix = '%s/%s/%s' % (self.sponsor.link_id, self.gsoc.link_id, 
                           'non_existing_link_id')
    url = '/gsoc/profile/organization/' + suffix
    import httplib
    response = self.get(url)
    self.assertResponseCode(response, httplib.NOT_FOUND)
    
  def testAnOrgAdminCanUpdateOrgProfile(self):
    """Tests if an org admin can update the profile for its organization.
    """
    self.timeline.orgSignup()
    from soc.modules.gsoc.models.organization import GSoCOrganization
    self.data.createOrgAdmin(self.org)

    url = '/gsoc/profile/organization/' + self.org.key().name()
    postdata = seeder_logic.seed_properties(GSoCOrganization)
    updates = {
        'email': 'temp@gmail.com', 'irc_channel': 'irc://i.f.net/gsoc',
        'pub_mailing_list': 'https://l.s.net',
        'tags': 'foo, bar', 'gsoc_org_page_home': 'http://www.xyz.com',
        'contact_postalcode': '247667', 'contact_country': 'India',
        'dev_mailing_list': 'http://d.com', 'home': postdata['home'].key(),
        'max_score': 5,
    }
    postdata.update(updates)
    self.assertNotEqual(updates['email'], self.org.email)
    response = self.post(url, postdata)
    self.assertResponseRedirect(response)
    
    expected_redirect_url = 'http://testserver' + url + '?validated'
    actual_redirect_url = response.get('location', None)
    self.assertEqual(expected_redirect_url, actual_redirect_url)
     
    updated_org = db.get(self.org.key())
    self.assertEqual(updates['email'], updated_org.email)
    
