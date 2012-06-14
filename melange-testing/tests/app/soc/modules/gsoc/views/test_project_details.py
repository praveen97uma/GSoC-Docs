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

"""Tests for project_detail views.
"""


from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import GSoCDjangoTestCase

from soc.modules.gsoc.models.project import GSoCProject


class ProjectDetailsTest(GSoCDjangoTestCase):
  """Tests project details page.
  """

  def setUp(self):
    super(ProjectDetailsTest, self).setUp()
    self.init()

  def assertProjectDetailsTemplateUsed(self, response):
    """Asserts that all the project details were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(
        response, 'v2/modules/gsoc/project_details/base.html')

  def createProject(self, override_properties={}):
    properties = {
        'is_featured': False, 'mentors': [],
        'status': 'accepted', 'program': self.gsoc, 'org': self.org,

    }
    properties.update(override_properties)
    return self.seed(GSoCProject, properties)

  def testProjectDetails(self):
    self.data.createStudent()
    self.timeline.studentsAnnounced()

    mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor.createOtherUser('mentor@example.com')
    mentor_entity = mentor.createMentor(self.org)

    project = self.createProject({'parent': self.data.profile,
                                 'mentor': mentor_entity})

    suffix = "%s/%s/%d" % (
        self.gsoc.key().name(),
        self.data.user.key().name(),
        project.key().id())

    # test project details GET
    url = '/gsoc/project/' + suffix
    response = self.get(url)
    self.assertProjectDetailsTemplateUsed(response)

  def testFeaturedProjectButton(self):
    self.timeline.studentsAnnounced()

    student = GSoCProfileHelper(self.gsoc, self.dev_test)
    student.createOtherUser('student@example.com')
    student.createStudent()

    self.data.createOrgAdmin(self.org)

    mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor.createOtherUser('mentor@example.com')
    mentor_entity = mentor.createMentor(self.org)

    project = self.createProject({'parent': self.data.profile,
                                 'mentor': mentor_entity})

    suffix = "%s/%s/%d" % (
        self.gsoc.key().name(),
        self.data.user.key().name(),
        project.key().id())

    url = '/gsoc/project/featured/' + suffix
    postdata = {'value': 'unchecked'}
    response = self.post(url, postdata)

    self.assertResponseOK(response)

    project = GSoCProject.all().get()
    self.assertEqual(project.is_featured, True)
