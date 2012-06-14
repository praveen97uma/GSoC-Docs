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


"""Tests for soc.logic.helper.timeline.
"""


import unittest

from datetime import datetime
from datetime import timedelta

from soc.logic.helper import timeline
from soc.models import timeline as timeline_model
from soc.models.sponsor import Sponsor

from soc.modules.seeder.logic.seeder import logic as seeder_logic


class TimelineTest(unittest.TestCase):
  """Tests for timeline helper functions.
  """

  def setUp(self):
    self.timeline = seeder_logic.seed(timeline_model.Timeline)

  def testIsBeforePeriod(self):
    """Tests if a correct bool is returned if the current DateTime is before
    a given period_start.
    """
    #program is yet to start.
    self.timeline.program_start = datetime.utcnow() + timedelta(10)
    self.assertTrue(timeline.isBeforePeriod(self.timeline, 'program'))

    #program has already started.
    self.timeline.program_start = datetime.utcnow() - timedelta(10)
    self.assertFalse(timeline.isBeforePeriod(self.timeline, 'program'))

    #student signup period is yet to start.
    self.timeline.student_signup_start = datetime.utcnow() + timedelta(10)
    self.assertTrue(timeline.isBeforePeriod(self.timeline, 'student_signup'))

    #student sign up period has already started.
    self.timeline.student_signup_start = datetime.utcnow() - timedelta(10)
    self.assertFalse(timeline.isBeforePeriod(self.timeline, 'student_signup'))

    #event not in the timeline.
    self.assertFalse(timeline.isBeforePeriod(self.timeline, 'other_event'))

  def testIsBeforeEvent(self):
    """Tests if a correct bool is returned if current DateTime 
    is before a given event.
    """
    #program has not started.
    self.timeline.program_start = datetime.utcnow() + timedelta(20)
    self.assertTrue(timeline.isBeforeEvent(self.timeline, 'program_start'))

    #program has already started.
    self.timeline.program_start = datetime.utcnow() - timedelta(20)
    self.assertFalse(timeline.isBeforeEvent(self.timeline, 'program_start'))

    #program has not ended.
    self.timeline.program_end = datetime.utcnow() + timedelta(20)
    self.assertTrue(timeline.isBeforeEvent(self.timeline, 'program_end'))

    #program has ended.
    self.timeline.program_end = datetime.utcnow() - timedelta(20)
    self.assertFalse(timeline.isBeforeEvent(self.timeline, 'program_end'))

    #the deadline to announce accepted organizations has not passed.
    self.timeline.accepted_organization_announced_deadline = (datetime.utcnow()
                                                              + timedelta(20))
    self.assertTrue(timeline.isBeforeEvent(
        self.timeline, "accepted_organization_announced_deadline"))

    #the deadline to announce accepted organizations has been passed.
    self.timeline.accepted_organization_announced_deadline = (datetime.utcnow()
                                                             - timedelta(20))
    self.assertFalse(timeline.isBeforeEvent(
        self.timeline, "accepted_organization_announced_deadline"))

    #student sign up period has not started.
    self.timeline.student_signup_start = datetime.utcnow() + timedelta(20)
    self.assertTrue(timeline.isBeforeEvent(self.timeline,
                                           'student_signup_start'))

    #student sign up period has already started.
    self.timeline.student_signup_start = datetime.utcnow() - timedelta(20)
    self.assertFalse(timeline.isBeforeEvent(self.timeline,
                                            'student_signup_start'))

    #student sign up period has not ended.
    self.timeline.student_signup_end = datetime.utcnow() + timedelta(20)
    self.assertTrue(timeline.isBeforeEvent(self.timeline,
                                           'student_signup_end'))

    #student sign up period has already ended.
    self.timeline.student_signup_end = datetime.utcnow() - timedelta(20)
    self.assertFalse(timeline.isBeforeEvent(self.timeline,
                                            'student_signup_end'))
    #event not in the timeline.
    self.assertFalse(timeline.isBeforeEvent(self.timeline, 'other_event'))

  def testIsActivePeriod(self):
    """Tests if a correct boolean is returned if the current DateTime is 
    between period_start and period_end.
    """
    #program is going on.
    self.timeline.program_start = datetime.utcnow() - timedelta(10)
    self.timeline.program_end = datetime.utcnow() + timedelta(10)
    self.assertTrue(timeline.isActivePeriod(self.timeline, 'program'))

    #program will start.
    self.timeline.program_start = datetime.utcnow() + timedelta(10)
    self.timeline.program_end = datetime.utcnow() + timedelta(20)
    self.assertFalse(timeline.isActivePeriod(self.timeline, 'program'))

    #program has ended.
    self.timeline.program_start = datetime.utcnow() - timedelta(20)
    self.timeline.program_end = datetime.utcnow() - timedelta(10)
    self.assertFalse(timeline.isActivePeriod(self.timeline, 'program'))

    #student sign up period will start
    self.timeline.student_signup_start = datetime.utcnow() + timedelta(10)
    self.timeline.student_signup_end = datetime.utcnow() + timedelta(30)
    self.assertFalse(timeline.isActivePeriod(self.timeline, 'student_signup'))

    #student sign up period has not ended.
    self.timeline.student_signup_start = datetime.utcnow() - timedelta(10)
    self.timeline.student_signup_end = datetime.utcnow() + timedelta(20)
    self.assertTrue(timeline.isActivePeriod(self.timeline,
                                            'student_signup'))

    #student sign up period has already ended.
    self.timeline.student_signup_start = datetime.utcnow() - timedelta(30)
    self.timeline.student_signup_end = datetime.utcnow() - timedelta(20)
    self.assertFalse(timeline.isActivePeriod(self.timeline,
                                            'student_signup'))
    #event not in the timeline.
    self.assertFalse(timeline.isActivePeriod(self.timeline, 'other_event'))

  def testActivePeriod(self):
    """Tests if the start and end of a specified period is returned.
    """
    start = datetime(2011, 4, 3)
    end = datetime(2020, 4, 3)
    self.timeline.program_start = start
    self.timeline.program_end = end
    actual = timeline.activePeriod(self.timeline, 'program')
    expected = (start, end)
    self.assertEqual(actual, expected)

    start = datetime(2011, 7, 4)
    end = datetime(2021, 7, 5)
    self.timeline.student_signup_start = start
    self.timeline.student_signup_end = end
    actual = timeline.activePeriod(self.timeline, 'student_sign_up')
    expected = (start, end)
    self.assertEqual(actual, expected)

    #event not in the timeline.
    expected = (None, None)
    actual = timeline.activePeriod(self.timeline, 'some_other_event')
    self.assertEqual(actual, expected)

  def testIsAfterPeriod(self):
    """Tests if True is returned if current DateTime is after period_end.
    """
    #program has ended.
    self.timeline.program_end = datetime.utcnow() - timedelta(10)
    self.assertTrue(timeline.isAfterPeriod(self.timeline, 'program'))

    #program has not ended.
    self.timeline.program_end = datetime.utcnow() + timedelta(10)
    self.assertFalse(timeline.isAfterPeriod(self.timeline, 'program'))

    #student sign up has ended.
    self.timeline.student_signup_end = datetime.utcnow() - timedelta(10)
    self.assertTrue(timeline.isAfterPeriod(self.timeline, 'student_signup'))

    #student sign up has not ended.
    self.timeline.student_signup_end = datetime.utcnow() + timedelta(10)
    self.assertFalse(timeline.isAfterPeriod(self.timeline, 'student_signup'))

    #event not in the timeline.
    self.assertFalse(timeline.isAfterPeriod(self.timeline, 'some_other_event'))

  def testIsAfterEvent(self):
    """Tests if True is returned if current DateTime is after the given event.
    """
    #program has started.
    self.timeline.program_start = datetime.utcnow() - timedelta(10)
    self.assertTrue(timeline.isAfterEvent(self.timeline, 'program_start'))

    #program is yet to start.
    self.timeline.program_start = datetime.utcnow() + timedelta(10)
    self.assertFalse(timeline.isAfterEvent(self.timeline, 'program_start'))

    #program has ended.
    self.timeline.program_start = datetime.utcnow() - timedelta(30)
    self.timeline.program_end = datetime.utcnow() - timedelta(20)
    self.assertTrue(timeline.isAfterEvent(self.timeline, 'program_end'))

    #the deadline to announce accepted organizations has not passed.
    self.timeline.accepted_organization_announced_deadline = (datetime.utcnow()
                                                              + timedelta(20))
    self.assertFalse(timeline.isAfterEvent(
        self.timeline, "accepted_organization_announced_deadline"))

    #the deadline to announce accepted organizations has been passed.
    self.timeline.accepted_organization_announced_deadline = (datetime.utcnow()
                                                             - timedelta(20))
    self.assertTrue(timeline.isAfterEvent(
        self.timeline, "accepted_organization_announced_deadline"))

    #student sign up period has not started.
    self.timeline.student_signup_start = datetime.utcnow() + timedelta(20)
    self.assertFalse(timeline.isAfterEvent(self.timeline,
                                           'student_signup_start'))

    #student sign up period has already started.
    self.timeline.student_signup_start = datetime.utcnow() - timedelta(20)
    self.assertTrue(timeline.isAfterEvent(self.timeline,
                                            'student_signup_start'))

    #student sign up period has not ended.
    self.timeline.student_signup_end = datetime.utcnow() + timedelta(20)
    self.assertFalse(timeline.isAfterEvent(self.timeline,
                                           'student_signup_end'))

    #student sign up period has already ended.
    self.timeline.student_signup_end = datetime.utcnow() - timedelta(20)
    self.assertTrue(timeline.isAfterEvent(self.timeline,
                                            'student_signup_end'))

    #event not in the Timeline.
    self.assertFalse(timeline.isAfterEvent(self.timeline, 'some_other_event'))

  def testGetDateTimeByname(self):
    """Tests that a DateTime property with a given name is returned.
    """
    self.timeline.program_start = datetime(2011, 7, 1)
    #name is available in the timeline.
    name = 'program_start'
    entity = self.timeline
    expected = self.timeline.program_start
    actual = timeline.getDateTimeByName(entity, name)
    self.assertEqual(actual, expected)

    self.timeline.program_end = datetime(2012, 7, 4)
    name = 'program_end'
    entity = self.timeline
    expected = self.timeline.program_end
    actual = timeline.getDateTimeByName(entity, name)
    self.assertEqual(actual, expected)

    self.timeline.student_signup_start = datetime(2011, 9, 5)
    name = 'student_signup_start'
    entity = self.timeline
    expected = self.timeline.student_signup_start
    actual = timeline.getDateTimeByName(entity, name)
    self.assertEqual(actual, expected)

    self.timeline.student_signup_end = datetime(2011, 12, 4)
    name = 'student_signup_end'
    entity = self.timeline
    expected = self.timeline.student_signup_end
    actual = timeline.getDateTimeByName(entity, name)
    self.assertEqual(actual, expected)

    self.timeline.accepted_organization_announced_deadline = datetime(2011, 5, 4)
    name = 'accepted_organizations_announced_deadline'
    entity = self.timeline
    expected = self.timeline.accepted_organization_announced_deadline
    actual = timeline.getDateTimeByName(entity, name)
    self.assertEqual(actual, expected)

    #name is not available in the timeline.
    name = 'some_name'
    entity = self.timeline
    expected = None
    actual = timeline.getDateTimeByName(entity, name)
    self.assertEqual(expected, actual)

