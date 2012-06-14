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

"""Tests for GCI logic for organizations.
"""


import unittest

from google.appengine.api import memcache

from soc.modules.gci.logic import organization as organization_logic
from soc.modules.gci.models.task import GCITask

from tests.gci_task_utils import GCITaskHelper
from tests.profile_utils import GCIProfileHelper
from tests.program_utils import GCIProgramHelper

class OrganizationTest(unittest.TestCase):
  """Tests the logic for GCIOrganization.
  """
  
  def setUp(self):
    self.gci_program_helper = GCIProgramHelper()
    self.program = self.gci_program_helper.createProgram()
    self.task_helper = GCITaskHelper(self.program)
  
  def testGetRemainingTaskQuota(self):
    """Tests if the remaining task quota that can be published by a given 
    organization is correctly returned.
    """
    gci_program_helper = GCIProgramHelper()
    org = gci_program_helper.createOrg()
    org.task_quota_limit = 5
    org.put()
    
    mentor = GCIProfileHelper(self.program, False).createOtherUser(
        'mentor@gmail.com').createMentor(org)
    
    student = GCIProfileHelper(self.program, False).createOtherUser(
        'student@gmail.com').createStudent()
    #valid tasks.
    for _ in xrange(3):
      self.task_helper.createTask('Closed', org, mentor, student)
    #invalid tasks.
    self.task_helper.createTask('Unpublished', org, mentor, student)
    expected_quota = org.task_quota_limit - 3
    actual_quota = organization_logic.getRemainingTaskQuota(org)

    self.assertEqual(expected_quota, actual_quota)

  def testParticipating(self):
    """Tests if a list of all the organizations participating in a given gci
    program is returned.
    """
    expected = []
    actual = organization_logic.participating(self.program)
    self.assertEqual(expected, actual)
    org1 = self.gci_program_helper.createOrg()
    org2 = self.gci_program_helper.createNewOrg()
    #We need to clear the cache with the key given below as the first call to
    #the function being tested sets an empty cache with the same key.
    key = 'participating_orgs_for' + self.program.key().name()
    memcache.delete(key)
    expected = set([org1.key(), org2.key()])
    actual = organization_logic.participating(self.gci_program_helper.program)
    actual = set([org.key() for org in actual])
    self.assertEqual(expected, set(actual))
