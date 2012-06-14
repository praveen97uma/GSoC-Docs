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


"""Tests for GCITask create/edit view.
"""


import datetime

from soc.modules.gci.logic.helper.notifications import (
    DEF_NEW_TASK_COMMENT_SUBJECT)
from soc.modules.gci.models.task import GCITask
from soc.modules.gci.models.profile import GCIProfile

from tests.gci_task_utils import GCITaskHelper
from tests.profile_utils import GCIProfileHelper
from tests.test_utils import GCIDjangoTestCase


class TaskCreateViewTest(GCIDjangoTestCase):
  """Tests GCITask create/edit view.
  """

  def setUp(self):
    """Creates a published task for self.org.
    """
    super(TaskCreateViewTest, self).setUp()
    self.init()

  def createTask(self, status=None, org=None, mentor=None, student=None):
    if not mentor:
      profile_helper = GCIProfileHelper(self.gci, self.dev_test)
      mentor = profile_helper.createOtherUser(
          'mentor@example.com').createMentor(self.org)

    if not student:
      profile_helper = GCIProfileHelper(self.gci, self.dev_test)
      student = profile_helper.createOtherUser(
          'student@example.com').createStudent()

    if not org:
      org = self.org

    if not status:
      status = 'Open'

    gci_task_helper = GCITaskHelper(self.program)
    return gci_task_helper.createTask(status, org, mentor, student)

  def assertFullEditTemplatesUsed(self, response):
    """Asserts that all the task creation base templates along with full edit
    template is used.
    """
    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/task_create/base.html')
    self.assertTemplateUsed(
        response, 'v2/modules/gci/task_create/_full_edit.html')

  def assertPostClaimEditTemplatesUsed(self, response):
    """Asserts that all the task creation base templates along with post claim
    edit template is used.
    """
    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/task_create/base.html')
    self.assertTemplateUsed(
        response, 'v2/modules/gci/task_create/_post_claim_edit.html')

  def testCreateTaskBeforeOrgsAnnouncedForNoRole(self):
    """Tests the task creation view before the program is public for user with
    no role.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createProfile()

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    # Task creation has not started yet and no role to create tasks
    self.assertResponseForbidden(response)

  def testCreateTaskBeforeOrgsAnnouncedForOrgAdmin(self):
    """Tests the task creation view before the program is public for org admin.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createOrgAdmin(self.org)

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    # Task creation has not started yet
    self.assertResponseForbidden(response)

  def testCreateTaskBeforeOrgsAnnouncedForMentor(self):
    """Tests the task creation view before the program is public for org admin.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createMentor(self.org)

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    # Task creation has not started yet
    self.assertResponseForbidden(response)

  def testCreateTaskBeforeOrgsAnnouncedForStudent(self):
    """Tests the task creation view before the program is public for org admin.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createStudent()

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    # Task creation has not started yet
    self.assertResponseForbidden(response)

  def testCreateTaskAfterClaimEndForNoRole(self):
    """Tests the task creation view after the task claim deadline for user with
    no role.
    """
    self.timeline.taskClaimEnded()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createProfile()

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    # Task creation has not started yet and no role to create tasks
    self.assertResponseForbidden(response)

  def testCreateTaskAfterClaimEndForOrgAdmin(self):
    """Tests the task creation view after the task claim deadline for org admin.
    """
    self.timeline.taskClaimEnded()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createOrgAdmin(self.org)

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    # Task creation has not started yet
    self.assertResponseForbidden(response)

  def testCreateTaskAfterClaimEndForMentor(self):
    """Tests the task creation view after the task claim deadline for mentor.
    """
    self.timeline.taskClaimEnded()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createMentor(self.org)

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    # Task creation has not started yet
    self.assertResponseForbidden(response)

  def testCreateTaskAfterClaimEndForStudent(self):
    """Tests the task creation view after the task claim deadline for student.
    """
    self.timeline.taskClaimEnded()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createStudent()

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    # Task creation has not started yet
    self.assertResponseForbidden(response)

  def testFullEditTaskBeforeOrgsAnnouncedForNoRole(self):
    """Tests the task full editing view before the program is public
    for user with no role.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createProfile()

    task = self.createTask()

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task full editing has not started yet and no role to edit tasks
    self.assertResponseForbidden(response)

  def testFullEditTaskBeforeOrgsAnnouncedForOrgAdmin(self):
    """Tests the task full editing view before the program is public
    for org admin.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createOrgAdmin(self.org)

    task = self.createTask()

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task full editing has not started yet
    self.assertResponseForbidden(response)

  def testFullEditTaskBeforeOrgsAnnouncedForMentor(self):
    """Tests the task full editing view before the program is public
    for mentor.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createMentor(self.org)

    task = self.createTask()

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task full editing has not started yet
    self.assertResponseForbidden(response)

  def testFullEditTaskBeforeOrgsAnnouncedForStudent(self):
    """Tests the task full editing view before the program is public
    for student.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createStudent()

    task = self.createTask()

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task full editing has not started yet
    self.assertResponseForbidden(response)

  def testFullEditTaskAfterClaimEndForNoRole(self):
    """Tests the task full editing view after the task claim deadline
    for user with no role.
    """
    self.timeline.taskClaimEnded()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createProfile()

    task = self.createTask()

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task full editing has not started yet and no role to edit tasks
    self.assertResponseForbidden(response)

  def testFullEditTaskAfterClaimEndForOrgAdmin(self):
    """Tests the task full editing view after the task claim deadline
    for org admin.
    """
    self.timeline.taskClaimEnded()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createOrgAdmin(self.org)

    task = self.createTask()

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task full editing has not started yet
    self.assertResponseForbidden(response)

  def testFullEditTaskAfterClaimEndForMentor(self):
    """Tests the task full editing view after the task claim deadline for
    mentor.
    """
    self.timeline.taskClaimEnded()

    task = self.createTask()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createMentor(self.org)

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task full editing has not started yet
    self.assertResponseForbidden(response)

  def testFullEditTaskAfterClaimEndForStudent(self):
    """Tests the task full editing view after the task claim deadline for
    student.
    """
    self.timeline.taskClaimEnded()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createStudent()

    task = self.createTask()

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task full editing has not started yet
    self.assertResponseForbidden(response)

  def testPostClaimEditTaskBeforeOrgsAnnouncedForNoRole(self):
    """Tests the task post claim editing view before the program is public
    for user with no role.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createProfile()

    task = self.createTask(status='ClaimRequested')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task post claim editing has not started yet and no role to edit tasks
    self.assertResponseForbidden(response)

  def testPostClaimEditTaskBeforeOrgsAnnouncedForOrgAdmin(self):
    """Tests the task post claim editing view before the program is public
    for org admin.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createOrgAdmin(self.org)

    task = self.createTask(status='Claimed')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task post claim editing has not started yet
    self.assertResponseForbidden(response)

  def testPostClaimEditTaskBeforeOrgsAnnouncedForMentor(self):
    """Tests the task post claim editing view before the program is public
    for mentor.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createMentor(self.org)

    task = self.createTask(status='ActionNeeded')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task post claim editing has not started yet
    self.assertResponseForbidden(response)

  def testPostClaimEditTaskBeforeOrgsAnnouncedForStudent(self):
    """Tests the task post claim editing view before the program is
    public for student.
    """
    self.timeline.orgSignup()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createStudent()

    task = self.createTask(status='NeedsWork')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task post claim editing has not started yet
    self.assertResponseForbidden(response)

  def testPostClaimEditTaskAfterClaimEndForNoRole(self):
    """Tests the task post claim editing view after the task claim deadline for
    user with no role.
    """
    self.timeline.taskClaimEnded()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createProfile()

    task = self.createTask(status='NeedsReview')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task post claim editing has not started yet and no role to edit tasks
    self.assertResponseForbidden(response)

  def testPostClaimEditTaskAfterClaimEndForOrgAdmin(self):
    """Tests the task post claim editing view after the task claim deadline
    for org admin.
    """
    self.timeline.taskClaimEnded()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createOrgAdmin(self.org)

    task = self.createTask(status='Closed')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task post claim editing has not started yet
    self.assertResponseForbidden(response)

  def testPostClaimEditTaskAfterClaimEndForMentor(self):
    """Tests the task post claim editing view after the task claim deadline
    for mentor.
    """
    self.timeline.taskClaimEnded()

    task = self.createTask(status='Claimed')

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createMentor(self.org)

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task post claim editing has not started yet
    self.assertResponseForbidden(response)

  def testPostClaimEditTaskAfterClaimEndForStudent(self):
    """Tests the task post claim editing view after the task claim deadline
    for student.
    """
    self.timeline.taskClaimEnded()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createStudent()

    task = self.createTask(status='ClaimRequested')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Task post claim editing has not started yet
    self.assertResponseForbidden(response)

  def testCreateTaskDuringProgramForNoRole(self):
    """Tests the task creation view during the program for user with no role.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createProfile()

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    # User has no privileges to create tasks
    self.assertResponseForbidden(response)

  def testCreateTaskDuringProgramForOrgAdmin(self):
    """Tests the task creation view during the program for org admin.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createOrgAdmin(self.org)

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    self.assertResponseOK(response)
    self.assertFullEditTemplatesUsed(response)

  def testCreateTaskDuringProgramForMentor(self):
    """Tests the task creation view during the program for org admin.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createMentor(self.org)

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    self.assertResponseOK(response)
    self.assertFullEditTemplatesUsed(response)

  def testCreateTaskDuringProgramForStudent(self):
    """Tests the task creation view during the program for org admin.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createStudent()

    url = '/gci/task/create/' + self.org.key().name()
    response = self.get(url)

    # Student can't create tasks
    self.assertResponseForbidden(response)

  def testFullEditTaskDuringProgramForNoRole(self):
    """Tests the task full editing view during the program for user
    with no role.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createProfile()

    task = self.createTask(status='Open')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # User without any role cannot edit the task
    self.assertResponseForbidden(response)

  def testFullEditTaskDuringProgramForOrgAdmin(self):
    """Tests the task full editing view during the program for org admin.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createOrgAdmin(self.org)

    task = self.createTask('Reopened')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    self.assertResponseOK(response)
    self.assertPostClaimEditTemplatesUsed(response)

  def testFullEditTaskDuringProgramForMentor(self):
    """Tests the task full editing view during the program for mentor.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createMentor(self.org)

    task = self.createTask('Unpublished')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    self.assertResponseOK(response)
    self.assertFullEditTemplatesUsed(response)

  def testFullEditTaskDuringProgramForStudent(self):
    """Tests the task full editing view during the program for student.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createStudent()

    task = self.createTask('Unapproved')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Student cannot edit task
    self.assertResponseForbidden(response)

  def testPostClaimEditTaskDuringProgramForNoRole(self):
    """Tests the task post claim editing view during the program for user
    with no role.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createProfile()

    task = self.createTask(status='ClaimRequested')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # User without any role cannot edit the task
    self.assertResponseForbidden(response)

  def testPostClaimEditTaskDuringProgramForOrgAdmin(self):
    """Tests the task post claim editing view during the program for org admin.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createOrgAdmin(self.org)

    task = self.createTask(status='Claimed')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    self.assertResponseOK(response)
    self.assertPostClaimEditTemplatesUsed(response)

  def testPostClaimEditTaskDuringProgramForMentor(self):
    """Tests the task post claim editing view during the program for mentor.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createMentor(self.org)

    task = self.createTask(status='NeedsReview')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    self.assertResponseOK(response)
    self.assertPostClaimEditTemplatesUsed(response)

  def testPostClaimEditTaskDuringProgramForStudent(self):
    """Tests the task post claim editing view during the program for student.
    """
    self.timeline.tasksPubliclyVisible()

    profile_helper = GCIProfileHelper(self.gci, self.dev_test)
    profile_helper.createStudent()

    task = self.createTask(status='ActionNeeded')

    url = '/gci/task/edit/%s/%s' % (self.gci.key().name(), task.key().id())
    response = self.get(url)

    # Student cannot edit task
    self.assertResponseForbidden(response)
