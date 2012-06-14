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


"""Tests for program homepage related views.
"""


from tests.test_utils import GSoCDjangoTestCase

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class HomepageViewTest(GSoCDjangoTestCase):
  """Tests program homepage views.
  """

  def setUp(self):
    self.init()

  def assertHomepageTemplatesUsed(self, response):
    """Asserts that all the templates from the homepage view were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_connect_with_us.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/homepage/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/homepage/_apply.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/homepage/_timeline.html')

  def testHomepageAnonymous(self):
    """Tests the homepage as an anonymous user throughout the program.
    """
    url = '/gsoc/homepage/' + self.gsoc.key().name()

    self.timeline.offSeason()
    response = self.get(url)
    self.assertHomepageTemplatesUsed(response)

    self.timeline.kickoff()
    response = self.get(url)
    self.assertHomepageTemplatesUsed(response)

    self.timeline.orgSignup()
    response = self.get(url)
    self.assertHomepageTemplatesUsed(response)

    self.timeline.orgsAnnounced()
    response = self.get(url)
    self.assertHomepageTemplatesUsed(response)

    self.timeline.studentSignup()
    response = self.get(url)
    self.assertHomepageTemplatesUsed(response)

    self.timeline.studentsAnnounced()
    response = self.get(url)
    self.assertHomepageTemplatesUsed(response)

  def testHomepageDuringSignup(self):
    """Tests the student homepage during the signup period.
    """
    self.timeline.studentsAnnounced()
    url = '/gsoc/homepage/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertHomepageTemplatesUsed(response)
    timeline_tmpl = response.context['timeline']
    apply_context = response.context['apply'].context()
    self.assertEqual(timeline_tmpl.current_timeline, 'coding_period')
    self.assertTrue('profile_link' in apply_context)

    # Show featured_project
    student = GSoCProfileHelper(self.gsoc, self.dev_test)
    student.createOtherUser('student@example.com')
    student_entity = student.createMentor(self.org)

    mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor.createOtherUser('mentor@example.com')
    mentor_entity = mentor.createMentor(self.org)

    project = self.createProject({'parent': student_entity,
                                 'mentor': mentor_entity, 'featured': True })

    response = self.get(url)
    self.assertHomepageTemplatesUsed(response)
    self.assertTemplateUsed(
        response, 'v2/modules/gsoc/homepage/_featured_project.html')

    featured_project_tmpl = response.context['featured_project']
    self.assertEqual(featured_project_tmpl.featured_project.key().
                     project.key())

  def testHomepageAfterStudentsAnnounceed(self):
    """Tests the student homepage after the student's have been announced.
    """
    self.timeline.student
    url = '/gsoc/homepage/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertHomepageTemplatesUsed(response)
    timeline_tmpl = response.context['timeline']
    apply_context = response.context['apply'].context()
    self.assertEqual(timeline_tmpl.current_timeline, 'student_signup_period')
    self.assertTrue('profile_link' in apply_context)

  def testHomepageDuringSignupExistingUser(self):
    """Tests the student hompepage during the signup period with an existing user.
    """
    self.data.createProfile()
    self.timeline.studentSignup()
    url = '/gsoc/homepage/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertHomepageTemplatesUsed(response)
    apply_tmpl = response.context['apply']
    self.assertTrue(apply_tmpl.data.profile)
    self.assertFalse('profile_link' in apply_tmpl.context())
