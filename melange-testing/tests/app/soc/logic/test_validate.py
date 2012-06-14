#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import unittest

from soc.logic import validate


class ValidateTest(unittest.TestCase):
  """Tests related to the validation helper functions.
  """

  def testIsFeedURLValid(self):
    """Tests whether the urls are valid feed urls.
    """
    #invalid: not a feed url
    self.assertFalse(validate.isFeedURLValid('http://www.google.com'))

    self.assertFalse(validate.isFeedURLValid(''))

    #valid feed url
    self.assertTrue(validate.isFeedURLValid(
        'http://googlesummerofcode.blogspot.com/feeds/posts/default'))

    #invalid: wrong protocol
    self.assertFalse(validate.isFeedURLValid(
        'htp://googlesummerofcode.blogspot.com/feeds/posts/default'))

  def testIsLinkIdFormatValid(self):
    """Tests the validity of Link Ids.
    """
    #valid: starts with lowercase, no double underscores, does not end 
    #with an underscore
    self.assertTrue(validate.isLinkIdFormatValid('sfd32'))

    #invalid: starts with a number
    self.assertFalse(validate.isLinkIdFormatValid('9s8whhu'))

    #invalid: starts with an underscore
    self.assertFalse(validate.isLinkIdFormatValid('_jhja87'))

    #valid: double underscore
    self.assertTrue(validate.isLinkIdFormatValid('kjnask__j87'))

    #valid: trailing underscore
    self.assertTrue(validate.isLinkIdFormatValid('jhsdfj_'))

    #invalid: starting and trailing underscores
    self.assertFalse(validate.isLinkIdFormatValid('_jhsj38_'))

    #invalid: starts with uppercase
    self.assertFalse(validate.isLinkIdFormatValid('Ukkjs'))

    #valid: underscore in the middle and rest in lowercase
    self.assertTrue(validate.isLinkIdFormatValid('a_b'))

    #invalid: a capital letter in the middle
    self.assertFalse(validate.isLinkIdFormatValid('aBc'))

  def testIsScopePathFormatValid(self):
    """Tests the validity of Scope Paths.

    Scope paths are group of Link Ids separated by '/'.
    """
    #invalid: empty string
    self.assertFalse(validate.isScopePathFormatValid(''))

    #valid: single chunk
    self.assertTrue(validate.isScopePathFormatValid('addvw'))

    #invalid: starts with an underscore
    self.assertFalse(validate.isScopePathFormatValid('_jhads/sdafsa'))

    #valid: chunks separated by '/'
    self.assertTrue(validate.isScopePathFormatValid('adhcd/dfds'))

    #valid: has a double underscore
    self.assertTrue(validate.isScopePathFormatValid('ndfnsj__nj'))

    #invalid: starts with a capital letter
    self.assertFalse(validate.isScopePathFormatValid('Usdn_/sdfa'))

    #invalid: second chunk ends with '/'
    self.assertFalse(validate.isScopePathFormatValid('adsf/sdfgr/'))

    #invalid: first chunk should not start with a '/'
    self.assertFalse(validate.isScopePathFormatValid('/abc'))

    #invalid: has a capital letter
    self.assertFalse(validate.isScopePathFormatValid('aBc/def'))

    #valid: underscore in the middle and rest of the letters in lowercase
    self.assertTrue(validate.isScopePathFormatValid('a_b/cde'))

