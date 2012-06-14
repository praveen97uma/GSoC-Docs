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


"""Tests for app.soc.logic.system
"""


import os
import unittest

from soc.logic import system
from soc.models import site
from soc.views.helper.request_data import RequestData


class SystemTest(unittest.TestCase):
  """Tests for basic system information functions.
  """
  def setUp(self):
    self.default_host = os.environ.get('HTTP_HOST', None)
    self.default_application_id = os.environ.get('APPLICATION_ID', None)
    self.default_current_version_id = os.environ.get('CURRENT_VERSION_ID', None)

  def testGetApplicationId(self):
    """Tests that a correct application id is returned.
    """
    try:
      expected_id = os.environ['APPLICATION_ID'] = 'test-app-run'
      self.assertEqual(system.getApplicationId(), expected_id)
    finally:
      if self.default_application_id is None:
        del os.environ['APPLICATION_ID']
      else:
        os.environ['APPLICATION_ID'] = self.default_application_id

    try:
      expected_id = os.environ['APPLICATION_ID'] = ''
      self.assertEqual(system.getApplicationId(), expected_id)
    finally:
      if self.default_application_id is None:
        del os.environ['APPLICATION_ID']
      else:
        os.environ['APPLICATION_ID'] = self.default_application_id

  def testGetApplicationEmail(self):
    """Tests that a correct application email is returned.
    """

    try:
      os.environ['APPLICATION_ID'] = 'test-app-run'
      expected_email = "simple-test@test-app-run.appspotmail.com"
      self.assertEqual(system.getApplicationEmail('simple-test'), expected_email)
    finally:
      if self.default_application_id is None:
        del os.environ['APPLICATION_ID']
      else:
        os.environ['APPLICATION_ID'] = self.default_application_id

    #Check if an exception is raised if no app-id is set
    try:
      os.environ['APPLICATION_ID'] = ''
      self.assertRaises(AssertionError, system.getApplicationEmail, 'test')
    finally:
      if self.default_application_id is None:
        del os.environ['APPLICATION_ID']
      else:
        os.environ['APPLICATION_ID'] = self.default_application_id

    #Check if an exception is raised when no argument passed  
    self.assertRaises(TypeError, system.getApplicationEmail,)

  def testGetApplicationNoReplyEmail(self):
    """Tests that a correct no-reply email is returned.
    """
    if self.default_application_id is None:
      let_current_app_id = 'test-app-run'
      try:
        os.environ['APPLICATION_ID'] = let_current_app_id
        expected = "no-reply@%s.appspotmail.com" % let_current_app_id
        self.assertEqual(system.getApplicationNoReplyEmail(), expected)
      finally:
        del os.environ['APPILICATION_ID']
    else:
      current_app_id = os.environ['APPLICATION_ID']
      expected = "no-reply@%s.appspotmail.com" % current_app_id
      self.assertEqual(system.getApplicationNoReplyEmail(), expected)

  def testGetRawHostName(self):
    """Tests that a correct raw host name is returned.
    """
    try:
      host = os.environ['HTTP_HOST'] = 'some.testing.host.tld'
      expected_current_host = host
      self.assertEqual(system.getRawHostname(), expected_current_host)
    finally:
      if self.default_host is None:
        del os.environ['HTTP_HOST']
      else:
        os.environ['HTTP_HOST'] = self.default_host

    try:
      expected_host = os.environ['HTTP_HOST'] = ''
      self.assertEqual(system.getRawHostname(), expected_host)
    finally:
      if self.default_host is None:
        del os.environ['HTTP_HOST']
      else:
        os.environ['HTTP_HOST'] = self.default_host

  def testGetHostName(self):
    """Tests that a correct host name is returned.
    """
    test_data = RequestData()
    test_site = site.Site(link_id='test', hostname='test_host')
    test_data.site = test_site

    try:
      expected_host = os.environ['HTTP_HOST'] = 'some.testing.host.tld'
      self.assertEqual(system.getHostname(), expected_host)
    finally:
      if self.default_host is None:
        del os.environ['HTTP_HOST']
      else:
        os.environ['HTTP_HOST'] = self.default_host

    #test a data object    
    expected_host = 'test_host'
    self.assertEqual(system.getHostname(data=test_data), expected_host)

    test_data.site.hostname = ''
    try:
      expected_host = os.environ['HTTP_HOST'] = 'some.testing.host.tld'
      self.assertEqual(system.getHostname(data=test_data), expected_host)
    finally:
      if self.default_host is None:
        del os.environ['HTTP_HOST']
      else:
        os.environ['HTTP_HOST'] = self.default_host

  def testGetSecureHostName(self):
    """Tests that a hostname suitable for https requests is returned.
    """
    try:
      os.environ['APPLICATION_ID'] = 'test-app-run'
      expected_host = 'test-app-run.appspot.com'
      self.assertEqual(system.getSecureHostname(), expected_host)
    finally:
      if self.default_application_id is None:
        del os.environ['APPLICATION_ID']
      else:
        os.environ['APPLICATION_ID'] = self.default_application_id

  def testIsSecondaryHostName(self):
    """Tests if a request is from a secondary hostname.
    """
    test_data = RequestData()
    test_site = site.Site(link_id='test', hostname='test_host')
    test_data.site = test_site

    try:
      os.environ['HTTP_HOST'] = 'some.testing.host.tld'
      self.assertFalse(system.isSecondaryHostname())
  
      self.assertFalse(system.isSecondaryHostname(data=test_data))
  
      test_data.site.hostname = "testing"
      self.assertTrue(system.isSecondaryHostname(data=test_data))
    finally:
      if self.default_host is None:
        del os.environ['HTTP_HOST']
      else:
        os.environ['HTTP_HOST'] = self.default_host

  def testGetAppVersion(self):
    """Tests if a google-app-version is returned.
    """
    try:
      expected_version = os.environ['CURRENT_VERSION_ID'] = 'testing-version'
      self.assertEqual(system.getAppVersion(), expected_version)
    finally:
      if self.default_current_version_id is None:
        del os.environ['CURRENT_VERSION_ID']
      else:
        os.environ['CURRENT_VERSION_ID'] = self.default_current_version_id

  def testGetMelangeVersion(self):
    """Tests if the Melange part of GAE version is returned.
    """
    try:
      expected_version = os.environ['CURRENT_VERSION_ID'] = 'testing-version'
      self.assertEqual(system.getMelangeVersion(), expected_version)
    finally:
      if self.default_current_version_id is None:
        del os.environ['CURRENT_VERSION_ID']
      else:
        os.environ['CURRENT_VERSION_ID'] = self.default_current_version_id

    try:
      os.environ['CURRENT_VERSION_ID'] = 'melange_version.testing'
      expected_version = 'melange_version'
      self.assertEqual(system.getMelangeVersion(), expected_version)
    finally:
      if self.default_current_version_id is None:
        del os.environ['CURRENT_VERSION_ID']
      else:
        os.environ['CURRENT_VERSION_ID'] = self.default_current_version_id

    try:
      expected_version = os.environ['CURRENT_VERSION_ID'] = ''
      self.assertEqual(system.getMelangeVersion(), expected_version)
    finally:
      if self.default_current_version_id is None:
        del os.environ['CURRENT_VERSION_ID']
      else:
        os.environ['CURRENT_VERSION_ID'] = self.default_current_version_id

  def testIsLocal(self):
    """Tests if the current Melange application is running locally.
    """
    self.assertTrue(system.isLocal())

  def testIsDebug(self):
    """Tests if Melange is running in debug mode.
    """
    self.assertTrue(system.isDebug())

    try:
      os.environ['CURRENT_VERSION_ID'] = 'devvin.testing-version'
      self.assertTrue(system.isDebug())
    finally:
      if self.default_current_version_id is None:
        del os.environ['CURRENT_VERSION_ID']
      else:
        os.environ['CURRENT_VERSION_ID'] = self.default_current_version_id

    try:
      os.environ['CURRENT_VERSION_ID'] = 'nondevvin.testing-version'
      self.assertTrue(system.isDebug())
    finally:
      if self.default_current_version_id is None:
        del os.environ['CURRENT_VERSION_ID']
      else:
        os.environ['CURRENT_VERSION_ID'] = self.default_current_version_id

