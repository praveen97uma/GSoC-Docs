#!/usr/bin/env python2.5
#
# Copyright 2008 the Melange authors.
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
"""Common testing utilities.
"""


import collections
import hashlib
import os
import datetime
import httplib
import StringIO
import unittest

import gaetestbed
from mox import stubout

from google.appengine.ext import db

from django.test import client
from django.test import TestCase

from soc.logic.helper import xsrfutil
from soc.middleware.xsrf import XsrfMiddleware
from soc.modules import callback


class MockRequest(object):
  """Shared dummy request object to mock common aspects of a request.

  Before using the object, start should be called, when done (and
  before calling start on a new request), end should be called.
  """

  def __init__(self, path=None, method='GET'):
    """Creates a new empty request object.

    self.REQUEST, self.GET and self.POST are set to an empty
    dictionary, and path to the value specified.
    """

    self.REQUEST = {}
    self.GET = {}
    self.POST = {}
    self.META = {}
    self.path = path
    self.method = method

  def get_full_path(self):
    # TODO: if needed add GET params
    return self.path

  def start(self):
    """Readies the core for a new request.
    """

    core = callback.getCore()
    core.startNewRequest(self)

  def end(self):
    """Finishes up the current request.
    """

    core = callback.getCore()
    core.endRequest(self, False)


def get_general_raw(args_names):
  """Gets a general_raw function object.
  """

  def general_raw(*args, **kwargs):
    """Sends a raw information.

    That is the parameters passed to the return function that is mentioned
    in corresponding stubout.Set
    """

    num_args = len(args)
    result = kwargs.copy()
    for i, name in enumerate(args_names):
      if i < num_args:
        result[name] = args[i]
      else:
        result[name] = None
    if len(args_names) < num_args:
      result['__args__'] = args[num_args:]
    return result
  return general_raw


class StuboutHelper(object):
  """Utilities for view test.
  """

  def __init__(self):
    """Creates a new ViewTest object.
    """

    #Creates a StubOutForTesting object
    self.stubout = stubout.StubOutForTesting()

  def tearDown(self):
    """Tear down the stubs that were set up.
    """

    self.stubout.UnsetAll()

  def stuboutBase(self):
    """Applies basic stubout replacements.
    """
    pass

  def stuboutElement(self, parent, child_name, args_names):
    """Applies a specific stubout replacement.

    Replaces child_name's old definition with the new definition which has
    a list of arguments (args_names), in the context of the given parent.
    """

    self.stubout.Set(parent, child_name, get_general_raw(args_names))


class NonFailingFakePayload(object):
  """Extension of Django FakePayload class that includes seek and readline
  methods.
  """

  def __init__(self, content):
    self.__content = StringIO.StringIO(content)
    self.__len = len(content)

  def read(self, num_bytes=None):
    if num_bytes is None:
        num_bytes = self.__len or 1
    assert self.__len >= num_bytes, \
      "Cannot read more than the available bytes from the HTTP incoming data."
    content = self.__content.read(num_bytes)
    self.__len -= num_bytes
    return content

  def seek(self, pos, mode=0):
    return self.__content.seek(pos, mode)
  
  def readline(self, length=None):
    return self.__content.readline(length)


class SoCTestCase(unittest.TestCase):
  """Base test case to be subclassed.

  Common data are seeded and common helpers are created to make testing easier.
  """
  def init(self):
    """Performs test setup.

    Sets the following attributes:
      dev_test: True iff DEV_TEST is in environment (in parent)
    """
    self.dev_test = 'DEV_TEST' in os.environ

  def assertItemsEqual(self, expected_seq, actual_seq, msg=''):
    """An unordered sequence / set specific comparison.

    It asserts that expected_seq and actual_seq contain the same elements.
    This method is heavily borrowed from Python 2.7 unittest
    library (since Melange uses Python 2.5 for deployment):
    http://svn.python.org/view/python/tags/r271/Lib/unittest/case.py?view=markup#l844
    """

    try:
      actual = collections.Counter(iter(actual_seq))
      expected = collections.Counter(iter(expected_seq))
      missing = list(expected - actual)
      unexpected = list(actual - expected)
    except TypeError:
      # Unsortable items (example: set(), complex(), ...)
      missing = []

      actual = list(actual_seq)
      expected = list(expected_seq)
      while expected:
        item = expected.pop()
        try:
          actual.remove(item)
        except ValueError:
          missing.append(item)
      #anything left in expected is unexpected
      unexpected = expected

    errors = []
    if missing:
      errors.append('Expected, but missing: %s' % str(missing))
    if unexpected:
      errors.append('Unexpected, but present: %s' % str(unexpected))

    if errors:
      if msg:
        errors = [msg] + errors
      error_message = '\n'.join(errors)
      self.fail(error_message)


