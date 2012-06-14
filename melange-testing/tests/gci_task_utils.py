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


"""Utils for manipulating GCI task data.
"""


import datetime

from soc.modules.gci.models.task import DIFFICULTIES
from soc.modules.gci.models.task import GCITask
from soc.modules.gci.models.work_submission import GCIWorkSubmission

from soc.modules.seeder.logic.seeder import logic as seeder_logic


class GCITaskHelper(object):
  """Helper class to aid in manipulating GCI task data.
  """

  def __init__(self, program):
    """Initializes the GCITaskHelper.

    Args:
      program: a GCI program
    """
    self.program = program

  def seed(self, model, properties,
           auto_seed_optional_properties=False):
    return seeder_logic.seed(model, properties, recurse=False,
        auto_seed_optional_properties=auto_seed_optional_properties)

  def createTask(self, status, org, mentor, student=None, override={}):
    """Creates a GCI task with only one mentor.

    Args:
      status: the status of the task
      org: the org under which the task is created
      mentor: mentor for the task
      student: student who claimed the task
    """
    return self.createTaskWithMentors(status, org, [mentor], student, override)

  def createTaskWithMentors(self, status, org, mentors, student=None, override={}):
    """Creates a GCI task with mentors.

    Args:
      status: the status of the task
      org: the org under which the task is created
      mentors: mentors for the task
      student: student who claimed the task
    """
    properties = {'program': self.program, 'org': org, 'status': status,
        'difficulty': DIFFICULTIES[0],
        'task_type': self.program.task_types[0],
        'mentors': [mentor.key() for mentor in mentors], 'student': student,
        'user': student.user if student else None,
        'created_by': mentors[0], 'modified_by': mentors[0],
        'created_on': datetime.datetime.now() - datetime.timedelta(20),
        'modified_on': datetime.datetime.now() - datetime.timedelta(10)
    }
    properties.update(override)
    return self.seed(GCITask, properties)

  def createWorkSubmission(self, task, student, url='http://www.example.com/'):
    """Creates a GCIWorkSubmission.

    Args:
      task: The task to create a worksubmission for.
      student: The student whose work it is.
      url: The url to the work.
    """
    work = GCIWorkSubmission(
        parent=task, program=task.program, org=task.org, user=student.user,
        url_to_work=url)
    work.put()
    return work
