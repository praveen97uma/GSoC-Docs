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


"""Tests for invite related views.
"""


from soc.logic.exceptions import BadRequest
from soc.modules.gci.models.request import GCIRequest

from tests.profile_utils import GCIProfileHelper
from tests.test_utils import GCIDjangoTestCase
from tests.utils.invite_utils import GCIInviteHelper


class BaseInviteTest(GCIDjangoTestCase):
  """Base class for invite tests.
  """ 

  def _invitee(self):
    invitee_data = GCIProfileHelper(self.gci, self.dev_test)
    invitee_data.createOtherUser('invitee@example.com')
    invitee_data.createProfile()
    invitee_data.notificationSettings(new_invites=True)
    return invitee_data.profile


class InviteViewTest(BaseInviteTest):
  """Tests user invite views.
  """

  def setUp(self):
    super(InviteViewTest, self).setUp()
    self.init()

  def assertInviteTemplatesUsed(self, response):
    """Asserts that all the templates are used.
    """
    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/invite/base.html')

  def testLoggedInCannotInvite(self):
    url = self._inviteMentorUrl()
    response = self.get(url)
    self.assertResponseForbidden(response)

    url = self._inviteOrgAdminUrl()
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testUserCannotInvite(self):
    self.data.createUser()

    url = self._inviteMentorUrl()
    response = self.get(url)
    self.assertResponseForbidden(response)

    url = self._inviteOrgAdminUrl()
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testMentorCannotInvite(self):
    self.data.createMentor(self.org)

    url = self._inviteMentorUrl()
    response = self.get(url)
    self.assertResponseForbidden(response)

    url = self._inviteOrgAdminUrl()
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testOrgAdminCanInvite(self):
    self.data.createOrgAdmin(self.org)

    url = self._inviteMentorUrl()
    response = self.get(url)
    self.assertInviteTemplatesUsed(response)

    url = self._inviteOrgAdminUrl()
    response = self.get(url)
    self.assertInviteTemplatesUsed(response)

  def testInviteOrgAdmin(self):
    self.data.createOrgAdmin(self.org)

    invitee = self._invitee()
    
    post_data = {
        'identifiers': invitee.user.link_id,
        }
    response = self.post(self._inviteOrgAdminUrl(), post_data)
    self.assertResponseRedirect(response,
        '/gci/dashboard/%s' % self.gci.key().name())

    invite = GCIRequest.all().get()
    self.assertPropertiesEqual(self._defaultOrgAdminInviteProperties(), invite)

  def testInviteMentor(self):
    self.data.createOrgAdmin(self.org)

    invitee = self._invitee()
    
    post_data = {
        'identifiers': invitee.user.link_id,
        }
    response = self.post(self._inviteMentorUrl(), post_data)
    self.assertResponseRedirect(response,
        '/gci/dashboard/%s' % self.gci.key().name())

    invite = GCIRequest.all().get()
    self.assertPropertiesEqual(self._defaultMentorInviteProperties(), invite)

  def testSecondInviteForbidden(self):
    self.data.createOrgAdmin(self.org)
    invitee = self._invitee()

    GCIInviteHelper().createMentorInvite(self.org, invitee.user)

    post_data = {
        'identifiers': invitee.user.link_id,
        }
    response = self.post(self._inviteMentorUrl(), post_data)
    self.assertResponseOK(response)
    self._assertFormValidationError(response, 'identifiers')

  def testOrgAdminInviteAfterMentorInvite(self):
    self.data.createOrgAdmin(self.org)
    invitee = self._invitee()

    GCIInviteHelper().createMentorInvite(self.org, invitee.user)

    post_data = {
        'identifiers': invitee.user.link_id,
        }
    response = self.post(self._inviteOrgAdminUrl(), post_data)
    self.assertResponseRedirect(response,
        '/gci/dashboard/%s' % self.gci.key().name())

    invite = GCIRequest.all().filter('role =', 'org_admin').get()
    self.assertPropertiesEqual(self._defaultOrgAdminInviteProperties(), invite)

  def testMentorInviteAfterOrgAdminInvite(self):
    # TODO(dhans): this test should fail in the future:
    # a existing mentor invite should be extended to become org_admin one

    self.data.createOrgAdmin(self.org)
    invitee = self._invitee()

    GCIInviteHelper().createOrgAdminInvite(self.org, invitee.user)

    post_data = {
        'identifiers': invitee.user.link_id,
        }
    response = self.post(self._inviteMentorUrl(), post_data)
    self.assertResponseRedirect(response,
        '/gci/dashboard/%s' % self.gci.key().name())

    invite = GCIRequest.all().filter('role =', 'mentor').get()
    self.assertPropertiesEqual(self._defaultMentorInviteProperties(), invite)

  def testInviteByEmailAddress(self):
    self.data.createOrgAdmin(self.org)
    self._invitee()

    post_data = {
        'identifiers': 'invitee@example.com'
        }
    response = self.post(self._inviteMentorUrl(), post_data)
    self.assertResponseRedirect(response,
        '/gci/dashboard/%s' % self.gci.key().name())

    invite = GCIRequest.all().get()
    self.assertPropertiesEqual(self._defaultMentorInviteProperties(), invite)

  def testInviteByEmailAddressNotExistingUserForbidden(self):
    self.data.createOrgAdmin(self.org)

    post_data = {
        'identifiers': 'invitee@example.com'
        }
    response = self.post(self._inviteMentorUrl(), post_data)

    self.assertResponseOK(response)
    self._assertFormValidationError(response, 'identifiers')

  def testInviteByEmailAndUsername(self):
    # TODO(dhans): in the perfect world, only one invite should be sent
    self.data.createOrgAdmin(self.org)
    invitee = self._invitee()

    post_data = {
        'identifiers': 'invitee@example.com, %s' % invitee.user.link_id
        }
    response = self.post(self._inviteMentorUrl(), post_data)

    self.assertResponseRedirect(response,
        '/gci/dashboard/%s' % self.gci.key().name())

    invite = GCIRequest.all().fetch(10)
    self.assertEqual(len(invite), 2)
    # we would prefer self.assertEqual(len(invite), 1) 

  def testInviteByInvalidEmailAddressForbidden(self):
    self.data.createOrgAdmin(self.org)
    self._testInviteInvalidEmailAddress('@example.com')
    self._testInviteInvalidEmailAddress('John Smith @example.com')
    self._testInviteInvalidEmailAddress('test@example')
    self._testInviteInvalidEmailAddress('test@example.com>')

  def _testInviteInvalidEmailAddress(self, email):
    post_data = {
        'identifiers': email
        }
    response = self.post(self._inviteMentorUrl(), post_data)

    self.assertResponseOK(response)
    self._assertFormValidationError(response, 'identifiers')

  def _invitee(self):
    invitee_data = GCIProfileHelper(self.gci, self.dev_test)
    invitee_data.createOtherUser('invitee@example.com')
    invitee_data.createProfile()
    invitee_data.notificationSettings(new_invites=True)
    return invitee_data.profile

  def _inviteOrgAdminUrl(self):
    return '/gci/invite/org_admin/%s' % self.org.key().name()

  def _inviteMentorUrl(self):
    return '/gci/invite/mentor/%s' % self.org.key().name()

  def _defaultMentorInviteProperties(self):
    properties = self._defaultInviteProperties()
    properties['role'] = 'mentor'
    return properties

  def _defaultOrgAdminInviteProperties(self):
    properties = self._defaultInviteProperties()
    properties['role'] = 'org_admin'
    return properties

  def _defaultInviteProperties(self):
    return {
        'org': self.org,
        'type': 'Invitation',
        'status': 'pending',
        }

  def _assertFormValidationError(self, response, error_field):
    assert response.context['form'].errors.get(error_field) is not None


