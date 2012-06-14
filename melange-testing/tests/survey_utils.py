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


"""Utils for manipulating the survey.
"""


from tests.profile_utils import GSoCProfileHelper
from tests import timeline_utils

from soc.modules.gsoc.models.grading_project_survey import GradingProjectSurvey
from soc.modules.gsoc.models.project_survey import ProjectSurvey

from soc.modules.seeder.logic.providers.string import SurveyKeyNameProvider
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class SurveyHelper(object):
  """Helper class to aid in setting the survey.
  """

  def __init__(self, program, dev_test, org_app=None):
    self.program = program
    self.dev_test = dev_test
    self.org_app = org_app

  def seed(self, model, properties):
    return seeder_logic.seed(model, properties, recurse=False)

  def evalSchemaString(self):
    return (
        '[["frm-t1309871149671-item","frm-t1309871322655-item",'
        '"frm-t1309871157535-item","frm-t1309871294200-item",'
        '"frm-t1310822212610-item"],{"frm-t1309871149671-item":'
        '{"field_type":"input_text","required":true,"label":'
        '"What%20is%20your%20name%3F"},"frm-t1309871322655-item":'
        '{"field_type":"checkbox","required":false,"other":false,'
        '"values":[{"value":"Option%203","checked":true},{"value":'
        '"Option%202","checked":true},{"value":"Option%204","checked":true}'
        ',{"value":"Option%201","checked":true}],"label":"'
        'Give%20every%20option%20you%20think%20is%20right"},'
        '"frm-t1309871157535-item":{"field_type":"textarea","required":'
        'false,"label":"Write%20a%20detail%20of%20your%20project%3F"},'
        '"frm-t1309871294200-item":{"field_type":"radio","required":'
        'false,"other":false,"values":[{"value":"Amongst%20the%20best%20'
        'people%20I%27ve%20ever%20worked%20with%20","checked":false},'
        '{"value":"Don%27t%20Know","checked":false},{"value":"Yes","checked"'
        ':false}],"label":"Are%20you%20alright%3F"},"frm-t1310822212610-item"'
        ':{"field_type":"radio","required":true,"other":true,"values":'
        '[{"value":"Wa","checked":true},{"value":"Wa%20Wa","checked":false}]'
        ',"label":"Testing%20radio%20again%20%3A%29"}}]')

  def createEvaluation(self, survey, host=None, override={}):
    if not host:
      host_profile = GSoCProfileHelper(self.program, self.dev_test)
      host_profile.createOtherUser('host@example.com')
      host = host_profile.createHost()

    # TODO (Madhu): Remove scope and author once the survey data conversion
    # is complete
    properties = {
        'program': self.program,
        'created_by': host,
        'prefix': 'gsoc_program',
        'schema': self.evalSchemaString(),
        'survey_content': None,
        'author': host,
        'modified_by': host,
        'scope': self.program,
        'key_name': SurveyKeyNameProvider(),
        'survey_start': timeline_utils.past(),
        'survey_end': timeline_utils.future(),
        }
    properties.update(override)
    return self.seed(survey, properties)

  def createStudentEvaluation(self, host=None, override={}):
    return self.createEvaluation(ProjectSurvey, host=host, override=override)

  def createMentorEvaluation(self, host=None, override={}):
    return self.createEvaluation(GradingProjectSurvey, host=host,
                                 override=override)

  def createOrgApp(self, link_id, user, override={}):
    """Creates a new OrgAppRecord for the specified link_id.
    """
    from soc.models.org_app_record import OrgAppRecord
    properties = {
      'org_id': link_id,
      'survey': self.org_app,
      'backup_admin': user,
      'user': user,
      'main_admin': user,
      'status': 'accepted',
      'program': self.program,
    }
    properties.update(override)
    entity = self.seed(OrgAppRecord, properties)
    return entity
