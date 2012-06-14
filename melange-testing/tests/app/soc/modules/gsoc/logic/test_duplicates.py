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

"""Tests for soc.modules.gsoc.logic.duplicates.
"""


import unittest

from soc.modules.gsoc.logic import duplicates as duplicate_logic
from soc.modules.gsoc.models.proposal_duplicates import GSoCProposalDuplicate
from soc.modules.gsoc.models.proposal_duplicates_status import \
    GSoCProposalDuplicatesStatus
from soc.modules.gsoc.models.program import GSoCProgram

from soc.modules.seeder.logic.seeder import logic as seeder_logic

from tests.profile_utils import GSoCProfileHelper


class DuplicatesTest(unittest.TestCase):
  """Tests duplicate detection functions in GSoC.
  """

  def createGSoCProposalDuplicate(self, student, program):
    """Creates and returns a seeded GSoCPropoposalDuplicate entity for
    a given student in a given program.
    """
    properties = {'program': program, 'student': student, 'is_duplicate': False}
    proposal_duplicate = seeder_logic.seed(GSoCProposalDuplicate, properties)
    return proposal_duplicate

  def createStudent(self, email, program):
    profile_helper = GSoCProfileHelper(program, dev_test=False)
    profile_helper.createOtherUser(email)
    student = profile_helper.createStudent()
    return student

  def setUp(self):
    """Setup required to test the functions.
    
    Two different program entities are created with their own set of students
    assigned to them. Some of the students in each program have duplicate
    proposals and some not.
    """
    self.program1 = seeder_logic.seed(GSoCProgram)

    #Create GSoCStudents in program1
    self.gsoc_students = []
    for i in xrange(5):
      email = 'test%s@example.com' % str(i)
      student = self.createStudent(email, self.program1)
      self.gsoc_students.append(student)

    #Create a GSoCProposalDuplicate entity for all the students 
    #in self.gsoc_students for program1.
    self.proposal_duplicates = []
    for student in self.gsoc_students:
      proposal_duplicate = self.createGSoCProposalDuplicate(student,
                                                            self.program1)
      self.proposal_duplicates.append(proposal_duplicate)

    #Create other program entity.
    self.program2 = seeder_logic.seed(GSoCProgram)

    #Create students in program2.
    self.other_gsoc_students = []
    for i in xrange(5):
      email = 'othertest%s@example.com' % str(i)
      student = self.createStudent(email, self.program2)
      self.other_gsoc_students.append(student)

    #Create a GSoCProposalDuplicate entity for all the students 
    #in self.other_gsoc_students for program2.
    self.other_proposal_duplicates = []
    for student in self.other_gsoc_students:
      proposal_duplicate = self.createGSoCProposalDuplicate(student,
                                                            self.program2)
      self.other_proposal_duplicates.append(proposal_duplicate)

    #Create a GSocProposalDuplicateStatusEntity for other_program
    properties = {'program': self.program2}
    self.gpds = seeder_logic.seed(GSoCProposalDuplicatesStatus, properties)


  def testGetOrCreateStatusForProgram(self):
    """Tests if a ProposalDuplicateStatus entity for a program is created or set.
    """
    #program has no ProposalDuplicateStatus entity. Check if the entity
    #is created for the program.
    program_entity = self.program1
    actual_pds = duplicate_logic.getOrCreateStatusForProgram(program_entity)
    self.assertEqual(actual_pds.program, program_entity)

    #program has a ProposalDuplicateStatus Entity.
    program_entity = self.program2
    expected_pds = self.gpds
    actual_pds = duplicate_logic.getOrCreateStatusForProgram(program_entity)
    self.assertEqual(actual_pds.key(), expected_pds.key())

  def testDeleteAllForProgram(self):
    """Tests if all proposal duplicates for a program are deleted.
    """
    #Before deleting.
    q = GSoCProposalDuplicate.all()
    q.filter('program', self.program1)
    q_result = q.fetch(limit=10)
    actual = [entity.key() for entity in q_result]
    expected = [entity.key() for entity in self.proposal_duplicates]
    self.assertEqual(actual, expected)

    #Delete duplicate proposals for program.
    duplicate_logic.deleteAllForProgram(self.program1)
    q = GSoCProposalDuplicate.all()
    q.filter('program', self.program1)
    actual = q.fetch(limit=10)
    expected = []
    self.assertEqual(actual, expected)

    #Test that duplicate proposals for other program were not deleted.
    expected = [entity.key() for entity in self.other_proposal_duplicates]
    q = GSoCProposalDuplicate.all()
    q.filter('program', self.program2)
    q_result = q.fetch(limit=10)
    actual = [entity.key() for entity in q_result]
    self.assertEqual(actual, expected)

  def testDeleteAllForProgramNonDupesOnlyIsTrue(self):
    """Tests if only those proposals are deleted which have is_duplicate set
    to false.
    """
    #is_duplicate is set to False by default for all the GSoCProposalDuplicate
    #entities. So, test if all the entities in program1 are deleted.
    duplicate_logic.deleteAllForProgram(self.program1, non_dupes_only=True)
    q = GSoCProposalDuplicate.all()
    q.filter('program', self.program1)
    q.filter('is_duplicate', False)
    q_result = q.fetch(limit=10)
    expected = []
    actual = [entity.key() for entity in q_result]
    self.assertEqual(actual, expected)

    #set is_duplicate = True for each of the first 3 students in
    #self.other_gsoc_students and test if these are not deleted for program2.
    for i in xrange(3):
      self.other_proposal_duplicates[i].is_duplicate = True
      self.other_proposal_duplicates[i].put()
    duplicate_logic.deleteAllForProgram(self.program2, non_dupes_only=True)
    q = GSoCProposalDuplicate.all()
    q.filter('program', self.program2)
    q.filter('is_duplicate', False)
    q_result = q.fetch(limit=10)
    expected = []
    actual = [entity.key() for entity in q_result]
    self.assertEqual(actual, expected)
    #check if entities with is_duplicate=True are not deleted
    q = GSoCProposalDuplicate.all()
    q.filter('program', self.program2)
    q.filter('is_duplicate', True)
    q_result = q.fetch(limit=10)
    expected = [entity.key() for entity in self.other_proposal_duplicates[:3]]
    actual = [entity.key() for entity in q_result]
    self.assertEqual(actual, expected)

