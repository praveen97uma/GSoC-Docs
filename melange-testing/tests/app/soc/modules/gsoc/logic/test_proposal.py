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

"""Tests for soc.modules.gsoc.logic.duplicates.
"""


import unittest

from soc.modules.gsoc.logic import proposal as proposal_logic
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.proposal import GSoCProposal

from soc.modules.seeder.logic.seeder import logic as seeder_logic


class ProposalTest(unittest.TestCase):
  """Tests the gsoc logic for proposals.
  """

  def setUp(self):
    self.program = seeder_logic.seed(GSoCProgram)
    #An organization which has all its slots allocated.
    org_properties = {'scope':self.program, 'slots': 2}
    self.foo_organization = seeder_logic.seed(GSoCOrganization, org_properties)

    proposal_properties = {'program': self.program, 'org': self.foo_organization,
                           'mentor': None, 'status': 'accepted'}
    self.foo_proposals = seeder_logic.seedn(GSoCProposal, 2,
                                            proposal_properties)

    #Create organization which has slots to be allocated. We create both 
    #rejected and accepted proposals for this organization entity.
    org_properties = {'scope':self.program, 'slots': 5}
    self.bar_organization = seeder_logic.seed(GSoCOrganization, org_properties)
    #Create some already accepted proposals for bar_organization.
    proposal_properties = {'program': self.program, 'org': self.bar_organization,
                           'mentor': None, 'status': 'accepted'}
    self.bar_accepted_proposals = seeder_logic.seedn(GSoCProposal, 2,
                                                     proposal_properties)
    #proposals which are yet to be accepted.
    proposal_properties = {'status': 'pending', 'accept_as_project': True,
                           'has_mentor': True, 'program': self.program,
                           'org': self.bar_organization}
    self.bar_to_be_accepted_proposals = seeder_logic.seedn(GSoCProposal, 3,
                                                           proposal_properties)
    #proposals which were rejected.
    proposal_properties = {'status': 'pending', 'accept_as_project': False,
                           'has_mentor': False, 'program': self.program,
                           'org': self.bar_organization}
    self.bar_rejected_proposals = seeder_logic.seedn(GSoCProposal, 2,
                                                     proposal_properties)

    #Create an organization for which the accepted proposals are more than
    #the available slots.
    org_properties = {'scope': self.program, 'slots': 1}
    self.happy_organization = seeder_logic.seed(GSoCOrganization, org_properties)
    proposal_properties = {'status': 'pending', 'accept_as_project': True,
                           'has_mentor': True, 'program': self.program,
                           'org': self.happy_organization}

    self.happy_accepted_proposals = []
    proposal_properties['score'] = 2
    self.happy_accepted_proposals.append(seeder_logic.seed(GSoCProposal,
                                                           proposal_properties))
    proposal_properties['score'] = 5
    self.happy_accepted_proposals.append(seeder_logic.seed(GSoCProposal,
                                                           proposal_properties))

  def testGetProposalsToBeAcceptedForOrg(self):
    """Tests if all GSoCProposals to be accepted into a program for a given
    organization are returned.
    """
    #Test that for organization which has been allotted all its slots, an empty
    #list is returned.
    org = self.foo_organization
    expected = []
    actual = proposal_logic.getProposalsToBeAcceptedForOrg(org)
    self.assertEqual(expected, actual)

    #Test that for an organization which has empty slots, only accepted
    #proposals are returned. We have both accepted and rejected proposals for
    #bar_organization.
    org = self.bar_organization
    expected_proposals_entities = self.bar_to_be_accepted_proposals
    expected = set([prop.key() for prop in expected_proposals_entities])
    actual_proposals_entities = proposal_logic.getProposalsToBeAcceptedForOrg(org)
    actual = set([prop.key() for prop in actual_proposals_entities])
    self.assertEqual(expected, actual)

    #Since self.happy_organization has more accepted projects than the available
    #slots, a proposal with a higher score should be returned.
    actual_proposals_entities = proposal_logic.getProposalsToBeAcceptedForOrg(
        self.happy_organization)
    actual = [prop.key() for prop in actual_proposals_entities]
    expected = [self.happy_accepted_proposals[1].key()]
    self.assertEqual(actual, expected)

    #Create an organization which has empty slots but no accepted projects.
    properties = {'scope': self.program, 'slots': 5}
    organization = seeder_logic.seed(GSoCOrganization, properties)
    expected = []
    actual = proposal_logic.getProposalsToBeAcceptedForOrg(organization)
    self.assertEqual(actual, expected)

