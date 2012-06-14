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


"""Utils for manipulating profile data.
"""


from soc.modules.seeder.logic.seeder import logic as seeder_logic


class ProfileHelper(object):
  """Helper class to aid in manipulating profile data.
  """

  def __init__(self, program, dev_test):
    """Initializes the ProfileHelper.

    Args:
      program: a program
      dev_test: if set, always creates users as developers
    """
    self.program = program
    self.user = None
    self.profile = None
    self.dev_test = dev_test

  def seed(self, model, properties,
           auto_seed_optional_properties=True):
    return seeder_logic.seed(model, properties, recurse=False,
        auto_seed_optional_properties=auto_seed_optional_properties)

  def seedn(self, model, properties, n,
            auto_seed_optional_properties=True):
    return seeder_logic.seedn(model, n, properties, recurse=False,
        auto_seed_optional_properties=auto_seed_optional_properties)

  def login(self, user_email, user_id):
    """Logs in the specified user.

    Args:
      user_email: the user email as a string, e.g.: 'test@example.com'
      user_id: the user id as a string, e.g.: '42'
    """
    import os
    os.environ['USER_EMAIL'] = user_email
    os.environ['USER_ID'] = user_id

  def logout(self):
    """Logs out the current user.
    """
    import os
    del os.environ['USER_EMAIL']
    del os.environ['USER_ID']

  def createUser(self):
    """Creates a user entity for the current user.
    """
    if self.user:
      return self.user
    from soc.models.user import User
    from soc.modules.seeder.logic.providers.user import CurrentUserProvider
    properties = {'account': CurrentUserProvider(),
                  'status': 'valid', 'is_developer': self.dev_test}
    self.user = self.seed(User, properties=properties)
    return self.user

  def createDeveloper(self):
    """Creates a user entity for the current user that is a developer.
    """
    self.createUser()
    self.user.is_developer = True
    self.user.put()
    return self.user

  def createOtherUser(self, email):
    """Creates a user entity for the specified email.
    """
    from soc.models.user import User
    from soc.modules.seeder.logic.providers.user import FixedUserProvider
    properties = {'account': FixedUserProvider(value=email), 'status': 'valid'}
    self.user = self.seed(User, properties=properties)
    return self

  def deleteProfile(self):
    """Deletes the created profile.
    """
    if not self.profile:
      return self

    if self.profile.student_info:
      self.profile.student_info.delete()
    self.profile.delete()
    self.profile = None

    return self

  def createProfile(self):
    """Creates a profile for the current user.
    """
    pass

  def createStudent(self):
    """Sets the current user to be a student for the current program.
    """
    pass

  def removeStudent(self):
    """Removes the student profile from the current user.
    """
    if not self.profile:
      return self
    if self.profile.student_info:
      self.profile.student_info.delete()
      self.profile.student_info = None
      self.profile.put()
    return self.profile

  def createHost(self):
    """Sets the current user to be a host for the current program.
    """
    self.createUser()
    self.user.host_for = [self.program.scope.key()]
    self.user.put()
    return self.user

  def removeHost(self):
    """Removes the host profile from the current user.
    """
    if not self.user:
      return self
    self.user.host_for = []
    self.user.put()
    return self.user

  def createOrgAdmin(self, org):
    """Creates an org admin profile for the current user.
    """
    self.createProfile()
    self.profile.mentor_for = [org.key()]
    self.profile.org_admin_for = [org.key()]
    self.profile.is_mentor = True
    self.profile.is_org_admin = True
    self.profile.put()
    return self.profile

  def removeOrgAdmin(self):
    """Removes the org admin profile from the current user.
    """
    if not self.profile:
      return self
    self.profile.mentor_for = []
    self.profile.org_admin_for = []
    self.profile.is_mentor = False
    self.profile.is_org_admin = False
    self.profile.put()
    return self.profile

  def createMentor(self, org):
    """Creates an mentor profile for the current user.
    """
    self.createProfile()
    self.profile.mentor_for = [org.key()]
    self.profile.is_mentor = True
    self.profile.put()
    return self.profile

  def removeMentor(self):
    """Removes the mentor profile from the current user.
    """
    if not self.profile:
      return self
    self.profile.mentor_for = []
    self.profile.is_mentor = False
    self.profile.put()
    return self.profile

  def removeAllRoles(self):
    """Removes all profile roles from the current user excluding host.
    """
    if not self.profile:
      return self
    self.removeMentor()
    self.removeOrgAdmin()
    self.removeStudent()
    return self.profile

  def clear(self):
    if self.profile and self.profile.student_info:
      self.profile.student_info.delete()
    if self.profile:
      self.profile.delete()
    if self.user:
      self.user.delete()
    self.profile = None
    self.user = None


