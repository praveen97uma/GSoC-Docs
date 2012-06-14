#!/usr/bin/env python2.5
#
# Copyright 2012 the Melange authors.
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


"""Tests for the maintenance mode.
"""


from tests.test_utils import GSoCDjangoTestCase


class RootMaintenanceModeTest(GSoCDjangoTestCase):
  """Tests maintenance mode.
  """

  def setUp(self):
    self.init()

  def testRootUrl(self):
    """Tests whether the root url is accessible when the site is
    in maintenance mode.
    """
    url = '/'

    # the page should be accessible
    response = self.get(url)
    homepage = '/gsoc/homepage/' + self.gsoc.key().name()
    self.assertResponseRedirect(response, homepage)

    # the page should be inaccessible
    self.site.maintenance_mode = True
    self.site.put()
    response = self.get(url)
    self.assertResponseCode(response, 503)

    self.data.createDeveloper()
    # the page should be accessible
    response = self.get(url)
    self.assertResponseRedirect(response, homepage)

  def testHomepageUrl(self):
    """Tests whether the program homepage site is accessible when the site
    is in maintenance mode.
    """
    url = '/gsoc/homepage/' + self.gsoc.key().name()
    
    # the page should be accessible
    response = self.get(url)
    self.assertResponseOK(response)

    # the page should be inaccessible
    self.site.maintenance_mode = True
    self.site.put()
    response = self.get(url)
    self.assertResponseCode(response, 503)

    self.data.createDeveloper()
    # the page should be accessible
    response = self.get(url)
    self.assertResponseOK(response)
