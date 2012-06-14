#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Tests for accept_proposals task
'''


import httplib
import urllib

from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import GSoCDjangoTestCase
from tests.test_utils import MailTestCase
from tests.test_utils import TaskQueueTestCase
from tests.timeline_utils import GSoCTimelineHelper

from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.project import GSoCProject


class AcceptProposalsTest(MailTestCase, GSoCDjangoTestCase, TaskQueueTestCase):
  """Tests for accept_proposals task.
  """

  ACCEPT_URL = '/tasks/gsoc/accept_proposals/accept'
  REJECT_URL = '/tasks/gsoc/accept_proposals/reject'
  MAIN_URL = '/tasks/gsoc/accept_proposals/main'

  def setUp(self):

    super(AcceptProposalsTest, self).setUp()
    self.init()
    self.createHost()
    self.createMentor()
    self.acceptProposals()

  def createHost(self):
    """Sets program host.
    """
    self.host = self.data
    self.host.createHost()
    self.host.createProfile()

  def createMentor(self):
    """Creates a mentor for organization.
    """
    self.mentor = GSoCProfileHelper(self.gsoc, self.dev_test)
    self.mentor.createOtherUser('mentor@example.com')
    self.mentor.createMentor(self.org)
    self.mentor.notificationSettings()

  def createStudent(self, email, n_proposals):
    """Creates a student with proposals.
    """
    student = GSoCProfileHelper(self.gsoc, self.dev_test)
    student.createOtherUser(email)
    student.createStudentWithProposals(self.org, self.mentor.profile,
                                       n=n_proposals)
    student.notificationSettings()
    return student

  def acceptProposals(self):
    """Set student proposals' acceptance state and make sure the organization
    has slots available.
    """
    self.student1 = self.createStudent('student1@example.com',
                                       n_proposals=2)
    self.student1_proposals = GSoCProposal.all().ancestor(
        self.student1.profile)
    self.student2 = self.createStudent('student2@example.com',
                                       n_proposals=3)
    self.student2_proposals = GSoCProposal.all().ancestor(
        self.student2.profile)

    self.assertEqual(self.student1_proposals.count(), 2)
    self.assertEqual(self.student2_proposals.count(), 3)

    #accept 1 of 2 proposal of student1
    proposal1 = self.student1_proposals[0]
    proposal1.accept_as_project = True
    proposal1.put()

    proposal2 = self.student1_proposals[1]
    proposal2.accept_as_project = False
    proposal2.put()

    #reject all proposals of student2
    for proposal in self.student2_proposals:
      proposal.accept_as_project = False
      proposal.put()

    self.org.slots = 5
    self.org.put()

    self.timeline.studentsAnnounced()

  def testConvertProposals(self):
    """Tests convert proposal task runs successfully.
    """
    post_data = {'program_key': self.gsoc.key().name()}
    response = self.post(self.MAIN_URL, post_data)
    self.assertEqual(response.status_code, httplib.OK)

    #assert accept task started for first org
    self.assertTasksInQueue(n=1, url=self.ACCEPT_URL)

    #assert main task started for next org
    self.assertTasksInQueue(n=1, url=self.MAIN_URL)

    #assert parameters to tasks
    for task in self.get_tasks():
      if task['url'] == self.ACCEPT_URL:
        expected_params = {'org_key':
                          urllib.quote_plus(self.org.key().id_or_name())}
        self.assertEqual(expected_params, task['params'])

      elif task['url'] == self.MAIN_URL:
        q = GSoCOrganization.all()
        q.filter('scope', self.gsoc)
        q.filter('status', 'active')
        q.get()
        expected_params = {'org_cursor': q.cursor(),
                           'program_key': urllib.quote_plus(
                               self.gsoc.key().name())}

        #as we can't know XSRF token, ignore it
        self.assertNotEqual(task['params'].get('xsrf_token'), None)
        task_params = task['params'].copy()
        del task_params['xsrf_token']

        self.assertEqual(expected_params, task_params)

  def testConverProposalsWithMissingParemeters(self):
    """Tests no tasks are queued if program_key is not supplied.
    """
    post_data = {}
    response = self.post(self.MAIN_URL, post_data)

    #assert no task started
    self.assertTasksInQueue(n=0, url=self.ACCEPT_URL)

  def testAcceptProposals(self):
    """Tests accept task for an organization.
    """
    from soc.modules.gsoc.models.program import GSoCProgramMessages
    properties = {
        'parent': self.gsoc,
    }
    self.seed(GSoCProgramMessages, properties)

    #assert current status of proposal to be accepted
    self.assertEqual(self.student1_proposals[0].status, 'pending')

    post_data = {'org_key': self.org.key().name(),
                 'program_key': self.gsoc.key().name()}
    response = self.post(self.ACCEPT_URL, post_data)

    #assert accepted student got proper emails
    self.assertEqual(response.status_code, httplib.OK)
    self.assertEmailSent(to=self.student1.profile.email,
                         subject='Congratulations!')
    self.assertEmailNotSent(to=self.student2.profile.email)

    #assert post status of proposal to be accepted
    self.assertEqual(self.student1_proposals[0].status, 'accepted')

    #assert a project created and associated with accepted student
    projects = GSoCProject.all().ancestor(self.student1.profile)
    self.assertEqual(projects.count(), 1)
    project = projects.get()
    self.assertEqual(project.status, 'accepted')

    #assert reject task is queued
    self.assertTasksInQueue(n=1, url=self.REJECT_URL)

    #assert parameters to task
    for task in self.get_tasks():
      if task['url'] == self.REJECT_URL:
        expected_params = {'org_key':
                           urllib.quote_plus(self.org.key().name()),
                           'program_key':
                           urllib.quote_plus(self.gsoc.key().name())}

        #ignore xsrf token
        self.assertNotEqual(task['params'].get('xsrf_token'), None)
        task_params = task['params'].copy()
        del task_params['xsrf_token']

        self.assertEqual(expected_params, task_params)


    # test reject proposals

    post_data = {'org_key': self.org.key().name(),
                 'program_key': self.gsoc.key().name()}
    response = self.post(self.REJECT_URL, post_data)
    self.assertEqual(response.status_code, httplib.OK)

    #assert post status of proposals
    self.assertEqual(self.student1_proposals[0].status, 'accepted')
    self.assertEqual(self.student1_proposals[1].status, 'rejected')
    self.assertEqual(self.student2_proposals[0].status, 'rejected')
    self.assertEqual(self.student2_proposals[1].status, 'rejected')
    self.assertEqual(self.student2_proposals[2].status, 'rejected')

    #assert student2 got a reject email
    self.assertEmailSent(to=self.student2.profile.email,
                         subject='Thank you for applying to %s'
                         % self.gsoc.name)
    #assert student2 got no accept email
    self.assertEmailNotSent(to=self.student2.profile.email,
                            subject='Congratulations!')
    #assert student1 got a reject email (already got an accept mail)
    self.assertEmailSent(to=self.student1.profile.email,
                        subject='Thank you for applying to %s'
                        % self.gsoc.name)

    #assert no projects are created for rejected student
    projects = GSoCProject.all().ancestor(self.student2.profile)
    self.assertEqual(projects.count(), 0)