class GSoCProfileHelper(ProfileHelper):
  """Helper class to aid in manipulating GSoC profile data.
  """

  def __init__(self, program, dev_test):
    """Initializes the GSocProfileHelper.

    Args:
      program: a GSoCProgram
      dev_test: if set, always creates users as developers
    """
    super(GSoCProfileHelper, self).__init__(program, dev_test)

  def createProfile(self):
    """Creates a profile for the current user.
    """
    if self.profile:
      return self.profile
    from soc.modules.gsoc.models.profile import GSoCProfile
    user = self.createUser()
    properties = {
        'link_id': user.link_id, 'student_info': None, 'user': user,
        'parent': user, 'scope': self.program, 'status': 'active',
        'email': self.user.account.email(),
        'mentor_for': [], 'org_admin_for': [],
        'is_org_admin': False, 'is_mentor': False, 'is_student': False
    }
    self.profile = self.seed(GSoCProfile, properties)
    return self.profile

  def notificationSettings(
      self, new_requests=False, new_invites=False,
      invite_handled=False, request_handled=False,
      new_proposals=False, proposal_updates=False,
      public_comments=False, private_comments=False):
    self.createProfile()
    self.profile.notify_new_requests = new_requests
    self.profile.notify_new_invites = new_invites
    self.profile.notify_invite_handled = invite_handled
    self.profile.notify_request_handled = request_handled
    self.profile.notify_new_proposals = new_proposals
    self.profile.notify_proposal_updates = proposal_updates
    self.profile.notify_public_comments = public_comments
    self.profile.notify_private_comments = private_comments
    self.profile.put()

  def createStudent(self):
    """Sets the current user to be a student for the current program.
    """
    self.createProfile()
    from soc.modules.gsoc.models.profile import GSoCStudentInfo
    properties = {'key_name': self.profile.key().name(), 'parent': self.profile,
                  'school': None, 'tax_form': None, 'enrollment_form': None,
                  'number_of_projects': 0, 'number_of_proposals': 0,
                  'passed_evaluations': 0, 'failed_evaluations': 0,
                  'program': self.program}
    self.profile.student_info = self.seed(GSoCStudentInfo, properties)
    self.profile.is_student = True
    self.profile.put()
    return self.profile

  def createStudentWithProposal(self, org, mentor):
    """Sets the current user to be a student with a proposal for the
    current program.
    """
    return self.createStudentWithProposals(org, mentor, 1)

  def createStudentWithProposals(self, org, mentor, n):
    """Sets the current user to be a student with specified number of 
    proposals for the current program.
    """
    self.createStudent()
    self.profile.student_info.number_of_proposals = n
    self.profile.put()
    from soc.modules.gsoc.models.proposal import GSoCProposal
    properties = {
        'scope': self.profile, 'score': 0, 'nr_scores': 0,
        'is_publicly_visible': False, 'accept_as_project': False,
        'is_editable_post_deadline': False, 'extra': None,
        'parent': self.profile, 'status': 'pending', 'has_mentor': True,
        'program': self.program, 'org': org, 'mentor': mentor
    }
    self.seedn(GSoCProposal, properties, n)
    return self.profile

  def createStudentWithProject(self, org, mentor):
    """Sets the current user to be a student with a project for the 
    current program.
    """
    return self.createStudentWithProjects(org, mentor, 1)

  def createStudentWithProjects(self, org, mentor, n):
    """Sets the current user to be a student with specified number of 
    projects for the current program.
    """
    student = self.createStudent()
    student.student_info.number_of_projects = n
    student.student_info.put()
    from soc.modules.gsoc.models.project import GSoCProject
    properties = {'program': self.program, 'org': org, 'status': 'accepted',
                  'parent': self.profile, 'mentors': [mentor.key()]}
    self.seedn(GSoCProject, properties, n)
    return self.profile

  def createMentorWithProject(self, org, student):
    """Creates an mentor profile with a project for the current user.
    """
    self.createMentor(org)
    from soc.modules.gsoc.models.project import GSoCProject
    properties = {'mentors': [self.profile.key()], 'program': self.program,
                  'parent': student, 'org': org, 'status': 'accepted'}
    self.seed(GSoCProject, properties)
    return self.profile

  def createMentorRequest(self, org):
    """Creates a mentor request.
    """
    from soc.modules.gsoc.models.request import GSoCRequest
    self.createProfile()
    properties = {
        'role': 'mentor', 'user': self.user, 'org': org,
        'status': 'pending', 'type': 'Request',
        'parent': self.user,
    }
    return seeder_logic.seed(GSoCRequest, properties=properties)

  def createInvitation(self, org, role):
    from soc.modules.gsoc.models.request import GSoCRequest
    self.createProfile()
    properties = {
        'role': role, 'user': self.user, 'org': org,
        'status': 'pending', 'type': 'Invitation',
        'parent': self.user,
    }
    return seeder_logic.seed(GSoCRequest, properties=properties)

