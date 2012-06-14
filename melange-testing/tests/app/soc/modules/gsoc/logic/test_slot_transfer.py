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


"""Tests for soc.modules.gsoc.logic.slot_transfer.
"""


import unittest

from soc.modules.seeder.logic.seeder import logic as seeder_logic

from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.logic import slot_transfer as slot_transfer_logic
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.slot_transfer import GSoCSlotTransfer


class SlotTransferTest(unittest.TestCase):
  """Tests for GSoC slot transfer logic.
  """

  def setUp(self):
    self.gsoc_program = seeder_logic.seed(GSoCProgram)
    self.gsoc_organization = seeder_logic.seed(GSoCOrganization,
                                               {'scope': self.gsoc_program})
    slot_transfer_properties = {'program': self.gsoc_program,
                                'status': 'accepted'}

    organization_properties = {'scope': self.gsoc_program}
    self.org_entities = seeder_logic.seedn(GSoCOrganization, 10,
                                           organization_properties)

    #Assign one slot transfer entity to each of the organization in
    #self.org_entities
    self.slot_transfer_entities = []
    properties = slot_transfer_properties.copy()
    for i in range(10):
      properties['parent'] = self.org_entities[i]
      entity = seeder_logic.seed(GSoCSlotTransfer, properties)
      self.slot_transfer_entities.append(entity)

    #Assign multiple slot transfer entities to self.gsoc_organization
    properties = slot_transfer_properties.copy()
    properties.update({'parent': self.gsoc_organization})
    self.gsoc_organization_slot_transfer_entities = seeder_logic.seedn(
        GSoCSlotTransfer, 5, properties)

  def testGetSlotTransferEntitiesForOrg(self):
    """Tests if all the slot transfer entities for an organization is returned.
    """
    #Every organization has a single slot transfer entity.
    expected = self.slot_transfer_entities[0]
    actual = slot_transfer_logic.getSlotTransferEntitiesForOrg(
                 self.org_entities[0])
    self.assertEqual(actual[0].key(), expected.key())
    self.assertNotEqual(actual[0].key(), self.slot_transfer_entities[1].key())

    #Multiple slot transfer entities for an organization. All the entities
    #must be returned.
    expected = [
        entity.key() for entity in self.gsoc_organization_slot_transfer_entities]
    slot_transfer_entities = slot_transfer_logic.getSlotTransferEntitiesForOrg(
                                 self.gsoc_organization)
    actual = [entity.key() for entity in slot_transfer_entities]
    self.assertEqual(expected, actual)

    #An organization has no slot transer entity
    expected = []
    organization = seeder_logic.seed(GSoCOrganization,
                                     {'scope': self.gsoc_program})
    actual = slot_transfer_logic.getSlotTransferEntitiesForOrg(organization)
    self.assertEqual(expected, actual)

