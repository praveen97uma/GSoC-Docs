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

"""Tests for GCI logic for profiles.
"""


import unittest

from soc.modules.gci.logic import profile as profile_logic
from soc.modules.gci.models.organization import GCIOrganization
from soc.modules.gci.models.profile import GCIProfile
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class ProfileTest(unittest.TestCase):
  """Tests the logic for GCI profiles.
  """
  
  def setUp(self):
    self.foo_org = seeder_logic.seed(GCIOrganization)
    self.bar_org = seeder_logic.seed(GCIOrganization)

  def testQueryAllMentorKeysForOrg(self):
    """Tests if a list of keys of all the mentors for an organization is
    returned.
    """
    #Since there are no mentors assigned to foo_org or bar_org, an empty list
    #should be returned.
    expected_keys = []
    actual_keys = profile_logic.queryAllMentorsKeysForOrg(self.foo_org)
    self.assertEqual(expected_keys, actual_keys) 

    actual_keys = profile_logic.queryAllMentorsKeysForOrg(self.bar_org)
    self.assertEqual(expected_keys,actual_keys)

    mentor_properties = {'mentor_for': [self.foo_org.key()], 'is_mentor': True}
    foo_mentors = seeder_logic.seedn(GCIProfile, 5, mentor_properties)

    org_admin_properties = {'org_admin_for': [self.foo_org.key()],
                            'mentor_for': [self.foo_org.key()],
                            'is_mentor': True, 'is_org_admin': True}
    foo_org_admin = seeder_logic.seed(GCIProfile, org_admin_properties)

    mentor_properties['mentor_for'] = [self.bar_org.key()]
    bar_mentors = seeder_logic.seedn(GCIProfile, 5, mentor_properties)

    org_admin_properties['org_admin_for'] = [self.bar_org.key()]
    org_admin_properties['mentor_for'] = [self.bar_org.key()]
    bar_org_admin = seeder_logic.seed(GCIProfile, org_admin_properties)

    expected = [mentor.key() for mentor in foo_mentors] + [foo_org_admin.key()]
    actual = profile_logic.queryAllMentorsKeysForOrg(self.foo_org)
    self.assertEqual(expected, actual)

    expected = [mentor.key() for mentor in bar_mentors] + [bar_org_admin.key()]

    actual = profile_logic.queryAllMentorsKeysForOrg(self.bar_org)
    self.assertEqual(expected, actual)