class GCIProfileHelper(ProfileHelper):
  """Helper class to aid in manipulating GCI profile data.
  """

  def __init__(self, program, dev_test):
    """Initializes the GSocProfileHelper.

    Args:
      program: a GCIProgram
      dev_test: if set, always creates users as developers
    """
    super(GCIProfileHelper, self).__init__(program, dev_test)

  def createProfile(self):
    """Creates a profile for the current user.
    """
    if self.profile:
      return
    from soc.modules.gci.models.profile import GCIProfile
    user = self.createUser()
    properties = {
        'link_id': user.link_id, 'student_info': None, 'user': user,
        'parent': user, 'scope': self.program, 'status': 'active',
        'email': self.user.account.email(),
        'mentor_for': [], 'org_admin_for': [],
        'is_org_admin': False, 'is_mentor': False, 'is_student': False
    }
    self.profile = self.seed(GCIProfile, properties)
    return self.profile

  def notificationSettings(
      self, new_requests=False, new_invites=False,
      invite_handled=False, request_handled=False,
      comments=False):
    self.createProfile()
    self.profile.notify_new_requests = new_requests
    self.profile.notify_new_invites = new_invites
    self.profile.notify_invite_handled = invite_handled
    self.profile.notify_request_handled = request_handled
    self.profile.notify_comments = comments
    self.profile.put()

  def createStudent(self):
    """Sets the current user to be a student for the current program.
    """
    self.createProfile()
    from soc.modules.gci.models.profile import GCIStudentInfo
    properties = {'key_name': self.profile.key().name(), 'parent': self.profile,
                  'school': None, 'number_of_tasks_completed': 0,
                  'program': self.program}
    self.profile.student_info = self.seed(GCIStudentInfo, properties)
    self.profile.is_student = True
    self.profile.put()
    return self.profile

  def createStudentWithTask(self, status, org, mentor):
    """Sets the current user to be a student with a task for the 
    current program.
    """
    return self.createStudentWithTasks(status, org, mentor, 1)[0]

  def createStudentWithTasks(self, status, org, mentor, n=1):
    """Sets the current user to be a student with specified number of 
    tasks for the current program.
    """
    from tests.gci_task_utils import GCITaskHelper
    student = self.createStudent()
    student.student_info.put()
    gci_task_helper = GCITaskHelper(self.program)
    tasks = []
    for _ in xrange(n):
        task = gci_task_helper.createTask(status, org, mentor, student)
        tasks.append(task)
    return tasks

  def createMentorWithTask(self, status, org):
    """Creates an mentor profile with a task for the current user.
    """
    return self.createMentorWithTasks(status, org, 1)[0]

  def createMentorWithTasks(self, status, org, n=1):
    """Creates an mentor profile with a task for the current user.
    """
    from tests.gci_task_utils import GCITaskHelper
    self.createMentor(org)
    gci_task_helper = GCITaskHelper(self.program)
    tasks = []
    for _ in xrange(n):
        task = gci_task_helper.createTask(status, org, self.profile)
        tasks.append(task)
    return tasks
