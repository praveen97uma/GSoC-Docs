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


"""Utils for manipulating the timeline.
"""


from datetime import datetime
from datetime import timedelta


def past(delta=100):
  """Returns a date that is delta days past today.
  """
  return datetime.today() - timedelta(delta)


def future(delta=100):
  """Returns a date that is delta days future today.
  """
  return datetime.today() + timedelta(delta)


class TimelineHelper(object):
  """Base helper class to aid in setting the timeline.
  """

  def __init__(self, timeline, org_appl):
    self.timeline = timeline
    # org_appl instead of org_app so that it is the same length as timeline
    self.org_appl = org_appl

  def _empty(self):
    """Removes all timeline settings.

    Note: does not save changes.
    """
    self.timeline.program_start = None
    self.timeline.program_end = None
    self.org_appl.survey_start = None
    self.org_appl.survey_end = None
    self.timeline.accepted_organization_announced_deadline = None
    self.timeline.student_signup_start = None
    self.timeline.student_signup_end = None

  def offSeason(self):
    """Sets the current period to off season.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = past()
    self.org_appl.survey_start = past()
    self.org_appl.survey_end = past()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = past()
    self.timeline.student_signup_end = past()

  def kickoff(self):
    """Sets the current period to the program kickoff.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.org_appl.survey_start = future()
    self.org_appl.survey_end = future()
    self.timeline.accepted_organization_announced_deadline = future()
    self.timeline.student_signup_start = future()
    self.timeline.student_signup_end = future()

  def orgSignup(self):
    """Sets the current period to the organization signup phase.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.org_appl.survey_start = past()
    self.org_appl.survey_end = future()
    self.timeline.accepted_organization_announced_deadline = future()
    self.timeline.student_signup_start = future()
    self.timeline.student_signup_end = future()

  def orgsAnnounced(self):
    """Sets the current period to the organization signup phase.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.org_appl.survey_start = past()
    self.org_appl.survey_end = past()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = future()
    self.timeline.student_signup_end = future()

  def studentSignup(self):
    """Sets the current period to the student signup phase.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.org_appl.survey_start = past()
    self.org_appl.survey_end = past()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = past()
    self.timeline.student_signup_end = future()


class GSoCTimelineHelper(TimelineHelper):
  """Helper class to aid in setting the GSoC timeline.
  """

  def __init__(self, timeline, org_appl):
    super(GSoCTimelineHelper, self).__init__(timeline, org_appl)

  def _empty(self):
    """Removes all timeline settings.

    Note: does not save changes.
    """
    super(GSoCTimelineHelper, self)._empty()
    self.timeline.accepted_students_announced_deadline = None

  def offSeason(self):
    """Sets the current period to off season.
    """
    super(GSoCTimelineHelper, self).offSeason()
    self.timeline.accepted_students_announced_deadline = past()
    self.timeline.put()
    self.org_appl.put()

  def kickoff(self):
    """Sets the current period to the program kickoff.
    """
    super(GSoCTimelineHelper, self).kickoff()
    self.timeline.accepted_students_announced_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def orgSignup(self):
    """Sets the current period to the organization signup phase.
    """
    super(GSoCTimelineHelper, self).orgSignup()
    self.timeline.accepted_students_announced_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def orgsAnnounced(self):
    """Sets the current period to the organization signup phase.
    """
    super(GSoCTimelineHelper, self).orgsAnnounced()
    self.timeline.accepted_students_announced_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def studentSignup(self):
    """Sets the current period to the student signup phase.
    """
    super(GSoCTimelineHelper, self).studentSignup()
    self.timeline.accepted_students_announced_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def postStudentSignup(self):
    """Sets the current period to after the signup phase.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.org_appl.survey_start = past()
    self.org_appl.survey_end = past()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = past()
    self.timeline.student_signup_end = past()
    self.timeline.accepted_students_announced_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def studentsAnnounced(self):
    """Sets the current period to be future accepted students announced phase.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.org_appl.survey_start = past()
    self.org_appl.survey_end = past()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = past()
    self.timeline.student_signup_end = past()
    self.timeline.accepted_students_announced_deadline = past()
    self.timeline.put()
    self.org_appl.put()


class GCITimelineHelper(TimelineHelper):
  """Helper class to aid in setting the GCI timeline.
  """

  def __init__(self, timeline, org_appl):
    super(GCITimelineHelper, self).__init__(timeline, org_appl)

  def _empty(self):
    """Removes all timeline settings.

    Note: does not save changes.
    """
    super(GCITimelineHelper, self)._empty()
    self.timeline.tasks_publicly_visible = None
    self.timeline.task_claim_deadline = None
    self.timeline.stop_all_work_deadline = None

  def offSeason(self):
    """Sets the current period to off season.
    """
    super(GCITimelineHelper, self).offSeason()
    self.timeline.tasks_publicly_visible = past()
    self.timeline.task_claim_deadline = past()
    self.timeline.stop_all_work_deadline = past()
    self.timeline.put()
    self.org_appl.put()

  def kickoff(self):
    """Sets the current period to the program kickoff.
    """
    super(GCITimelineHelper, self).kickoff()
    self.timeline.tasks_publicly_visible = future()
    self.timeline.task_claim_deadline = future()
    self.timeline.stop_all_work_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def orgSignup(self):
    """Sets the current period to the organization signup phase.
    """
    super(GCITimelineHelper, self).orgSignup()
    self.timeline.tasks_publicly_visible = future()
    self.timeline.task_claim_deadline = future()
    self.timeline.stop_all_work_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def orgsAnnounced(self):
    """Sets the current period to the organization signup phase.
    """
    super(GCITimelineHelper, self).orgsAnnounced()
    self.timeline.tasks_publicly_visible = future()
    self.timeline.task_claim_deadline = future()
    self.timeline.stop_all_work_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def tasksPubliclyVisible(self):
    """Sets the current period to the tasks publicly visible phase.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.org_appl.survey_start = past()
    self.org_appl.survey_end = past()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = future()
    self.timeline.student_signup_end = future()
    self.timeline.tasks_publicly_visible = past()
    self.timeline.task_claim_deadline = future()
    self.timeline.stop_all_work_deadline = future()
    self.timeline.work_review_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def studentSignup(self):
    """Sets the current period to the student signup phase.
    """
    super(GCITimelineHelper, self).studentSignup()
    self.timeline.tasks_publicly_visible = past()
    self.timeline.task_claim_deadline = future()
    self.timeline.stop_all_work_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def taskClaimEnded(self):
    """Sets the current period to the task claim ended phase.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.org_appl.survey_start = past()
    self.org_appl.survey_end = past()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = past()
    self.timeline.student_signup_end = future()
    self.timeline.tasks_publicly_visible = past()
    self.timeline.task_claim_deadline = past()
    self.timeline.stop_all_work_deadline = future()
    self.timeline.put()
    self.org_appl.put()

  def pencilDown(self):
    """Sets the current period to the phase when all work should stop.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.org_appl.survey_start = past()
    self.org_appl.survey_end = past()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = past()
    self.timeline.student_signup_end = future()
    self.timeline.tasks_publicly_visible = past()
    self.timeline.task_claim_deadline = past()
    self.timeline.stop_all_work_deadline = past()
    self.timeline.put()
    self.org_appl.put()
