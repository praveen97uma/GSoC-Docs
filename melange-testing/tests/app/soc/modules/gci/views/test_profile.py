#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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


"""Tests for user profile related views.
"""


from datetime import date
from datetime import timedelta

from soc.modules.seeder.logic.seeder import logic as seeder_logic

from soc.modules.gci.models.profile import GCIProfile

from tests.test_utils import GCIDjangoTestCase


class ProfileViewTest(GCIDjangoTestCase):
  """Tests user profile views.
  """

  def setUp(self):
    from soc.modules.gci.models.profile import GCIProfile
    from soc.modules.gci.models.profile import GCIStudentInfo

    self.init()

    program_suffix = self.gci.key().name()

    self.url = '/gci/profile/%(program_suffix)s' % {
        'program_suffix': program_suffix
        }
    
    self.validated_url = self.url + '?validated'

    self.student_url = '/gci/profile/%(role)s/%(program_suffix)s' % {
        'role': 'student',
        'program_suffix': program_suffix                                                            
        }

    self.birth_date = str(date.today() - timedelta(365*15))

    props = {}
    # we do not want to seed the data in the datastore, we just
    # want to get the properties generated for seeding. The post
    # test will actually do the entity creation, so we reuse the
    # seed_properties method from the seeder to get the most common
    # values for Profile and StudentInfo
    props.update(seeder_logic.seed_properties(GCIProfile))
    props.update(seeder_logic.seed_properties(GCIStudentInfo))

    props.update({
        'student_info': None,
        'status': 'active',
        'is_org_admin': False,
        'is_mentor': False,
        'org_admin_for': [],
        'mentor_for': [],
        'scope': self.gci,
        'birth_date': self.birth_date,
        'res_country': 'Netherlands',
        'ship_country': 'Netherlands',
    })

    self.default_props = props

    # we have other tests that verify the age_check system
    self.client.cookies['age_check'] = self.birth_date

  def _updateDefaultProps(self, request_data):
    """Updates default_props variable with more personal data stored in
    the specified request_data object.
    """
    self.default_props.update({
        'link_id': request_data.user.link_id,
        'user': request_data.user,
        'parent': request_data.user,
        'email': request_data.user.account.email()
        })

  def assertProfileTemplatesUsed(self, response):
    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/profile/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gci/_form.html')

  def testCreateProfilePage(self):
    self.timeline.studentSignup()
    url = '/gci/profile/student/' + self.gci.key().name()
    self.client.cookies['age_check'] = '1'
    response = self.get(url)
    self.assertProfileTemplatesUsed(response)

  def testCreateMentorProfilePage(self):
    self.timeline.studentSignup()
    url = '/gci/profile/mentor/' + self.gci.key().name()
    response = self.get(url)
    self.assertProfileTemplatesUsed(response)

  def testRedirectWithStudentProfilePage(self):
    self.timeline.studentSignup()
    self.data.createStudent()
    url = '/gci/profile/student/' + self.gci.key().name()
    response = self.get(url)
    redirect_url = '/gci/profile/' + self.gci.key().name()
    self.assertResponseRedirect(response, redirect_url)

  def testRedirectWithMentorProfilePage(self):
    self.timeline.studentSignup()
    self.data.createMentor(self.org)
    url = '/gci/profile/mentor/' + self.gci.key().name()
    response = self.get(url)
    response_url = '/gci/profile/' + self.gci.key().name()
    self.assertResponseRedirect(response, response_url)

  def testForbiddenWithStudentProfilePage(self):
    self.timeline.studentSignup()
    self.data.createStudent()
    url = '/gci/profile/mentor/' + self.gci.key().name()
    response = self.get(url)
    self.assertResponseForbidden(response)
    url = '/gci/profile/org_admin/' + self.gci.key().name()
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testForbiddenWithMentorProfilePage(self):
    self.timeline.studentSignup()
    self.data.createMentor(self.org)
    url = '/gci/profile/student/' + self.gci.key().name()
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testEditProfilePage(self):
    self.timeline.studentSignup()
    self.data.createProfile()
    url = '/gci/profile/' + self.gci.key().name()
    response = self.get(url)
    self.assertResponseOK(response)

  #TODO(daniel): this test should work, when we disable edition of profiles
  # after the project is over
  #def testEditProfilePageInactive(self):
  #  self.timeline.offSeason()
  #  self.data.createProfile()
  #  url = '/gci/profile/' + self.gci.key().name()
  #  response = self.get(url)
  #  self.assertResponseForbidden(response)

  def testCreateUser(self):
    self.timeline.studentSignup()

    self.default_props.update({
        'link_id': 'test',
        })

    response = self.post(self.student_url, self.default_props)
    self.assertResponseRedirect(response, self.validated_url)

    self.assertEqual(1, GCIProfile.all().count())
    student = GCIProfile.all().get()

    self.assertEqual(self.birth_date, str(student.birth_date))

  def testCreateUserNoLinkId(self):
    self.timeline.studentSignup()

    self.default_props.update({
        })

    response = self.post(self.student_url, self.default_props)
    self.assertResponseOK(response)
    self.assertTrue('link_id' in response.context['error'])

  def testCreateProfile(self):
    from soc.modules.gci.models.profile import GCIStudentInfo

    self.timeline.studentSignup()
    self.data.createUser()
    self._updateDefaultProps(self.data)
    postdata = self.default_props

    response = self.post(self.student_url, postdata)
    self.assertResponseRedirect(response, self.validated_url)

    # hacky
    profile = GCIProfile.all().get()
    profile.delete()

    postdata.update({
        'email': 'somerandominvalid@emailid',
        })

    response = self.post(self.student_url, postdata)

    # yes! this is the protocol for form posts. We get an OK response
    # with the response containing the form's GET request page whenever
    # the form has an error and could not be posted. This is the architecture
    # chosen in order to save the form error state's while rendering the
    # error fields.
    self.assertResponseOK(response)

    error_dict = response.context['error']
    self.assertTrue('email' in error_dict)
