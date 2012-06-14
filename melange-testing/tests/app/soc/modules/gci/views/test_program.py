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


"""Tests for program related views.
"""


from tests.test_utils import GCIDjangoTestCase


class EditProgramTest(GCIDjangoTestCase):
  """Tests program edit page.
  """

  def setUp(self):
    self.init()

  def assertProgramTemplatesUsed(self, response):
    """Asserts that all the templates from the program were used.
    """
    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/program/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gci/_form.html')

  def testEditProgramHostOnly(self):
    url = '/gci/program/edit/' + self.gci.key().name()
    response = self.get(url)
    self.assertErrorTemplatesUsed(response)

  def testEditProgramAsDeveloper(self):
    self.data.createDeveloper()
    url = '/gci/program/edit/' + self.gci.key().name()
    response = self.get(url)
    self.assertProgramTemplatesUsed(response)

  def testEditProgram(self):
    from soc.models.document import Document
    self.data.createHost()
    url = '/gci/program/edit/' + self.gci.key().name()
    response = self.get(url)
    self.assertProgramTemplatesUsed(response)

    response = self.getJsonResponse(url)
    self.assertIsJsonResponse(response)
    self.assertEqual(1, len(response.context['data']))
