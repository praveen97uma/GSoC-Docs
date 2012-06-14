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


from soc.modules.seeder.logic.seeder import logic as seeder_logic

from tests.test_utils import GSoCDjangoTestCase

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class ProfileViewTest(GSoCDjangoTestCase):
  """Tests user profile views.
  """

  def setUp(self):
    self.init()

  def assertProfileTemplatesUsed(self, response):
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/profile/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')

  def testCreateProfilePage(self):
    self.timeline.studentSignup()
    url = '/gsoc/profile/student/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertProfileTemplatesUsed(response)

  def testCreateMentorProfilePage(self):
    self.timeline.studentSignup()
    url = '/gsoc/profile/mentor/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertProfileTemplatesUsed(response)

  def testRedirectWithStudentProfilePage(self):
    self.timeline.studentSignup()
    self.data.createStudent()
    url = '/gsoc/profile/student/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertResponseRedirect(response)

  def testForbiddenWithStudentProfilePage(self):
    self.timeline.studentSignup()
    self.data.createStudent()
    url = '/gsoc/profile/mentor/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testForbiddenWithMentorProfilePage(self):
    self.timeline.studentSignup()
    self.data.createMentor(self.org)
    url = '/gsoc/profile/student/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testEditProfilePage(self):
    self.timeline.studentSignup()
    self.data.createProfile()
    url = '/gsoc/profile/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertResponseOK(response)

  def testCreateProfile(self):
    from soc.modules.gsoc.models.profile import GSoCProfile
    from soc.modules.gsoc.models.profile import GSoCStudentInfo

    self.timeline.studentSignup()
    self.data.createUser()

    suffix = "%(program)s" % {
        'program': self.gsoc.key().name(),
        }

    role_suffix = "%(role)s/%(suffix)s" % {
        'role': 'student',
        'suffix': suffix,
        }

    url = '/gsoc/profile/' + suffix
    role_url = '/gsoc/profile/' + role_suffix


    # we do not want to seed the data in the datastore, we just
    # want to get the properties generated for seeding. The post
    # test will actually do the entity creation, so we reuse the
    # seed_properties method from the seeder to get the most common
    # values for Profile and StudentInfo
    postdata = seeder_logic.seed_properties(GSoCProfile)
    props = seeder_logic.seed_properties(GSoCStudentInfo, properties={
        'tax_form': None,
        'enrollment_form': None,
    })
    props.pop('tax_form')
    props.pop('enrollment_form')
    postdata.update(props)
    postdata.update({
        'link_id': self.data.user.link_id,
        'student_info': None,
        'user': self.data.user, 'parent': self.data.user,
        'scope': self.gsoc, 'status': 'active',
        'email': self.data.user.account.email(),
        'mentor_for': [], 'org_admin_for': [],
        'is_org_admin': False, 'is_mentor': False,
    })

    response = self.post(role_url, postdata)

    self.assertResponseRedirect(response, url + '?validated')

    # hacky
    profile = GSoCProfile.all().get()
    profile.delete()

    postdata.update({
        'email': 'somerandominvalid@emailid',
        })

    response = self.post(role_url, postdata)

    # yes! this is the protocol for form posts. We get an OK response
    # with the response containing the form's GET request page whenever
    # the form has an error and could not be posted. This is the architecture
    # chosen in order to save the form error state's while rendering the
    # error fields.
    self.assertResponseOK(response)

    error_dict = response.context['error']
    self.assertTrue('email' in error_dict)
