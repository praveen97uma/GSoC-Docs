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


"""Tests for soc.logic.host.
"""


import unittest

from google.appengine.api import users

from soc.logic import host as host_logic
from soc.models.host import Host
from soc.models.program import Program
from soc.models.sponsor import Sponsor
from soc.models.timeline import Timeline
from soc.models.user import User

from soc.modules.seeder.logic.seeder import logic as seeder_logic

class HostTest(unittest.TestCase):
  """Tests for logic of Host Model.
  """
  def setUp(self):
    """Set up required for the host logic tests.
    """
    self.founder = seeder_logic.seed(User)

    properties = {'founder': self.founder, 'home': None}
    self.sponsor = seeder_logic.seed(Sponsor, properties)

  def testGetHostForUser(self):
    """Tests if a host entity for the user entity is returned.
    """
    #create an entity group. The entity at index i in the list is the parent of
    #the entity at index i+1.
    user_entities = []
    user_entities.append(seeder_logic.seed(User))
    for i in range(4):
      properties = {'parent': user_entities[i].key()}
      entity = seeder_logic.seed(User, properties)
      user_entities.append(entity)

    #create a Host entity with parent as an entity in user_entities
    properties = {'parent': user_entities[4]}
    host = seeder_logic.seed(Host, properties)

    #root entity
    expected = host.key()
    user_entity = user_entities[0]
    self.assertEqual(host_logic.getHostForUser(user_entity).key(), expected)

    #all entities in the ancestral path
    expected = host.key()
    for entity in user_entities:
      self.assertEqual(host_logic.getHostForUser(entity).key(), expected)

    #an entity not in the same entity group
    expected = None
    entity = seeder_logic.seed(User)
    self.assertEqual(host_logic.getHostForUser(entity), expected)

  def testGetHostsForProgram(self):
    """Tests if a host entity for a program is returned.
    """
    properties = {'scope': self.sponsor, }
    program = seeder_logic.seed(Program, properties)

    #hosts of the program
    user_entities = []
    for i in range(5):
      properties = { 'host_for': [self.sponsor.key()]}
      entity = seeder_logic.seed(User, properties)
      user_entities.append(entity)

    host_entities = []
    for i in range(5):
      properties = {'parent': user_entities[i]}
      entity = seeder_logic.seed(Host, properties)
      host_entities.append(entity)

    expected = [entity.key() for entity in host_entities]
    hosts_list = host_logic.getHostsForProgram(program)
    actual = [host.key() for host in hosts_list]
    self.assertEqual(actual, expected)

    #program with a different scope
    program = seeder_logic.seed(Program)
    expected = []
    hosts_list = host_logic.getHostsForProgram(program)
    actual = [host.key() for host in hosts_list]
    self.assertEqual(actual, expected)

