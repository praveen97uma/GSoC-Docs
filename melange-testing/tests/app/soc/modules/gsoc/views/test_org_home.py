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


"""Tests for Organization homepage related views.
"""


from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import GSoCDjangoTestCase


class OrgHomeProjectListTest(GSoCDjangoTestCase):
  """Tests organization homepage views.
  """

  def setUp(self):
    self.init()

  def createStudentProjects(self):
    """Creates two student projects.
    """
    from soc.modules.gsoc.models.student_project import StudentProject
    mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor.createOtherUser('mentor@example.com').createMentor(self.org)

    student = GSoCProfileHelper(self.gsoc, self.dev_test)
    student.createOtherUser('student@example.com')
    student.createStudentWithProjects(self.org, mentor.profile, 2)

  def assertOrgHomeTemplatesUsed(self, response, show_project_list):
    """Asserts that all the org home templates were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_connect_with_us.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/org_home/base.html')

    if show_project_list:
      self.assertTemplateUsed(
          response, 'v2/modules/gsoc/org_home/_project_list.html')
    else:
      self.assertTemplateNotUsed(
          response, 'v2/modules/gsoc/org_home/_project_list.html')

  def testOrgHomeDuringOrgSignup(self):
    """Tests the the org home page during the organization signup period.
    """
    self.timeline.orgSignup()
    url = '/gsoc/org/' + self.org.key().name()
    response = self.get(url)
    self.assertOrgHomeTemplatesUsed(response, False)

  def testOrgHomeDuringStudentSignup(self):
    """Tests the the org home page during the student signup period.
    """
    self.timeline.studentSignup()
    url = '/gsoc/org/' + self.org.key().name()
    response = self.get(url)
    self.assertOrgHomeTemplatesUsed(response, False)

  def testOrgHomeAfterStudentProjectsAnnounced(self):
    """Tests the the org home page after announcing accepted student projects.
    """
    self.timeline.studentsAnnounced()
    self.createStudentProjects()
    url = '/gsoc/org/' + self.org.key().name()
    response = self.get(url)
    self.assertOrgHomeTemplatesUsed(response, True)
    data = self.getListData(url, 0)
    self.assertEqual(2, len(data))

  def testOrgHomeDuringOffseason(self):
    """Tests the the org home page after GSoC is over.
    """
    self.timeline.offSeason()
    self.createStudentProjects()
    url = '/gsoc/org/' + self.org.key().name()
    response = self.get(url)
    self.assertOrgHomeTemplatesUsed(response, True)
    data = self.getListData(url, 0)
    self.assertEqual(2, len(data))


class OrgHomeApplyTest(GSoCDjangoTestCase):
  """Tests organization homepage views.
  """

  def setUp(self):
    self.init()

  def homepageContext(self):
    url = '/gsoc/org/' + self.org.key().name()
    response = self.get(url)
    self.assertResponseOK(response)
    return response.context

  def assertNoStudent(self, context):
    self.assertFalse('student_apply_block' in context)
    self.assertFalse('student_profile_link' in context)
    self.assertFalse('submit_proposal_link' in context)

  def assertNoMentor(self, context):
    self.assertFalse('mentor_apply_block' in context)
    self.assertFalse('mentor_profile_link' in context)
    self.assertFalse('role' in context)
    self.assertFalse('mentor_applied' in context)
    self.assertFalse('invited_role' in context)
    self.assertFalse('mentor_request_link' in context)

  def assertMentor(self):
    self.data.createMentor(self.org)
    context = self.homepageContext()
    self.assertNoStudent(context)

    self.assertTrue('mentor_apply_block' in context)
    self.assertFalse('mentor_profile_link' in context)
    self.assertEqual('a mentor', context['role'])
    self.assertFalse('mentor_applied' in context)
    self.assertFalse('invited_role' in context)
    self.assertFalse('mentor_request_link' in context)

  def testAnonymousPreSignup(self):
    self.timeline.orgSignup()
    context = self.homepageContext()
    self.assertNoStudent(context)

    self.assertTrue('mentor_apply_block' in context)
    self.assertTrue('mentor_profile_link' in context)
    self.assertFalse('role' in context)
    self.assertFalse('mentor_applied' in context)
    self.assertFalse('invited_role' in context)
    self.assertFalse('mentor_request_link' in context)

  def testAnonymousDuringSignup(self):
    self.timeline.studentSignup()
    context = self.homepageContext()
    self.assertTrue('student_apply_block' in context)
    self.assertTrue('student_profile_link' in context)
    self.assertFalse('submit_proposal_link' in context)

    self.assertFalse('mentor_apply_block' in context)
    self.assertTrue('mentor_profile_link' in context)
    self.assertFalse('role' in context)
    self.assertFalse('mentor_applied' in context)
    self.assertFalse('invited_role' in context)
    self.assertFalse('mentor_request_link' in context)

  def testAnonymousPostSignup(self):
    self.timeline.postStudentSignup()
    context = self.homepageContext()
    self.assertNoStudent(context)

    self.assertTrue('mentor_apply_block' in context)
    self.assertTrue('mentor_profile_link' in context)
    self.assertFalse('role' in context)
    self.assertFalse('mentor_applied' in context)
    self.assertFalse('invited_role' in context)
    self.assertFalse('mentor_request_link' in context)

  def testAnonymousStudentsAnnounced(self):
    self.timeline.studentsAnnounced()
    context = self.homepageContext()
    self.assertNoStudent(context)

    self.assertFalse('mentor_apply_block' in context)
    self.assertFalse('mentor_profile_link' in context)
    self.assertFalse('role' in context)
    self.assertFalse('mentor_applied' in context)
    self.assertFalse('invited_role' in context)
    self.assertFalse('mentor_request_link' in context)

  def testMentorPreSignup(self):
    self.timeline.orgSignup()
    self.assertMentor()

  def testMentorDuringSignup(self):
    self.timeline.studentSignup()
    self.assertMentor()

  def testMentorPostSignup(self):
    self.timeline.postStudentSignup()
    self.assertMentor()

  def testMentorStudentsAnnounced(self):
    self.timeline.studentsAnnounced()
    self.assertMentor()

  def testOrgAdmin(self):
    self.data.createOrgAdmin(self.org)
    context = self.homepageContext()
    self.assertNoStudent(context)

    self.assertTrue('mentor_apply_block' in context)
    self.assertFalse('mentor_profile_link' in context)
    self.assertEqual('an administrator', context['role'])
    self.assertFalse('mentor_applied' in context)
    self.assertFalse('invited_role' in context)
    self.assertFalse('mentor_request_link' in context)

  def testAppliedMentor(self):
    self.data.createMentorRequest(self.org)
    context = self.homepageContext()
    self.assertNoStudent(context)

    self.assertTrue('mentor_apply_block' in context)
    self.assertFalse('mentor_profile_link' in context)
    self.assertFalse('role' in context)
    self.assertTrue('mentor_applied' in context)
    self.assertFalse('invited_role' in context)
    self.assertFalse('mentor_request_link' in context)

  def testInvitedMentor(self):
    self.data.createInvitation(self.org, 'mentor')
    context = self.homepageContext()
    self.assertNoStudent(context)

    self.assertTrue('mentor_apply_block' in context)
    self.assertFalse('mentor_profile_link' in context)
    self.assertFalse('role' in context)
    self.assertFalse('mentor_applied' in context)
    self.assertEqual('a mentor', context['invited_role'])
    self.assertFalse('mentor_request_link' in context)

  def testInvitedOrgAdmin(self):
    self.data.createInvitation(self.org, 'org_admin')
    context = self.homepageContext()
    self.assertNoStudent(context)

    self.assertTrue('mentor_apply_block' in context)
    self.assertFalse('mentor_profile_link' in context)
    self.assertFalse('role' in context)
    self.assertFalse('mentor_applied' in context)
    self.assertEqual('an administrator', context['invited_role'])
    self.assertFalse('mentor_request_link' in context)

  def testStudentDuringSignup(self):
    self.timeline.studentSignup()
    self.data.createStudent()
    context = self.homepageContext()
    self.assertTrue('student_apply_block' in context)
    self.assertFalse('student_profile_link' in context)
    self.assertTrue('submit_proposal_link' in context)
    self.assertNoMentor(context)

  def testStudentPostSignup(self):
    self.timeline.postStudentSignup()
    self.data.createStudent()
    context = self.homepageContext()
    self.assertNoStudent(context)
    self.assertNoStudent(context)
