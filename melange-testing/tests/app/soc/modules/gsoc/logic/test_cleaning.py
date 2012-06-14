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

"""Tests for cleaning methods in GSoC.
"""


import unittest

from django import forms

from soc.modules.gsoc.logic import cleaning

class Form(object):
  """A dummy form class for CleaningTest.
  """
  def __init__(self):
    self.cleaned_data = {}
    self._errors = {}

class CleaningTest(unittest.TestCase):
  """Tests for cleaning methods in GSoC.
  """
  def setUp(self):
    self.form = Form()

  def testCleanTagsList(self):
    """Tests if tags are cleaned and validated.
    """
    field_name = 'tags'
    clean_data = cleaning.cleanTagsList(field_name)

    #Test valid tags.
    field_value = "python\ndjango\ntesting"
    data_to_clean = {field_name: field_value}
    self.form.cleaned_data = data_to_clean
    expected = field_value.split('\n')
    self.assertEqual(clean_data(self.form), expected)

    #Test if extra-whitespace in the tags string are removed.
    field_value = "python  \n  django\n testing"
    data_to_clean = {field_name: field_value}
    self.form.cleaned_data = data_to_clean
    temp = field_value.split('\n')
    expected = [tag.strip() for tag in temp]
    self.assertEqual(clean_data(self.form), expected)

    #Invalid tags.
    field_value = "python\n &%tag \n#^ase"
    data_to_clean = {field_name: field_value}
    self.form.cleaned_data = data_to_clean
    self.assertRaises(forms.ValidationError, clean_data, self.form)