class GSoCTestCase(SoCTestCase):
  """GSoCTestCase for GSoC tests.

  Common data are seeded and common helpers are created to make testing easier.
  """
  def init(self):
    """Performs test setup.

    Sets the following attributes:
      program_helper: a GSoCProgramHelper instance
      gsoc/program: a GSoCProgram instance
      site: a Site instance
      org: a GSoCOrganization instance
      org_app: a OrgAppSurvey instance
      timeline: a GSoCTimelineHelper instance
      data: a GSoCProfileHelper instance
    """
    from tests.program_utils import GSoCProgramHelper
    from tests.timeline_utils import GSoCTimelineHelper
    from tests.profile_utils import GSoCProfileHelper
    super(GSoCTestCase, self).init()
    self.program_helper = GSoCProgramHelper()
    self.founder = self.program_helper.createFounder()
    self.sponsor = self.program_helper.createSponsor()
    self.gsoc = self.program = self.program_helper.createProgram()
    self.site = self.program_helper.createSite()
    self.org = self.program_helper.createOrg()
    self.org_app = self.program_helper.createOrgApp()
    self.timeline = GSoCTimelineHelper(self.gsoc.timeline, self.org_app)
    self.data = GSoCProfileHelper(self.gsoc, self.dev_test)


class GCITestCase(SoCTestCase):
  """GCITestCase for GCI tests.

  Common data are seeded and common helpers are created to make testing easier.
  """
  def init(self):
    """Performs test setup.

    Sets the following attributes:
      program_helper: a GCIProgramHelper instance
      gci/program: a GCIProgram instance
      site: a Site instance
      org: a GCIOrganization instance
      org_app: a OrgAppSurvey instance
      timeline: a GCITimelineHelper instance
      data: a GCIProfileHelper instance
    """
    from tests.program_utils import GCIProgramHelper
    from tests.timeline_utils import GCITimelineHelper
    from tests.profile_utils import GCIProfileHelper
    super(GCITestCase, self).init()
    self.program_helper = GCIProgramHelper()
    self.founder = self.program_helper.createFounder()
    self.sponsor = self.program_helper.createSponsor()
    self.gci = self.program = self.program_helper.createProgram()
    self.site = self.program_helper.createSite()
    self.org = self.program_helper.createOrg()
    self.org_app = self.program_helper.createOrgApp()
    self.timeline = GCITimelineHelper(self.gci.timeline, self.org_app)
    self.data = GCIProfileHelper(self.gci, self.dev_test)


