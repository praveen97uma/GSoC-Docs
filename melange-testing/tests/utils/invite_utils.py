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


"""Utils for manipulating invite data.
"""


from soc.models.request import INVITATION_TYPE

from soc.modules.gci.models.request import GCIRequest

from soc.modules.seeder.logic.seeder import logic as seeder_logic


class GCIInviteHelper(object):
  """Base helper class to help to create and manipulate the invites.
  """

  def seed(self, model, properties):
    return seeder_logic.seed(model, properties, recurse=False)

  def createMentorInvite(self, org, user):
    properties = {
        'status': 'pending',
        'type': INVITATION_TYPE,
        'role': 'mentor',
        'org': org,
        'user': user
        }
    return self.seed(GCIRequest, properties)

  def createOrgAdminInvite(self, org, user):
    properties = {
        'status': 'pending',
        'type': INVITATION_TYPE,
        'role': 'org_admin',
        'org': org,
        'user': user
        }
    return self.seed(GCIRequest, properties)
