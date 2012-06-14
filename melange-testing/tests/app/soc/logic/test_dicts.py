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


"""Tests related to soc.logic.dicts.
"""


import unittest

from google.appengine.ext import db

from soc.logic import dicts


class TestDicts(unittest.TestCase):
  """Tests functions in dicts module.
  """
  def setUp(self):
    self.dummy_dict = {'a': '1', 'b': '2', 'c': '3', 'd': '1',
                       'e': '1', 'f': '3', 'g': '7'}

  def testFilterKeysToFilterValid(self):
    """Tests if a dict is filtered correctly if some keys are given.
    """
    keys_to_filter = ['a', 'b', 'c', 'd']
    expected_dict = {'a': '1', 'b': '2', 'c': '3', 'd': '1'}
    self.assertEqual(
        dicts.filter(self.dummy_dict, keys_to_filter), expected_dict)

  def testFilterNoKeysToFilter(self):
    """Tests that nothing is filtered if no keys are given.
    """
    keys_to_filter = []
    expected_dict = {}
    self.assertEqual(
        dicts.filter(self.dummy_dict, keys_to_filter), expected_dict)

  def testFilterKeysToFilterNotInDict(self):
    """Tests that nothing is filtered if keys are not in dict.
    """
    keys_to_filter = ['foo8']
    expected_dict = {}
    self.assertEqual(
        dicts.filter(self.dummy_dict, keys_to_filter), expected_dict)

  def testMergeTargetHasNoKeysInUpdates(self):
    """Tests if a dictionary is updated correctly.
    """
    target = self.dummy_dict
    updates = {'h': '8', 'i': {'a': '3', 'b': '11'}}
    temp = target.copy()
    temp.update(updates)
    expected_dict = temp
    self.assertEqual(dicts.merge(target, updates), expected_dict)

  def testMergeTargetHasAnyKeyInUpdates(self):
    """Tests if a dictionary is updated correctly.
    """
    target = self.dummy_dict
    updates = {'a': '2', 'b': '3', 'c': '4', 'd': '5', 'e': '6', 'f': '7',
               'g': '8', 'h': '9', 'i': {'a': '3', 'b': '11'}}
    temp = target.copy()
    temp_updates = dict((('h', updates['h']), ('i', updates['i'])))
    temp.update(temp_updates)
    expected_dict = temp
    self.assertEqual(dicts.merge(target, updates), expected_dict)

  def testMergeUpdatesEmpty(self):
    """Tests that nothing is updated if no updates.
    """
    target = self.dummy_dict
    updates = {}
    expected_dict = target
    self.assertEqual(dicts.merge(target, updates), expected_dict)

  def testMergeTargetEmptyUpdatesNotEmpty(self):
    """Tests that an empty target is updated.
    """
    target = {}
    updates = {'a': '1'}
    expected = updates
    self.assertEqual(dicts.merge(target, updates), expected)

  def testMergeTargetEmptyUpdatesEmpty(self):
    """Tests that an empty dict is returned when no target and updates.
    """
    target = {}
    updates = {}
    expected_dict = updates
    self.assertEqual(dicts.merge(target, updates), expected_dict)

  def testMergeSubMergeTrueMergeSubDictsPresent(self):
    """Tests if sub-dicts are merged if sub_merge=True.
    """
    #merge sub dict present in both target and updates
    target = self.dummy_dict.copy()
    new_key = 'foo'
    new_value = {'k1': 'v1', 'k2': 'v2'}
    target.update({new_key: new_value })
    updates = {'h': '8', 'foo': {'a': '3', 'b': '11'}}
    temp = self.dummy_dict.copy()
    from copy import deepcopy
    updates_copy = deepcopy(updates)
    temp.update(updates_copy)
    temp[new_key].update(new_value)
    expected_dict = temp
    self.assertEqual(dicts.merge(target, updates, sub_merge=True), expected_dict)

  def testMergeSubMergeTrueSubListsPresent(self):
    """Tests if two lists are merged if sub_merge=True.
    """
    #merge sub lists present in both target and lists
    target = self.dummy_dict.copy()
    target.update({'foo': ['value1', 'value2']})

    updates = {'h': '8', 'foo': ['value3', 'value4']}

    temp = target.copy()
    temp['foo'] = temp['foo'] + updates['foo']
    temp.update(h='8')
    expected_dict = temp
    self.assertEqual(dicts.merge(target, updates, sub_merge=True), expected_dict)

  def testMergeWhenBothSubListsAndDictsArePresent(self):
    """Tests that lists and dicts can not be merged.
    """
    #do not merge lists and dicts and sub_merge is True
    target = self.dummy_dict.copy()
    target.update({'foo': {'alpha': 1, 'beta': 2}})
    updates = {'foo':['gamma', 'delta']}
    expected = target
    self.assertEqual(dicts.merge(target, updates), expected)

    target = self.dummy_dict.copy()
    target.update({'foo':['gamma', 'delta']})
    updates = {'foo': {'alpha': 1, 'beta': 2}}
    expected = target
    self.assertEqual(dicts.merge(target, updates), expected)

  def testMergeSubMergeFalseSubDictsPresent(self):
    """Tests if sub-dicts are not merged if sub_merge=False.
    """
    #merge sub dict present in both target and updates
    target = self.dummy_dict.copy()
    target.update({'foo': {'k1': 'v1', 'k2': 'v2'}})
    updates = {'foo': {'a': '3', 'b': '11'}}
    expected_dict = target
    self.assertEqual(dicts.merge(target, updates, sub_merge=False), expected_dict)

  def testMergeRecursiveFalse(self):
    """Tests if dicts are updated.
    """
    target = {'a':1, 'b': {'c': {"d": { "e": 2}}}}
    updates = {'f': 3, 'b': {'c' :{"d": {"g": 5}}}}

    temp = target.copy()
    temp.update({'f': 3})
    expected = temp
    self.assertEqual(dicts.merge(target, updates,
                                 sub_merge=True, recursive=False), expected)

  def testMergeRecursiveTrue(self):
    """Tests if dicts are updated correctly when recursive is set True.
    """
    target = {'a':1, 'b': {'c': {"d": { "e": 2}}}}
    updates = {'f': 3, 'b': {'c' :{"d": {"g": 5}}}}
    expected = {'a':1, 'f':3, 'b': {'c': {"d": { "e": 2, 'g':5}}}}
    self.assertEqual(dicts.merge(target, updates,
                                 sub_merge=True, recursive=True), expected)

  def testMergeRecursiveTrueSubMergeFalse(self):
    """Tests if dicts are updated correctly when recursive True, sub_merge False.
    """
    target = {'a':1, 'b': {'c': {"d": { "e": 2}}}}
    updates = {'f': 3, 'b': {'c' :{"d": {"g": 5}}}}
    expected = {'a':1, 'f':3, 'b': {'c': {"d": { "e": 2}}}}
    self.assertEqual(dicts.merge(target, updates,
                                 sub_merge=False, recursive=True), expected)

  def testZip(self):
    """Test that keys and values are zipped as desired.
    """
    #equal keys and values
    keys = ['a', 'b', 'c']
    values = ['1', '2', '3']
    expected_dict = dict(zip(keys, values))
    self.assertEqual(dicts.zip(keys, values), expected_dict)

    #extra key
    keys.append('d')
    expected_dict.update({'d': None})
    self.assertEqual(dicts.zip(keys, values), expected_dict)

    #extra values
    values.extend(['4', '5'])
    expected_dict = dict(zip(keys, values))
    self.assertEqual(dicts.zip(keys, values), expected_dict)

  def testUnzip(self):
    """Tests if desired values are unzipped from a dictionary.
    """
    target = self.dummy_dict
    order = ['a', 'b', 'c']
    expected_list = ['1', '2', '3']
    gen = dicts.unzip(target, order)
    result = list(gen)
    self.assertEqual(result, expected_list)

    target = self.dummy_dict
    order = ['x', 'y', 'z']
    expected_list = []
    gen = dicts.unzip(target, order)
    self.assertRaises(KeyError, list, gen)

    order = []
    expected_list = []
    gen = dicts.unzip(target, order)
    result = list(gen)
    self.assertEqual(result, expected_list)


  def testRename(self):
    """Tests that keys in the target dict are renamed with value of the same key
    in another dict.
    """
    target = {'wan': 1, 'too': 2, 'tree': 3}
    keys = {'wan': 'one', 'too': 'two', 'tree': 'three'}
    expected_dict = {'one': 1, 'two': 2, 'three': 3}
    self.assertEqual(dicts.rename(target, keys), expected_dict)

    target = {}
    expected_dict = {}
    self.assertEqual(dicts.rename(target, keys), expected_dict)

    target = {'wan': 1, 'too': 2, 'tree': 3}
    keys = {}
    expected_dict = {}
    self.assertEqual(dicts.rename(target, keys), expected_dict)

    target = {'wan': 1, 'too': 2, 'tree': 3}
    keys = {'for': 4}
    expected_dict = {}
    self.assertEqual(dicts.rename(target, keys), expected_dict)

  def testSplit(self):
    """Tests that a dict is split into single-valued pairs.
    """
    target = {}
    expected = [{}]
    self.assertEqual(dicts.split(target), expected)

    target = {'foo': 'bar'}
    expected = [{'foo': 'bar'}]
    self.assertEqual(dicts.split(target), expected)

    target = {'foo': 'bar', 'bar': 'baz'}
    expected = [{'foo': 'bar', 'bar': 'baz'}]
    self.assertEqual(dicts.split(target), expected)

    target = {'foo': 'bar', 'bar': ['one', 'two']}
    expected = [
        {'foo': 'bar', 'bar': 'one'}, {'foo': 'bar', 'bar': 'two'}]
    self.assertEqual(dicts.split(target), expected)

    target = {'foo': 'bar', 'bar': ['one', 'two'], 'baz': ['three', 'four']}
    expected = [{'bar': 'one', 'foo': 'bar', 'baz': 'three'},
                {'bar': 'two', 'foo': 'bar', 'baz': 'three'},
                {'bar': 'one', 'foo': 'bar', 'baz': 'four'},
                {'bar': 'two', 'foo': 'bar', 'baz': 'four'}]
    self.assertEqual(dicts.split(target), expected)

  def testGroupDictBy(self):
    """Not tested because dicts.groupDictBy is not used in the code base 
    presently.
    """
    pass

  def testIdentity(self):
    """Tests if a dict with values equal to keys is returned
    """
    target = {'wan': 1, 'too': 2, 'tree': 3}
    expected_dict = {'wan': 'wan' , 'too': 'too', 'tree': 'tree'}
    self.assertEqual(dicts.identity(target), expected_dict)

    target = {}
    expected_dict = {}
    self.assertEqual(dicts.identity(target), expected_dict)

  def testFormat(self):
    """Not tested because dicts.format is not used in the code base presently.
    """
    pass

  def testGroupby(self):
    """Tests if a list of dictionaries is grouped by a group_key.
    """
    target = [{'a':1, 'b': 2}, {'a':3, 'b': 4}, {'a':1, 'c': 4}]

    group_key = 'a'
    expected = {1: [{'a':1, 'b': 2}, {'a':1, 'c': 4}], 3: [{'a':3, 'b': 4}]}
    self.assertEqual(dicts.groupby(target, group_key), expected)

    group_key = ''
    expected = {}
    self.assertRaises(KeyError, dicts.groupby, target, group_key)

    group_key = 'f'
    self.assertRaises(KeyError, dicts.groupby, target, group_key)

    target = []
    group_key = ''
    expected = {}
    self.assertEqual(dicts.groupby(target, group_key), expected)

    target = []
    group_key = 'a'
    expected = {}
    self.assertEqual(dicts.groupby(target, group_key), expected)

  def testContainsAll(self):
    """Tests if a correct boolean value is returned.
    """
    target = {'wan': 1, 'too': 2, 'tree': 3}
    keys = ['wan', 'too']
    self.assertTrue(dicts.containsAll(target, keys))

    keys = ['wan', 'fore']
    self.assertFalse(dicts.containsAll(target, keys))

    keys = []
    self.assertTrue(dicts.containsAll(target, keys))

  def testToDict(self):
    """Tests if a dict with desired entity properties is returned.
    """
    class Books(db.Model):
      item_freq = db.StringProperty()
      freq = db.IntegerProperty()
      details = db.TextProperty()
      released = bool

    entity = Books()
    entity.item_freq = '5'
    entity.freq = 4
    entity.details = 'Test Entity'
    entity.released = True
    entity.put()

    expected_dict = {'freq': 4, 'item_freq': '5'}
    self.assertEqual(dicts.toDict(entity), expected_dict)

    field_names = ['item_freq', 'details', 'released']
    expected_dict = {'released': True,
                     'details': 'Test Entity',
                     'item_freq': '5'}
    self.assertEqual(dicts.toDict(entity, field_names), expected_dict)

    field_names = []
    expected_dict = {'freq': 4, 'item_freq': '5'}
    self.assertEqual(dicts.toDict(entity, field_names), expected_dict)

    #field names not in the entity
    field_names = ['other_data']
    expected_dict = {}
    self.assertEqual(dicts.toDict(entity, field_names), expected_dict)

  def testCleanDict(self):
    """Tests  if the fields in the dict is HTML escaped as desired.
    """
    target = {
        'name': 'test', 'param1':'>1000', 'param2':'<1000', 'param3': 'a&b'}
    filter_fields = ['param1', 'param2', 'param3']
    expected_dict = {
        'param3': u'a&amp;b', 'name': 'test', 'param1': u'&gt;1000',
        'param2': u'&lt;1000'
    }
    self.assertEqual(dicts.cleanDict(target, filter_fields), expected_dict)

    filter_fields = []
    expected_dict = {'param3': 'a&b', 'name': 'test', 'param1': '>1000',
                     'param2': '<1000'}
    self.assertEqual(dicts.cleanDict(target, filter_fields), expected_dict)

    #parameter not present in target
    filter_fields = ['other_param']
    self.assertRaises(KeyError, dicts.cleanDict, target, filter_fields)

    from django.utils.safestring import mark_safe
    target['param1'] = mark_safe(target['param1'])
    expected_dict = {
        'param3': u'a&amp;b', 'name': 'test', 'param1': '>1000',
        'param2': u'&lt;1000'}
    filter_fields = ['param1', 'param2', 'param3']
    self.assertEqual(dicts.cleanDict(target, filter_fields), expected_dict)

    expected_dict = {
        'param3': u'a&amp;b', 'name': 'test', 'param1': u'&gt;1000',
        'param2': u'&lt;1000'}
    self.assertEqual(
        dicts.cleanDict(target, filter_fields, escape_safe=True), expected_dict)

