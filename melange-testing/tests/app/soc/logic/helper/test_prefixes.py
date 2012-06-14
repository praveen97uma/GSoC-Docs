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

"""Tests for soc.logic.helper.prefixes.
"""


import unittest

from google.appengine.api import users

from soc.logic.helper import prefixes
from soc.models.organization import Organization
from soc.models.program import Program
from soc.models.site import Site
from soc.models.user import User

from soc.modules.gci.models.organization import GCIOrganization
from soc.modules.gci.models.program import GCIProgram
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.timeline import GSoCTimeline
from soc.modules.seeder.logic.seeder import logic as seeder_logic

class TestPrefixes(unittest.TestCase):
  """Tests for prefix helper functions for models with document prefixes.
  """

  def setUp(self):

    self.user = seeder_logic.seed(User)

    self.program_timeline = seeder_logic.seed(GSoCTimeline)

    program_properties = {'timeline': self.program_timeline, 'scope': self.user}
    self.program = seeder_logic.seed(Program, program_properties)

    self.gsoc_program = seeder_logic.seed(GSoCProgram, program_properties)

    self.gci_program = seeder_logic.seed(GCIProgram, program_properties)

    self.site = seeder_logic.seed(Site,)

    self.organization = seeder_logic.seed(Organization)

    self.gsoc_organization = seeder_logic.seed(GSoCOrganization)

    self.gci_organization = seeder_logic.seed(GCIOrganization)

    self.user_key_name = self.user.key().name()
    self.program_key_name = self.program.key().name()
    self.gsoc_program_key_name = self.gsoc_program.key().name()
    self.gci_program_key_name = self.gci_program.key().name()
    self.site_key_name = self.site.key().name()
    self.org_key_name = self.organization.key().name()
    self.gsoc_org_key_name = self.gsoc_organization.key().name()
    self.gci_org_key_name = self.gci_organization.key().name()

  def testGetOrSetScope(self):
    """Not tested because it is used in soc.logic.models.survey and 
    soc.logic.models.document and soc.logic.models will be removed.
    """
    pass

  def testGetScopeForPrefix(self):
    """Tests if the scope for a given prefix and key_name is returned.
    """
    prefix = 'user'
    key_name = self.user_key_name
    scope_returned = prefixes.getScopeForPrefix(prefix, key_name)
    self.assertEqual(scope_returned.key().name(), key_name)
    self.assertEqual(type(scope_returned), type(self.user))

    prefix = 'site'
    key_name = self.site_key_name
    scope_returned = prefixes.getScopeForPrefix(prefix, key_name)
    self.assertEqual(scope_returned.key().name(), key_name)
    self.assertEqual(type(scope_returned), type(self.site))

    prefix = 'org'
    key_name = self.org_key_name
    scope_returned = prefixes.getScopeForPrefix(prefix, key_name)
    self.assertEqual(scope_returned.key().name(), key_name)
    self.assertEqual(type(scope_returned), type(self.organization))

    prefix = 'gsoc_org'
    key_name = self.gsoc_org_key_name
    scope_returned = prefixes.getScopeForPrefix(prefix, key_name)
    self.assertEqual(scope_returned.key().name(), key_name)
    self.assertEqual(type(scope_returned), type(self.gsoc_organization))

    prefix = 'gci_org'
    key_name = self.gci_org_key_name
    scope_returned = prefixes.getScopeForPrefix(prefix, key_name)
    self.assertEqual(scope_returned.key().name(), key_name)
    self.assertEqual(type(scope_returned), type(self.gci_organization))

    prefix = 'program'
    key_name = self.program_key_name
    scope_returned = prefixes.getScopeForPrefix(prefix, key_name)
    self.assertEqual(scope_returned.key().name(), key_name)
    self.assertEqual(type(scope_returned), type(self.program))

    prefix = 'gsoc_program'
    key_name = self.gsoc_program_key_name
    scope_returned = prefixes.getScopeForPrefix(prefix, key_name)
    self.assertEqual(scope_returned.key().name(), key_name)
    self.assertEqual(type(scope_returned), type(self.gsoc_program))

    prefix = 'gci_program'
    key_name = self.gci_program_key_name
    scope_returned = prefixes.getScopeForPrefix(prefix, key_name)
    self.assertEqual(scope_returned.key().name(), key_name)
    self.assertEqual(type(scope_returned), type(self.gci_program))

    #When prefix is invalid.
    prefix = 'invalid_prefix'
    key_name = 'some_key_name'
    self.assertRaises(
        AttributeError, prefixes.getScopeForPrefix, prefix, key_name)

