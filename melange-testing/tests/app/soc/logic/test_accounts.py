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


"""Tests for soc.logic.accounts.
"""


import os
import unittest

from google.appengine.api import users

from soc.logic import accounts


class TestAccounts(unittest.TestCase):
  """Tests for accounts logic.
  """
  def setUp(self):
    self.regular_email = 'test@example.com'
    self.non_normal_email = 'TEST1@example.com'
    self.invalid_emails = ['test', 'test@example', 'test#/1$@example.com']
    self.account = users.get_current_user()

  def testGetCurrentAccount(self):
    """Tests that current account is returned.
    """
    expected_account = accounts.normalizeAccount(self.account)
    self.assertEqual(accounts.getCurrentAccount(), expected_account)

    expected_account = self.account
    self.assertEqual(accounts.getCurrentAccount(False), expected_account)

    default_account_setting = os.environ.get('USER_EMAIL', None)
    try:
      os.environ['USER_EMAIL'] = self.non_normal_email
      expected_account = users.get_current_user()
      self.assertEqual(accounts.getCurrentAccount(False), expected_account)
      self.assertEqual(accounts.getCurrentAccount(True),
          accounts.normalizeAccount(expected_account))
    finally:
      if default_account_setting is None:
        del os.environ['USER_EMAIL']
      else:
        os.environ['USER_EMAIL'] = default_account_setting

  def testGetCurrentUserId(self):
    """Tests if correct user id is returned.
    """
    default_user_id = os.environ.get('USER_ID', None)
    try:
      os.environ['USER_ID'] = expected_user_id = '42'
      self.assertEqual(accounts.getCurrentUserId(), expected_user_id)
    finally:
      if default_user_id is None:
        del os.environ['USER_ID']
      else:
        os.environ['USER_ID'] = default_user_id

    try:
      os.environ['USER_ID'] = ''
      expected_user_id = None
      self.assertEqual(accounts.getCurrentUserId(), expected_user_id)
    finally:
      if default_user_id is None:
        del os.environ['USER_ID']
      else:
        os.environ['USER_ID'] = default_user_id

  def testNormalizeAccount(self):
    """Tests if normalizeAccount normalizes accounts properly.
    """
    #normalize currently logged in user
    account = self.account
    normalized_acc = accounts.normalizeAccount(account)
    expected_email = self.regular_email
    self.assertEqual(normalized_acc.email(), expected_email)

    #normalize a non normal account
    account = users.User(email=self.non_normal_email)
    normalized_acc = accounts.normalizeAccount(account)
    expected_email = self.non_normal_email.lower()
    self.assertEqual(normalized_acc.email(), expected_email)

    #when account is None, e.g. if no user is logged in
    account = None
    self.assertRaises(AttributeError, accounts.normalizeAccount, account)

    #test invalid emails
    account = users.User(email=self.invalid_emails[0])
    normalized_acc = accounts.normalizeAccount(account)
    expected_email = self.invalid_emails[0]
    self.assertEqual(normalized_acc.email(), expected_email)

    account = users.User(email=self.invalid_emails[1])
    normalized_acc = accounts.normalizeAccount(account)
    expected_email = self.invalid_emails[1]
    self.assertEqual(normalized_acc.email(), expected_email)

    account = users.User(email=self.invalid_emails[2])
    normalized_acc = accounts.normalizeAccount(account)
    expected_email = self.invalid_emails[2]
    self.assertEqual(normalized_acc.email(), expected_email)


  def testDenormalizeAccount(self):
    """Tests if accounts are denormalised as expected.
    """
    expected_email = self.regular_email
    denormalized_acc = accounts.denormalizeAccount(self.account)
    self.assertEqual(denormalized_acc.email(), expected_email)

    account = users.User(email='test')
    denormalized_acc = accounts.denormalizeAccount(account)
    self.assertEqual(denormalized_acc.email(), 'test@gmail.com')

    account = users.User(email='test', _auth_domain='example.com')
    denormalized_acc = accounts.denormalizeAccount(account)
    self.assertEqual(denormalized_acc.email(), 'test@example.com')

    account = None
    self.assertRaises(AttributeError, accounts.denormalizeAccount, account)

  def testIsDeveloper(self):
    """Tests if the current user is a developer.
    """
    default_developer_setting = os.environ.get('USER_IS_ADMIN', None)
    default_account_setting = os.environ.get('USER_EMAIL', None)
    #test currently logged in user  
    try:
      os.environ['USER_EMAIL'] = 'test@example.com'
      os.environ['USER_IS_ADMIN'] = '0'
      self.assertFalse(accounts.isDeveloper())
      account = users.User(email=os.environ['USER_EMAIL'])
      self.assertFalse(accounts.isDeveloper(account))
    finally:
      if default_account_setting is None:
        del os.environ['USER_EMAIL']
      else:
        os.environ['USER_EMAIL'] = default_account_setting
      if default_developer_setting is None:
        del os.environ['USER_IS_ADMIN']
      else:
        os.environ['USER_IS_ADMIN'] = default_developer_setting

    #test currently logged in user as a developer  
    try:
      os.environ['USER_EMAIL'] = 'test@example.com'
      os.environ['USER_IS_ADMIN'] = '1'
      self.assertTrue(accounts.isDeveloper())
      account = users.User(email=os.environ['USER_EMAIL'])
      self.assertTrue(accounts.isDeveloper(account))
    finally:
      if default_account_setting is None:
        del os.environ['USER_EMAIL']
      else:
        os.environ['USER_EMAIL'] = default_account_setting
      if default_developer_setting is None:
        del os.environ['USER_IS_ADMIN']
      else:
        os.environ['USER_IS_ADMIN'] = default_developer_setting

    #no currently logged in user and google acc not passed
    try:
      os.environ['USER_EMAIL'] = ''
      os.environ['USER_IS_ADMIN'] = '0'
      self.assertFalse(accounts.isDeveloper())
    finally:
      if default_account_setting is None:
        del os.environ['USER_EMAIL']
      else:
        os.environ['USER_EMAIL'] = default_account_setting
      if default_developer_setting is None:
        del os.environ['USER_IS_ADMIN']
      else:
        os.environ['USER_IS_ADMIN'] = default_developer_setting

    #no user logged in but the environ variable for developer is set to true
    try:
      os.environ['USER_EMAIL'] = ''
      os.environ['USER_IS_ADMIN'] = '1'
      self.assertFalse(accounts.isDeveloper())
    finally:
      os.environ['USER_EMAIL'] = self.account.email()
      if default_account_setting is None:
        del os.environ['USER_EMAIL']
      else:
        os.environ['USER_EMAIL'] = default_account_setting
      if default_developer_setting is None:
        del os.environ['USER_IS_ADMIN']
      else:
        os.environ['USER_IS_ADMIN'] = default_developer_setting

