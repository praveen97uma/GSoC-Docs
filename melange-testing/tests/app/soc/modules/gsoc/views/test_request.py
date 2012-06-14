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


class RequestTest(MailTestCase, GSoCDjangoTestCase):
  """Tests request page.
  """

  def setUp(self):
    super(RequestTest, self).setUp()
    self.init()

  def createRequest(self):
    """Creates and returns an accepted invitation for the current user.
    """
    # create other user to send invite to
    other_data = GSoCProfileHelper(self.gsoc, self.dev_test)
    other_data.createOtherUser('to_be_mentor@example.com')
    other_data.createProfile()
    request = other_data.createMentorRequest(self.org)

    return (other_data, request)

  def assertRequestTemplatesUsed(self, response):
    """Asserts that all the request templates were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/invite/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')

  def testRequestMentor(self):
    admin = GSoCProfileHelper(self.gsoc, self.dev_test)
    admin.createOtherUser('admin@example.com')
    admin.createOrgAdmin(self.org)
    admin.notificationSettings(new_requests=True)

    other_admin = GSoCProfileHelper(self.gsoc, self.dev_test)
    other_admin.createOtherUser('other_admin@example.com')
    other_admin.createOrgAdmin(self.org)
    other_admin.notificationSettings()

    # test GET
    self.data.createProfile()
    url = '/gsoc/request/' + self.org.key().name()
    response = self.get(url)
    self.assertRequestTemplatesUsed(response)

    # test POST
    override = {'status': 'pending', 'role': 'mentor', 'type': 'Request',
                'user': self.data.user, 'org': self.org}
    response, properties = self.modelPost(url, GSoCRequest, override)

    request = GSoCRequest.all().get()
    self.assertPropertiesEqual(properties, request)

    self.assertEmailSent(to=admin.profile.email, n=1)
    self.assertEmailNotSent(to=other_admin.profile.email)

    # test withdrawing a request
    url = '/gsoc/request/%s/%s/%s' % (
        self.gsoc.key().name(),
        request.parent_key().name(),
        request.key().id())

    postdata = {'action': 'Withdraw'}
    response = self.post(url, postdata)
    self.assertResponseRedirect(response)
    request = GSoCRequest.all().get()
    self.assertEqual('withdrawn', request.status)

    # test that you can resubmit
    postdata = {'action': 'Resubmit'}
    response = self.post(url, postdata)
    self.assertResponseRedirect(response)
    request = GSoCRequest.all().get()
    self.assertEqual('pending', request.status)

  def testAcceptRequest(self):
    self.data.createOrgAdmin(self.org)
    other_data, request = self.createRequest()
    other_data.notificationSettings(request_handled=True)
    url = '/gsoc/request/%s/%s/%s' % (
        self.gsoc.key().name(),
        request.parent_key().name(),
        request.key().id())
    response = self.get(url)
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/soc/request/base.html')

    postdata = {'action': 'Reject'}
    response = self.post(url, postdata)
    self.assertResponseRedirect(response)
    request = GSoCRequest.all().get()
    self.assertEqual('rejected', request.status)

    self.assertEmailSent(to=other_data.profile.email, n=1)

    # test that you can change after the fact
    postdata = {'action': 'Accept'}
    response = self.post(url, postdata)

    def checkPostAccept():
      self.assertResponseRedirect(response)
      request = GSoCRequest.all().get()
      self.assertEqual('accepted', request.status)

      profile = db.get(other_data.profile.key())
      self.assertEqual(1, profile.mentor_for.count(self.org.key()))
      self.assertTrue(profile.is_mentor)
      self.assertFalse(profile.is_student)
      self.assertFalse(profile.is_org_admin)
      self.assertFalse(profile.org_admin_for)

    checkPostAccept()

    self.assertEmailSent(to=other_data.profile.email, n=2)

    request.status = 'pending'
    request.put()
    other_data.notificationSettings()

    response = self.post(url, postdata)

    checkPostAccept()
    self.assertEmailSent(to=other_data.profile.email, n=2)
