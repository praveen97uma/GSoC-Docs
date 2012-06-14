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


"""Utils for manipulating program data.
"""


from datetime import date

from soc.models.document import Document
from soc.models.org_app_survey import OrgAppSurvey
from soc.models.site import Site
from soc.models.sponsor import Sponsor
from soc.models.user import User

from soc.modules.gci.models.organization import GCIOrganization
from soc.modules.gci.models.program import GCIProgram
from soc.modules.gci.models.program import GCIProgramMessages
from soc.modules.gci.models.timeline import GCITimeline
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.program import GSoCProgramMessages
from soc.modules.gsoc.models.timeline import GSoCTimeline
from soc.modules.seeder.logic.providers.string import DocumentKeyNameProvider
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class ProgramHelper(object):
  """Helper class to aid in manipulating program data.
  """

  def __init__(self):
    """Initializes the ProgramHelper.

    Args:
      program: a program
      org_app: an organization application
      org: an organization
      site: a site
    """
    self.founder = None
    self.sponsor = None
    self.program = None
    self.org_app = None
    self.org = None
    self.site = None
    self.createOrg = self.createOrUpdateOrg

  def seed(self, model, properties,
           auto_seed_optional_properties=True):
    return seeder_logic.seed(model, properties, recurse=False,
        auto_seed_optional_properties=auto_seed_optional_properties)

  def seedn(self, model, properties, n,
            auto_seed_optional_properties=True):
    return seeder_logic.seedn(model, n, properties, recurse=False,
        auto_seed_optional_properties=auto_seed_optional_properties)

  def createFounder(self, override={}):
    """Creates a founder for the defined properties.
    """
    if self.founder:
      return self.founder
    properties = {}
    properties.update(override)
    self.founder = self.seed(User, properties)
    return self.founder

  def createSponsor(self, override={}):
    """Creates a sponsor for the defined properties.
    """
    if self.sponsor:
      return self.sponsor
    if self.founder is None:
      self.createFounder()
    properties = {'founder': self.founder, 'home': None}
    properties.update(override)
    self.sponsor = self.seed(Sponsor, properties)
    return self.sponsor

  def createProgram(self, override={}):
    """Creates a program for the defined properties.
    """
    if self.sponsor is None:
      self.createSponsor()

  def createOrgApp(self, override={}):
    """Creates an organization application for the defined properties.
    """
    if self.org_app:
      return self.org_app
    if self.program is None:
      self.createProgram()
    # TODO (Madhu): Remove scope and author fields once the data
    # conversion is done.
    properties = {
        'key_name': 'gci_program/%s/orgapp' % self.program.key().name(),
        'scope': self.program, 'program': self.program,
        'modified_by': self.founder,
        'created_by': self.founder,
        'author': self.founder,
        'schema': ('[["item"],{"item":{"field_type":"input_text",'
                   '"required":false, "label":"test"}}]'),
        'survey_content': None,
    }
    properties.update(override)
    self.org_app = self.seed(OrgAppSurvey, properties)
    return self.org_app

  def _updateEntity(self, entity, override):
    """Updates self.<entity> with override.
    """
    properties = entity.properties()
    for name, value in override.iteritems():
      properties[name].__set__(entity, value)
    entity.put()
    return entity

  def _updateOrg(self, override):
    """Updates self.org with override.
    """
    return self._updateEntity(self.org, override)

  def createOrUpdateOrg(self, override={}):
    """Creates or updates an org (self.org) for the defined properties.
    """
    if self.org:
      if not override:
        return self.org
      else:
        return self._updateOrg(override)
    self.org = self.createNewOrg(override)
    return self.org

  def createNewOrg(self, override={}):
    """Creates a new organization for the defined properties.

    This new organization will not be stored in self.org but returned.
    """
    if self.program is None:
      self.createProgram()

  def createSite(self, override={}):
    """Creates a site for the defined properties.
    """
    if self.program is None:
      self.createProgram()
    properties = {
        'key_name': 'site', 'link_id': 'site',
        'active_program': self.program,
        'latest_gsoc': 'google/gsoc',
        'latest_gci': 'google/gci',
    }
    properties.update(override)
    self.site = Site(**properties)
    self.site.put()
    return self.site


