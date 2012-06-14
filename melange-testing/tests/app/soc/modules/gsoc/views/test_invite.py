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

"""Tests for invite view.
"""


from google.appengine.ext import db

from soc.modules.gsoc.models.request import GSoCRequest

from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import GSoCDjangoTestCase
from tests.test_utils import MailTestCase

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class InviteTest(MailTestCase, GSoCDjangoTestCase):
  """Tests invite page.
  """

  def setUp(self):
    super(InviteTest, self).setUp()
    self.init()

  def createInvitation(self):
    """Creates and returns an accepted invitation for the current user.
    """
    return self.data.createInvitation(self.org, 'mentor')

  def assertInviteTemplatesUsed(self, response):
    """Asserts that all the templates from the dashboard were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/invite/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')

  def testInviteOrgAdminNoAdmin(self):
    url = '/gsoc/invite/org_admin/' + self.org.key().name()
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testInviteOrgAdmin(self):
    # test GET
    self.data.createOrgAdmin(self.org)
    url = '/gsoc/invite/org_admin/' + self.org.key().name()
    response = self.get(url)
    self.assertInviteTemplatesUsed(response)

    # create other user to send invite to
    other_data = GSoCProfileHelper(self.gsoc, self.dev_test)
    other_data.createOtherUser('to_be_admin@example.com')
    other_data.createProfile()
    other_data.notificationSettings(new_invites=True)
    other_user = other_data.user

    # test POST
    override = {
        'link_id': other_user.link_id, 'status': 'pending',
        'role': 'org_admin', 'user': other_user, 'org': self.org,
        'type': 'Invitation',
        'parent': other_user,
    }
    response, properties = self.modelPost(url, GSoCRequest, override)
    self.assertEmailSent(to=other_data.profile.email, n=1)

    invitation = GSoCRequest.all().get()
    properties.pop('link_id')
    self.assertPropertiesEqual(properties, invitation)

    other_data2 = GSoCProfileHelper(self.gsoc, self.dev_test)
    other_data2.createOtherUser('to_be_admin2@example.com')
    other_data2.createProfile()
    other_data2.notificationSettings()

    invitation.delete()
    override['link_id'] = 'to_be_admin@example.com, to_be_admin2@example.com'
    other_data.notificationSettings()
    response, properties = self.modelPost(url, GSoCRequest, override)
    self.assertEmailSent(to=other_data.profile.email, n=1)

    invitations = GSoCRequest.all().fetch(2)
    self.assertEqual(2, len(invitations))
    invitation = invitations[0]
    properties.pop('link_id')
    self.assertPropertiesEqual(properties, invitation)
    properties['user'] = other_data2.user
    properties['parent'] = other_data2.user
    self.assertPropertiesEqual(properties, invitations[1])

    # test withdraw/resubmit invite
    url = '/gsoc/invitation/%s/%s/%s' % (
	self.gsoc.key().name(),
	invitation.parent_key().name(),
	invitation.key().id())

    other_data.notificationSettings(invite_handled=True)

    postdata = {'action': 'Withdraw'}
    response = self.post(url, postdata)
    self.assertResponseRedirect(response)
    invite = GSoCRequest.all().get()
    self.assertEqual('withdrawn', invite.status)
    self.assertEmailSent(to=other_data.profile.email, n=2)

    # test that you can resubmit
    postdata = {'action': 'Resubmit'}
    response = self.post(url, postdata)
    self.assertResponseRedirect(response)
    invite = GSoCRequest.all().get()
    self.assertEqual('pending', invite.status)
    self.assertEmailSent(to=other_data.profile.email, n=3)

  def testInviteMentor(self):
    self.data.createOrgAdmin(self.org)
    url = '/gsoc/invite/mentor/' + self.org.key().name()
    response = self.get(url)
    self.assertInviteTemplatesUsed(response)

  def testViewInvite(self):
    self.data.createProfile()
    invitation = self.createInvitation()
    url = '/gsoc/invitation/%s/%s/%s' % (
	self.gsoc.key().name(),
	invitation.parent_key().name(),
	invitation.key().id())
    response = self.get(url)
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/soc/request/base.html')

    postdata = {'action': 'Reject'}
    response = self.post(url, postdata)
    self.assertResponseRedirect(response)
    invitation = GSoCRequest.all().get()
    self.assertEqual('rejected', invitation.status)

    # test that you can change after the fact
    postdata = {'action': 'Accept'}
    response = self.post(url, postdata)
    self.assertResponseRedirect(response)

    profile = db.get(self.data.profile.key())
    self.assertEqual(1, profile.mentor_for.count(self.org.key()))
    self.assertTrue(profile.is_mentor)
    self.assertFalse(profile.is_student)
    self.assertFalse(profile.is_org_admin)
    self.assertFalse(profile.org_admin_for)

    # test admin invite
    invitation.status = 'pending'
    invitation.role = 'org_admin'
    invitation.put()

    response = self.post(url, postdata)
    self.assertResponseRedirect(response)

    profile = db.get(self.data.profile.key())
    self.assertEqual(1, profile.mentor_for.count(self.org.key()))
    self.assertEqual(1, profile.org_admin_for.count(self.org.key()))
    self.assertFalse(profile.is_student)
    self.assertTrue(profile.is_mentor)
    self.assertTrue(profile.is_org_admin)