class DjangoTestCase(TestCase):
  """Class extending Django TestCase in order to extend its functions.

  As well as remove the functions which are not supported by Google App Engine,
  e.g. database flush and fixtures loading without the assistance of Google
  App Engine Helper for Django.
  """

  _request_id = 0

  def _pre_setup(self):
    """Performs any pre-test setup.
    """
    client.FakePayload = NonFailingFakePayload

  def _post_teardown(self):
    """ Performs any post-test cleanup.
    """
    os.environ['USER_EMAIL'] = 'test@example.com'
    os.environ['USER_ID'] = '42'

  def createOrg(self, override={}):
    """Creates an organization for the defined properties.
    """
    pass

  def seed(self, model, properties):
    """Returns a instance of model, seeded with properties.
    """
    from soc.modules.seeder.logic.seeder import logic as seeder_logic
    return seeder_logic.seed(model, properties, recurse=False)

  def seedProperties(self, model, properties):
    """Returns seeded properties for the specified model.
    """
    from soc.modules.seeder.logic.seeder import logic as seeder_logic
    return seeder_logic.seed_properties(model, properties, recurse=False)

  def gen_request_id(self):
    """Generate a request id.
    """
    os.environ['REQUEST_ID_HASH'] = hashlib.sha1(str(
        DjangoTestCase._request_id)).hexdigest()[:8].upper()
    DjangoTestCase._request_id += 1

  def get(self, url):
    """Performs a get to the specified url.
    """
    self.gen_request_id()
    response = self.client.get(url)
    return response

  def post(self, url, postdata={}):
    """Performs a post to the specified url with postdata.

    Takes care of setting the xsrf_token.
    """
    self.gen_request_id()
    postdata['xsrf_token'] = self.getXsrfToken(url, site=self.site)
    response = self.client.post(url, postdata)
    postdata.pop('xsrf_token')
    return response

  def modelPost(self, url, model, properties):
    """Performs a post to the specified url after seeding for model.

    Calls post().
    """
    properties = self.seedProperties(model, properties)
    response = self.post(url, properties)
    return response, properties

  def buttonPost(self, url, button_name, postdata=None):
    """Performs a post to url simulating that button_name is clicked.

    Calls post().
    """
    combined_postdata = {button_name: ''}
    if postdata:
      combined_postdata.update(postdata)
    url = '%s?button' % url
    response = self.post(url, combined_postdata)
    return response

  def createDocumentForPrefix(self, prefix, override={}):
    """Creates a document for the specified properties.
    """
    from soc.models.document import Document
    from soc.modules.seeder.logic.providers.string import (
        DocumentKeyNameProvider)
    properties = {
        'modified_by': self.data.user,
        'author': self.data.user,
        'home_for': None,
        'prefix': prefix,
        'scope': self.program,
        'read_access': 'public',
        'key_name': DocumentKeyNameProvider(),
    }
    properties.update(override)
    return self.seed(Document, properties)

  @classmethod
  def getXsrfToken(cls, path=None, method='POST', data={}, site=None, **extra):
    """Returns an XSRF token for request context.

    It is signed by Melange XSRF middleware.
    Add this token to POST data in order to pass the validation check of
    Melange XSRF middleware for HTTP POST.
    """

    """
    request = HttpRequest()
    request.path = path
    request.method = method
    """
    # request is currently not used in _getSecretKey
    class SiteContainingRequest(object):
      def __init__(self, site):
        if site:
          self.site = site
    request = SiteContainingRequest(site)
    xsrf = XsrfMiddleware()
    key = xsrf._getSecretKey(request)
    user_id = xsrfutil._getCurrentUserId()
    xsrf_token = xsrfutil._generateToken(key, user_id)
    return xsrf_token

  def getJsonResponse(self, url):
    """Returns the list reponse for the specified url and index.
    """
    return self.client.get(url + '?fmt=json&marker=1')

  def getListResponse(self, url, idx, start=None, limit=None):
    """Returns the list reponse for the specified url and index.
    """
    url = [url,'?fmt=json&marker=1&&idx=', str(idx)]
    if limit:
      url += ["&limit=", str(limit)]
    if start:
      url += ['&start=', start]
    return self.client.get(''.join(url))

  def getListData(self, url, idx):
    """Returns all data from a list view.
    """
    result = []
    start = ''

    i = 0

    while start != 'done':
      i += 1
      response = self.getListResponse(url, idx, start, 1000)
      data = response.context['data'][start]
      self.assertIsJsonResponse(response)
      result += data
      start = response.context['next']

    return result

  def assertRenderAll(self, response):
    """Calls render on all objects that are renderable.
    """
    for contexts in response.context or []:
      for context in contexts:
        values = context.values() if isinstance(context, dict) else [context]
        for value in values:
          try:
            iterable = iter(value)
          except TypeError:
            iterable = [value]
          for i in iterable:
            # make it easier to debug render failures
            if hasattr(i, 'render'):
              i.render()

  def assertErrorTemplatesUsed(self, response):
    """Assert that all the error templates were used.
    """
    self.assertNotEqual(response.status_code, httplib.OK)
    # TODO(SRabbelier): update this when we use an error template again
    # self.assertTemplateUsed(response, 'soc/error.html')

  def assertResponseCode(self, response, status_code):
    """Asserts that the response status is status_code.
    """
    # first ensure that no render failures occured
    self.assertRenderAll(response)

    if response.status_code != status_code:
      verbose_codes = [
          httplib.FOUND,
      ]
      message_codes = [
          httplib.FORBIDDEN, httplib.BAD_REQUEST, httplib.NOT_FOUND,
      ]
      url_codes = [httplib.NOT_FOUND]

      if response.status_code in verbose_codes:
        print response

      if response.context and response.status_code in message_codes:
        try:
          print response.context['message']
        except KeyError:
          pass

      if response.status_code in url_codes:
        print response.request['PATH_INFO']

    self.assertEqual(status_code, response.status_code)

  def assertResponseOK(self, response):
    """Asserts that the response status is OK.
    """
    self.assertResponseCode(response, httplib.OK)

  def assertResponseRedirect(self, response, url=None):
    """Asserts that the response status is FOUND.
    """
    self.assertResponseCode(response, httplib.FOUND)
    if url:
      url = "http://testserver" + url
      self.assertEqual(url, response["Location"])

  def assertResponseForbidden(self, response):
    """Asserts that the response status is FORBIDDEN.

    Does not raise an error if dev_test is set.
    """
    if self.dev_test:
      return
    self.assertResponseCode(response, httplib.FORBIDDEN)

  def assertResponseBadRequest(self, response):
    """Asserts that the response status is BAD_REQUEST.
    """
    self.assertResponseCode(response, httplib.BAD_REQUEST)

  def assertResponseNotFound(self, response):
    """Asserts that the response status is NOT_FOUND.
    """

    self.assertResponseCode(response, httplib.NOT_FOUND)

  def assertIsJsonResponse(self, response):
    """Asserts that all the templates from the base view were used.
    """
    self.assertResponseOK(response)
    self.assertEqual('application/json', response['Content-Type'])
    self.assertTemplateUsed(response, 'json_marker.html')

  def assertPropertiesEqual(self, properties, entity):
    """Asserts that all properties are set on the specified entity.

    Reference properties are compared by their key.
    Any date/time objects are ignored.
    """
    errors = []

    for key, value in properties.iteritems():
      if key == 'key_name':
        prop = entity.key().name()
      elif key == 'parent':
        prop = entity.parent()
      else:
        prop = getattr(entity, key)

      if isinstance(value, db.Model) or isinstance(prop, db.Model):
        value = repr(value.key()) if value else value
        prop = repr(prop.key()) if prop else prop

      if isinstance(value, datetime.date) or isinstance(value, datetime.time):
        continue

      msg = "property %s: '%r' != '%r'" % (key, value, prop)

      try:
        self.assertEqual(value, prop, msg=msg)
      except AssertionError, e:
        errors.append(msg)

    if errors:
      self.fail("\n".join(errors))