class GSoCProgramHelper(ProgramHelper):
  """Helper class to aid in manipulating GSoC program data.
  """

  def __init__(self):
    """Initializes the GSoCProgramHelper.
    """
    super(GSoCProgramHelper, self).__init__()

  def createProgram(self, override={}):
    """Creates a program for the defined properties.
    """
    if self.program:
      return self.program
    super(GSoCProgramHelper, self).createProgram()
    properties = {'scope': self.sponsor}
    self.program_timeline = self.seed(GSoCTimeline, properties)

    properties = {'timeline': self.program_timeline,
                  'status': 'visible', 'apps_tasks_limit': 20,
                  'scope': self.sponsor,
                  'student_agreement': None, 'events_page': None,
                  'help_page': None, 'connect_with_us_page': None,
                  'mentor_agreement': None, 'org_admin_agreement': None,
                  'terms_and_conditions': None,
                  'home': None, 'about_page': None}
    properties.update(override)
    self.program = self.seed(GSoCProgram, properties)

    properties = {
        'prefix': 'gsoc_program', 'scope': self.program,
        'read_access': 'public', 'key_name': DocumentKeyNameProvider(),
        'modified_by': self.founder, 'author': self.founder,
        'home_for': None,
    }
    document = self.seed(Document, properties=properties)

    self.program.about_page = document
    self.program.events_page = document
    self.program.help_page = document
    self.program.connect_with_us_page = document
    self.program.privacy_policy = document
    self.program.put()

    properties = {
        'parent': self.program,
        'accepted_orgs_msg': 'Organization accepted',
        'rejected_orgs_msg': 'Organization rejected',
        }
    self.program_messages = self.seed(GSoCProgramMessages,
        properties=properties)
    self.program_messages.put()

    return self.program

  def createNewOrg(self, override={}):
    """Creates a new organization for the defined properties.

    This new organization will not be stored in self.org but returned.
    """
    super(GSoCProgramHelper, self).createNewOrg(override)
    properties = {'scope': self.program, 'status': 'active',
                  'scoring_disabled': False, 'max_score': 5,
                  'founder': self.founder, 'home': None,}
    properties.update(override)
    return self.seed(GSoCOrganization, properties)

class GCIProgramHelper(ProgramHelper):
  """Helper class to aid in manipulating GCI program data.
  """

  def __init__(self):
    """Initializes the GCIProgramHelper.
    """
    super(GCIProgramHelper, self).__init__()

  def createProgram(self, override={}):
    """Creates a program for the defined properties.
    """
    if self.program:
      return self.program
    super(GCIProgramHelper, self).createProgram()

    properties = {'scope': self.sponsor}
    self.program_timeline = self.seed(GCITimeline, properties)

    properties = {
        'timeline': self.program_timeline,
        'status': 'visible',
        'scope': self.sponsor,
        'student_agreement': None, 'events_page': None,
        'help_page': None, 'connect_with_us_page': None,
        'mentor_agreement': None, 'org_admin_agreement': None,
        'terms_and_conditions': None, 'home': None, 'about_page': None,
        'nr_simultaneous_tasks': 5,
        'student_min_age': 13, 'student_max_age': 17,
        'student_min_age_as_of': date.today(),
        'task_types': ['code', 'documentation', 'design'],
    }
    properties.update(override)
    self.program = self.seed(GCIProgram, properties)

    properties = {
        'prefix': 'gci_program', 'scope': self.program,
        'read_access': 'public', 'key_name': DocumentKeyNameProvider(),
        'modified_by': self.founder, 'author': self.founder,
        'home_for': None,
    }
    document = self.seed(Document, properties=properties)

    self.program.about_page = document
    self.program.events_page = document
    self.program.help_page = document
    self.program.connect_with_us_page = document
    self.program.privacy_policy = document
    self.program.put()

    properties = {
        'parent': self.program,
        'accepted_orgs_msg': 'Organization accepted',
        'rejected_orgs_msg': 'Organization rejected',
        }
    self.program_messages = self.seed(GCIProgramMessages,
        properties=properties)
    self.program_messages.put()

    return self.program

  def createNewOrg(self, override={}):
    """Creates a new organization for the defined properties.

    This new organization will not be stored in self.org but returned.
    """
    super(GCIProgramHelper, self).createNewOrg(override)
    properties = {'scope': self.program, 'status': 'active',
                  'founder': self.founder,
                  'home': None,
                  'task_quota_limit': 100}
    properties.update(override)
    return self.seed(GCIOrganization, properties)