class ManageInviteTest(BaseInviteTest):
  """Tests for Manage Invite views.
  """

  def setUp(self):
    super(ManageInviteTest, self).setUp()
    self.init()

    self.invitee = self._invitee()
    self.invite = GCIInviteHelper().createOrgAdminInvite(
        self.org, self.invitee.user)

  def assertInviteTemplatesUsed(self, response):
    """Asserts that all the templates are used.
    """
    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/invite/base.html')

  def testLoggedInCannotManageInvite(self):
    url = self._manageInviteUrl(self.invite)
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testUserCannotManageInvite(self):
    self.data.createUser()

    url = self._manageInviteUrl(self.invite)
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testMentorCannotManageInvite(self):
    self.data.createMentor(self.org)

    url = self._manageInviteUrl(self.invite)
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testOrgAdminCanInvite(self):
    self.data.createOrgAdmin(self.org)

    url = self._manageInviteUrl(self.invite)
    response = self.get(url)
    self.assertInviteTemplatesUsed(response)

  def testInvalidPostDataForbidden(self):
    self.data.createOrgAdmin(self.org)

    # empty post data
    post_data = {}
    response = self.post(self._manageInviteUrl(self.invite), post_data)
    self.assertResponseCode(response, BadRequest.status)

    # only invalid data
    post_data = {
        'invalid_field': ''
        }
    response = self.post(self._manageInviteUrl(self.invite), post_data)
    self.assertResponseCode(response, BadRequest.status)

  def testWithdrawInvite(self):
    self.data.createOrgAdmin(self.org)

    post_data = {
        'withdraw': ''
        }
    response = self.post(self._manageInviteUrl(self.invite), post_data)
    self.assertResponseRedirect(response, self._manageInviteUrl(self.invite))

    new_invite = GCIRequest.all().get()
    self.assertTrue(new_invite.status == 'withdrawn')

  def testPendingInviteCannotBeResubmitted(self):
    self.data.createOrgAdmin(self.org)

    post_data = {
        'resubmit': ''
        }
    response = self.post(self._manageInviteUrl(self.invite), post_data)
    self.assertResponseForbidden(response)

  def testResubmitInvite(self):
    self.data.createOrgAdmin(self.org)

    self.invite.status = 'withdrawn'
    self.invite.put()

    post_data = {
        'resubmit': ''
        }
    response = self.post(self._manageInviteUrl(self.invite), post_data)
    self.assertResponseRedirect(response, self._manageInviteUrl(self.invite))

    new_invite = GCIRequest.all().get()
    self.assertTrue(new_invite.status == 'pending')

  def testAcceptedInviteCannotBeManaged(self):
    self.data.createOrgAdmin(self.org)

    self.invite.status = 'accepted'
    self.invite.put()

    post_data = {
        'resubmit': ''
        }
    response = self.post(self._manageInviteUrl(self.invite), post_data)
    self.assertResponseForbidden(response)

    post_data = {
        'withdraw': ''
        }
    response = self.post(self._manageInviteUrl(self.invite), post_data)
    self.assertResponseForbidden(response)    

  def _manageInviteUrl(self, invite):
    return '/gci/invite/manage/%s/%s' % (
        self.invite.org.scope.key().name(), self.invite.key().id())
