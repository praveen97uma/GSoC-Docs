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


"""Tests for the root url.
"""


from tests.test_utils import GSoCDjangoTestCase


class RootUrlViewTest(GSoCDjangoTestCase):
  """Tests program homepage views.
  """

  def setUp(self):
    self.init()

  def testRootUrl(self):
    """Tests that the root url redirects to the gsoc homepage.
    """
    url = '/'
    response = self.get(url)
    homepage = '/gsoc/homepage/' + self.gsoc.key().name()
    self.assertResponseRedirect(response, homepage)