class GSoCDjangoTestCase(DjangoTestCase, GSoCTestCase):
  """DjangoTestCase specifically for GSoC view tests.
  """

  def init(self):
    """Performs test setup.
    """
    # Initialize instances in the parent first
    super(GSoCDjangoTestCase, self).init()

  def createOrg(self, override={}):
    """Creates an organization for the defined properties.
    """
    from soc.modules.gsoc.models.organization import GSoCOrganization

    properties = {'scope': self.gsoc, 'status': 'active',
                  'scoring_disabled': False, 'max_score': 5,
                  'founder': self.founder,
                  'home': None,}
    properties.update(override)
    return self.seed(GSoCOrganization, properties)

  def createDocument(self, override={}):
    return self.createDocumentForPrefix('gsoc_program', override)

  def assertGSoCTemplatesUsed(self, response):
    """Asserts that all the templates from the base view were used.
    """
    self.assertResponseOK(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/footer.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/header.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/mainmenu.html')

  def assertGSoCColorboxTemplatesUsed(self, response):
    """Asserts that all the templates from the base_colorbox view were used.
    """
    self.assertResponseOK(response)
    for contexts in response.context:
      for context in contexts:
        for value in context.values():
          # make it easier to debug render failures
          if hasattr(value, 'render'):
            value.render()
    self.assertTemplateUsed(response, 'v2/modules/gsoc/base_colorbox.html')


class GCIDjangoTestCase(DjangoTestCase, GCITestCase):
  """DjangoTestCase specifically for GCI view tests.
  """

  def init(self):
    """Performs test setup.
    """
    # Initialize instances in the parent first
    super(GCIDjangoTestCase, self).init()

  def assertGCITemplatesUsed(self, response):
    """Asserts that all the templates from the base view were used.
    """
    self.assertResponseOK(response)
    for contexts in response.context:
      for context in contexts:
        for value in context.values():
          # make it easier to debug render failures
          if hasattr(value, 'render'):
            value.render()
    self.assertTemplateUsed(response, 'v2/modules/gci/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gci/_footer.html')
    self.assertTemplateUsed(response, 'v2/modules/gci/_header.html')
    self.assertTemplateUsed(response, 'v2/modules/gci/_mainmenu.html')

  def createDocument(self, override={}):
    return self.createDocumentForPrefix('gci_program', override)


def runTasks(url = None, name=None, queue_names = None):
  """Run tasks with specified url and name in specified task queues.
  """

  task_queue_test_case = gaetestbed.taskqueue.TaskQueueTestCase()
  # Get all tasks with specified url and name in specified task queues
  tasks = task_queue_test_case.get_tasks(url=url, name=name, 
                                         queue_names=queue_names)
  for task in tasks:
    postdata = task['params']
    xsrf_token = GSoCDjangoTestCase.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    client.FakePayload = NonFailingFakePayload
    c = client.Client()
    # Run the task with Django test client
    c.post(url, postdata)


class MailTestCase(gaetestbed.mail.MailTestCase, unittest.TestCase):
  """Class extending gaetestbed.mail.MailTestCase to extend its functions.

  Difference:
  * Subclass unittest.TestCase so that all its subclasses need not subclass
  unittest.TestCase in their code.
  * Override assertEmailSent method.
  """

  def setUp(self):
    """Sets up gaetestbed.mail.MailTestCase.
    """

    super(MailTestCase, self).setUp()

  def get_sent_messages(self, to=None, cc=None, bcc=None, sender=None,
                        subject=None, body=None, html=None):
    """Override gaetestbed.mail.MailTestCase.get_sent_messages method.

    Difference:
    * It checks cc and bcc as well.
    """
    messages = super(MailTestCase, self).get_sent_messages(to, sender, subject,
                                                           body, html)
    if cc:
      messages = [m for m in messages if cc in m.cc_list()]
    if bcc:
      messages = [m for m in messages if bcc in m.bcc_list()]
    return messages

  def assertEmailSent(self, to=None, cc=None, bcc=None, sender=None,
      subject=None, body=None, html=None, n=None, fullbody=False):
    """Override gaetestbed.mail.MailTestCase.assertEmailSent method.

    Difference:
    * It runs all mail tasks first.
    * It prints out all sent messages to facilitate debug in case of failure.
    * It accepts an optional argument n which is used to assert exactly n
    messages satisfying the criteria are sent out.
    * Clips textbody to the first 50 characters, unless fullbody is True.
    """

    # Run all mail tasks first so that all mails will be sent out
    runTasks(url = '/tasks/mail/send_mail', queue_names = ['mail'])
    messages = self.get_sent_messages(
        to = to,
        cc = cc,
        bcc = bcc,
        sender = sender,
        subject = subject,
        body = body,
        html = html,
    )
    failed = False
    if not messages:
      failed = True
      failure_message = "Expected e-mail message sent. No messages sent"
      details = self._get_email_detail_string(to, sender, subject, body, html)
      if details:
        failure_message += ' with %s.' % details
      else:
        failure_message += '.'
    elif n:
      actual_n = len(messages)
      if n != actual_n:
        failed = True
        failure_message = ("Expected e-mail message sent."
                           "Expected %d messages sent" % n)
        details = self._get_email_detail_string(to, sender, subject, body, html)
        if details:
          failure_message += ' with %s;' % details
        else:
          failure_message += ';'
        failure_message += ' but actually %d.' % actual_n
    # If failed, raise error and display all messages sent
    if failed:
      all_messages = self.get_sent_messages()
      failure_message += '\nAll messages sent: '
      if all_messages:
        failure_message += '\n'
        for message in all_messages:
          if not fullbody:
            message.set_textbody(message.textbody()[:50])
            message.set_htmlbody(message.htmlbody()[:50])
          failure_message += str(message)
      else:
        failure_message += 'None'
      self.fail(failure_message)


class TaskQueueTestCase(gaetestbed.taskqueue.TaskQueueTestCase,
                        unittest.TestCase):
  """Class extending gaetestbed.taskqueue.TaskQueueTestCase.

  Difference:
  * Subclass unittest.TestCase so that all its subclasses need not subclass
  unittest.TestCase in their code.
  """

  def setUp(self):
    """Sets up gaetestbed.taskqueue.TaskQueueTestCase.
    """

    super(TaskQueueTestCase, self).setUp()
