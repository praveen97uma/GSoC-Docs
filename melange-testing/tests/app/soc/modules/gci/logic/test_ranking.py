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

"""Tests for GCIStudentRanking methods.
"""


import unittest

from soc.modules.gci.logic import ranking as ranking_logic
from soc.modules.gci.models.student_ranking import GCIStudentRanking

from tests.gci_task_utils import GCITaskHelper
from tests.profile_utils import GCIProfileHelper
from tests.program_utils import GCIProgramHelper


class RankingTest(unittest.TestCase):
  """Tests the ranking methods for students in GCI.
  """

  def setUp(self):
    self.gci_program_helper = GCIProgramHelper()
    self.program = self.gci_program_helper.createProgram()
    self.task_helper = GCITaskHelper(self.program)
    self.student = GCIProfileHelper(self.program, False).createStudent()

  def testGetOrCreateForStudent(self):
    """Tests if an appropriate ranking object is created for a student.
    """
    #There is no GCIStudentRanking object for self.student in the datastore.
    #Hence, a new entity should be created and returned.
    q = GCIStudentRanking.all()
    q.filter('student', self.student)
    ranking = q.get()

    self.assertEqual(ranking, None)

    actual_ranking = ranking_logic.getOrCreateForStudent(self.student)
    q = GCIStudentRanking.all()
    q.filter('student', self.student)
    expected_ranking = q.get()
    self.assertEqual(expected_ranking.key(), actual_ranking.key())

    #GCIStudentRanking object already exists for a student.
    student = GCIProfileHelper(self.program, False).createOtherUser(
        'student@gmail.com').createStudent()
    ranking = GCIStudentRanking(program=student.scope, student=student)
    ranking.put()
    actual_ranking = ranking_logic.getOrCreateForStudent(student)

    self.assertEqual(ranking.key(), actual_ranking.key())
"""
  def testUpdateRankingWithTask(self):
    Tests if the ranking of a specified task is updated.

    org = self.gci_program_helper.createNewOrg()

    mentor = GCIProfileHelper(self.program, False).createOtherUser(
        'mentor@gmail.com').createMentor(org)

    task = self.task_helper.createTask('Closed', org, mentor, self.student)

    expected_value = task.taskDifficulty().value
    actual = ranking_logic.updateRankingWithTask(task)
    self.assertEqual(expected_value, actual.points)

    another_task = self.task_helper.createTask('Closed', org, 
                                               mentor, self.student)
    expected = expected_value + another_task.taskDifficulty().value
    actual = ranking_logic.updateRankingWithTask(another_task)
    self.assertEqual(expected, actual.points)

    #Test with an existing GCIStudentRanking object.
    another_student = GCIProfileHelper(self.program, False).createOtherUser(
        'student@gmail.com').createStudent()

    ranking = GCIStudentRanking(program=self.program, student=another_student)
    ranking.points = 5
    ranking.put()

    org = self.gci_program_helper.createNewOrg()
    mentor = GCIProfileHelper(self.program, False).createOtherUser(
        'men@g.com').createMentor(org)

    task = self.task_helper.createTask('Closed', org, mentor, another_student)

    expected_value = ranking.points + task.taskDifficulty().value
    actual = ranking_logic.updateRankingWithTask(task)
    self.assertEqual(expected_value, actual.points)

  def testCalculateRankingForStudent(self):
    Tests if the ranking of a student is correctly calculated.

    org = self.gci_program_helper.createNewOrg()
    mentor = GCIProfileHelper(self.program, False).createOtherUser(
        'mentot@gmail.com').createMentor(org)
    createTask = self.task_helper.createTask
    tasks = [
        createTask('Closed', org, mentor, self.student) for _ in range(5)
    ]

    expected_value = 0
    for task in tasks:
      expected_value+=task.taskDifficulty().value
    actual = ranking_logic.calculateRankingForStudent(self.student, tasks)
    self.assertEquals(expected_value, actual.points)

    #Test with an already existing GCIStudentRanking object.
    another_student = GCIProfileHelper(self.program, False).createOtherUser(
        'stud@c.com').createStudent()

    ranking = GCIStudentRanking(program=self.program, student=another_student)
    ranking.points = 5
    ranking.put()

    org = self.gci_program_helper.createNewOrg()
    mentor = GCIProfileHelper(self.program, False).createOtherUser(
        'praveen@gm.com').createMentor(org)
    tasks = [
        createTask('Closed', org, mentor, another_student) for _ in range(5)
    ]
    expected_value = 0
    for task in tasks:
      expected_value += task.taskDifficulty().value
    actual = ranking_logic.calculateRankingForStudent(another_student, tasks)
    self.assertEquals(expected_value, actual.points)
"""