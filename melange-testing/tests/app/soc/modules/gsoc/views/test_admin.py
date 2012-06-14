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

"""Tests for admin dashboard view.
"""


import httplib

from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import GSoCDjangoTestCase
from tests.timeline_utils import GSoCTimelineHelper


class AdminDashboardTest(GSoCDjangoTestCase):
  """Tests admin dashboard page.
  """

  def setUp(self):
    self.init()

  def adminDashboardContext(self, colorbox=False):
    url = '/gsoc/admin/' + self.gsoc.key().name()
    if colorbox:
      url += '?colorbox=true'
    response = self.get(url)
    self.assertResponseOK(response)
    return response.context

  def assertAdminBaseTemplatesUsed(self, response):
    """Asserts that all the templates from the admin page were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/admin/base.html')

  def assertDashboardTemplatesUsed(self, response):
    """Asserts that all the templates to render a dashboard were used.
    """
    self.assertAdminBaseTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/soc/dashboard/base.html')

  def assertUserActionsTemplatesUsed(self, response):
    """Asserts that all the templates to render user actions were used.
    """
    self.assertAdminBaseTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/soc/dashboard/_user_action.html')

  def testAdminDashboard(self):
    self.data.createHost()

    url = '/gsoc/admin/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertDashboardTemplatesUsed(response)
    self.assertUserActionsTemplatesUsed(response)

    context = self.adminDashboardContext()
    self.assertTrue('colorbox' in context)
    self.assertFalse(context['colorbox'])
    self.assertTrue('dashboards' in context)

    # dashboards template context
    for dashboard in context['dashboards']:
      dashboard_context = dashboard.context()
      self.assertTrue('title' in dashboard_context)
      self.assertTrue('name' in dashboard_context)
      self.assertTrue('subpages' in dashboard_context)
      subpages = dashboard_context['subpages']
      self.assertTrue(2 == len(subpages))

    self.assertTrue('page_name' in context)
    self.assertTrue('user_actions' in context)

    # context with colorbox passed in query string
    context = self.adminDashboardContext(colorbox=True)
    self.assertTrue('colorbox' in context)
    self.assertTrue(context['colorbox'])


class LookupProfileTest(GSoCDjangoTestCase):
  """Test lookup profile page
  """

  def setUp(self):
    self.init()

  def assertLookupProfile(self, response):
    """Asserts that all templates from the lookup profile page were used
    and all contexts were passed
    """
    self.assertTrue('base_layout' in response.context)
    self.assertTrue('cbox' in response.context)
    if response.context['cbox']:
      self.assertGSoCColorboxTemplatesUsed(response)
      self.assertEqual(response.context['base_layout'],
        'v2/modules/gsoc/base_colorbox.html')
    else:
      self.assertGSoCTemplatesUsed(response)
      self.assertEqual(response.context['base_layout'],
        'v2/modules/gsoc/base.html')

    self.assertTemplateUsed(response, 'v2/modules/gsoc/admin/lookup.html')

  def testLookupProfile(self):
    self.data.createHost()

    # rendered with default base layout
    url = '/gsoc/admin/lookup/' + self.gsoc.key().name()
    response = self.get(url)
    self.assertLookupProfile(response)

    # rendered inside cbox iframe
    url = '/gsoc/admin/lookup/' + self.gsoc.key().name() + '?cbox=true'
    response = self.get(url)
    self.assertLookupProfile(response)

    post_url = '/gsoc/admin/lookup/' + self.gsoc.key().name()
    postdata = {}

    # invalid post data submitted to lookup form
    response = self.post(post_url, postdata)
    self.assertResponseOK(response)
    self.assertTrue(response.context['error'])

    # valid post data submitted to lookup form
    self.data.createProfile()
    postdata.update({
        'email': self.data.profile.email
        })
    response = self.post(post_url, postdata)
    new_url = '/gsoc/profile/admin/%s/%s' % (
        self.gsoc.key().name(),self.data.profile.link_id)
    self.assertResponseRedirect(response, new_url)

    # inside cbox iframe and submit invalid data to lookup form
    post_url += '?cbox=true'
    response = self.post(post_url, {})
    self.assertResponseOK(response)
    self.assertTrue(response.context['error'])
    self.assertLookupProfile(response)

    # inside cbox iframe and submit valid data to lookup form
    response = self.post(post_url, postdata)
    new_url = '/gsoc/profile/admin/%s/%s?cbox=true' % (
        self.gsoc.key().name(),self.data.profile.link_id)
    self.assertResponseRedirect(response, new_url)


class AcceptedOrgsPageTest(GSoCDjangoTestCase):
  """Test for accepted orgs that show proposals or projects for each org
  """

  def setUp(self):
    self.init()

  def assertAcceptedOrgs(self, response):
    """Asserts that all the templates from the accepted orgs list were used
    and all contexts were passed.
    """
    self.assertTrue('base_layout' in response.context)
    self.assertTrue('cbox' in response.context)
    if response.context['cbox']:
      self.assertGSoCColorboxTemplatesUsed(response)
      self.assertEqual(response.context['base_layout'],
        'v2/modules/gsoc/base_colorbox.html')
    else:
      self.assertGSoCTemplatesUsed(response)
      self.assertEqual(response.context['base_layout'],
        'v2/modules/gsoc/base.html')

    self.assertTemplateUsed(response, 'v2/modules/gsoc/admin/list.html')
    self.assertTemplateUsed(response,
        'v2/modules/gsoc/admin/_accepted_orgs_list.html')

  def testListOrgs(self):
    self.data.createHost()

    bases = ['proposals', 'projects']
    for base in bases:
      # rendered with default base layout
      url = ('/gsoc/admin/%s/' % base) + self.gsoc.key().name()
      response = self.get(url)
      self.assertAcceptedOrgs(response)
      response = self.getListResponse(url, 0)
      self.assertIsJsonResponse(response)

      # rendered inside cbox iframe
      url += '?cbox=true'
      response = self.get(url)
      self.assertAcceptedOrgs(response)


class ProposalsPageTest(GSoCDjangoTestCase):
  """Test proposals list page for admin
  """

  def setUp(self):
    self.init()

  def assertProposalsPage(self, response):
    """Asserts that all the templates from the submitted proposals list
    were used and all contexts were passed.
    """
    self.assertTrue('base_layout' in response.context)
    self.assertTrue('cbox' in response.context)
    if response.context['cbox']:
      self.assertGSoCColorboxTemplatesUsed(response)
      self.assertEqual(response.context['base_layout'],
        'v2/modules/gsoc/base_colorbox.html')
    else:
      self.assertGSoCTemplatesUsed(response)
      self.assertEqual(response.context['base_layout'],
        'v2/modules/gsoc/base.html')

    self.assertTemplateUsed(response, 'v2/modules/gsoc/admin/list.html')
    self.assertTemplateUsed(response,
        'v2/modules/gsoc/admin/_proposals_list.html')

  def testListProposals(self):
    self.data.createHost()
    self.timeline.studentSignup()

    url = '/gsoc/admin/proposals/' + self.org.key().name()
    response = self.get(url)
    self.assertProposalsPage(response)

    response = self.getListResponse(url, 0)
    self.assertIsJsonResponse(response)
    data = response.context['data']['']
    self.assertEqual(0, len(data))

    # test list with student's proposal
    self.mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    self.mentor.createMentor(self.org)
    self.data.createStudentWithProposals(self.org, self.mentor.profile, 1)
    response = self.getListResponse(url, 0)
    self.assertIsJsonResponse(response)
    data = response.context['data']['']
    self.assertEqual(1, len(data))

    # rendered inside cbox iframe
    url += '?cbox=true'
    response = self.get(url)
    self.assertProposalsPage(response)


class ProjectsPageTest(GSoCDjangoTestCase):
  """Test projects list for admin
  """

  def setUp(self):
    self.init()

  def assertProjectsPage(self, response):
    """Asserts that all the templates from the accepted projects list were used
    and all contexts were passed.
    """
    self.assertTrue('base_layout' in response.context)
    self.assertTrue('cbox' in response.context)
    if response.context['cbox']:
      self.assertGSoCColorboxTemplatesUsed(response)
      self.assertEqual(response.context['base_layout'],
        'v2/modules/gsoc/base_colorbox.html')
    else:
      self.assertGSoCTemplatesUsed(response)
      self.assertEqual(response.context['base_layout'],
        'v2/modules/gsoc/base.html')

    self.assertTemplateUsed(response, 'v2/modules/gsoc/admin/list.html')
    self.assertTemplateUsed(response,
        'v2/modules/gsoc/admin/_projects_list.html')

  def testListProjects(self):
    self.data.createHost()
    self.timeline.studentsAnnounced()

    url = '/gsoc/admin/projects/' + self.org.key().name()
    response = self.get(url)
    self.assertProjectsPage(response)

    response = self.getListResponse(url, 0)
    self.assertIsJsonResponse(response)
    data = response.context['data']['']
    self.assertEqual(0, len(data))

    # test list with student's proposal
    self.mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    self.mentor.createMentor(self.org)
    self.data.createStudentWithProjects(self.org, self.mentor.profile, 1)
    response = self.getListResponse(url, 0)
    self.assertIsJsonResponse(response)
    data = response.context['data']['']
    self.assertEqual(1, len(data))

    # rendered inside cbox iframe
    url += '?cbox=true'
    response = self.get(url)
    self.assertProjectsPage(response)
