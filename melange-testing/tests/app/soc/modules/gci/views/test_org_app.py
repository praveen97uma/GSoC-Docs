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


"""Tests for organization applications.
"""


from datetime import datetime
from datetime import timedelta

from google.appengine.ext import db

from django.utils import simplejson

from soc.models.org_app_survey import OrgAppSurvey
from soc.models.org_app_record import OrgAppRecord

from soc.modules.seeder.logic.seeder import logic as seeder_logic

from tests.test_utils import GCIDjangoTestCase
from tests.test_utils import MailTestCase
from tests.survey_utils import SurveyHelper
from tests.profile_utils import GCIProfileHelper


class GCIOrgAppEditPageTest(GCIDjangoTestCase):
  """Tests for organization applications edit page.
  """

  def setUp(self):
    self.init()
    self.url = '/gci/org/application/edit/%s' % self.gci.key().name()
    self.post_params = {
        'title': 'Test Title',
        'short_name': 'Test Short Name',
        'content': 'Test Content',
        'survey_start': '2011-10-13 00:00:00',
        'survey_finish': '2011-10-13 00:00:00',
        'schema': 'Test Scheme',
    }

  def assertTemplatesUsed(self, response):
    """Asserts all the templates for edit page were used.
    """

    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/org_app/edit.html')
    self.assertTemplateUsed(response, 'v2/modules/gci/_form.html')

  def testAccessCheck(self):
    """Asserts only the host can access the page.
    """

    response = self.get(self.url)
    self.assertResponseForbidden(response)

    response = self.post(self.url, self.post_params)
    self.assertResponseForbidden(response)

    self.data.createHost()

    response = self.get(self.url)
    self.assertResponseOK(response)

  def testEditPage(self):
    """Tests organization applications edit page.
    """

    self.data.createHost()
    response = self.get(self.url)
    self.assertTemplatesUsed(response)

    response = self.post(self.url, self.post_params)
    self.assertResponseRedirect(response, '%s?validated' % self.url)

    query = OrgAppSurvey.all().filter('program = ', self.gci)
    self.assertEqual(query.count(), 1,
                     ('There must be one and only one OrgAppSurvey '
                      'instance for the program.'))

    survey = query.get()
    self.assertEqual(survey.title, self.post_params['title'])
    self.assertEqual(survey.modified_by.key(), self.data.user.key())


class GCIOrgAppTakePageTest(GCIDjangoTestCase):
  """Tests for organizations to submit and edit their application.
  """

  def setUp(self):
    self.init()

    self.take_url = '/gci/org/application/%s' % self.gci.key().name()
    self.retake_url_raw = '/gci/org/application/%s/%s'

    self.post_params = {
      'org_id': 'melange',
      'name': 'Melange',
      'description': 'Melange',
      'home_page': 'code.google.com/p/soc',
      'license': 'Apache License, 2.0',
      'agreed_to_admin_agreement': 'on',
      'item': 'test',
    }

  def assertTemplatesUsed(self, response):
    """Asserts all the templates for edit page were used.
    """

    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gci/org_app/take.html')

  def updateOrgAppSurvey(self, survey_start=None, survey_end=None):
    """Create an organization application survey.
    """

    if survey_start is None:
      survey_start = datetime.now()

    if survey_end is None:
      survey_end = survey_start + timedelta(days=10)

    self.org_app.survey_start = survey_start
    self.org_app.survey_end = survey_end
    self.org_app.put()

  def testAccessCheckWithoutSurvey(self):
    self.org_app.delete()

    response = self.get(self.take_url)
    self.assertResponseNotFound(response)

    self.data.createOrgAdmin(self.org)
    response = self.get(self.take_url)
    self.assertResponseNotFound(response)

  def testAccessCheckForNonOrgMembers(self):
    self.updateOrgAppSurvey()

    #Check for non-org members
    self.data.createStudent()
    response = self.get(self.take_url)
    self.assertResponseForbidden(response)
    self.data.removeStudent()

  def testAccessCheckForOrgMembers(self):
    self.updateOrgAppSurvey()

    #OK
    self.data.createOrgAdmin(self.org)
    response = self.get(self.take_url)
    self.assertResponseOK(response)
    self.data.removeOrgAdmin()

    #also check for a mentor who is not admin
    self.data.createMentor(self.org)
    response = self.get(self.take_url)
    self.assertResponseOK(response)

  def testOrgAppSurveyTakePage(self):
    """Tests organizationn application survey take/retake page.
    """
    self.updateOrgAppSurvey()

    self.data.createOrgAdmin(self.org)
    backup_admin = GCIProfileHelper(self.gci, self.dev_test)
    backup_admin.createMentor(self.org)

    response = self.get(self.take_url)
    self.assertTemplatesUsed(response)

    params = {'admin_id': self.data.user.link_id,
              'backup_admin_id': backup_admin.user.link_id}
    params.update(self.post_params)
    response = self.post(self.take_url, params)
    query = OrgAppRecord.all()
    query.filter('main_admin = ', self.data.user)
    self.assertEqual(query.count(), 1, 'Survey record is not created.')

    record = query.get()
    self.assertEqual(record.org_id, self.post_params['org_id'])
    self.assertEqual(record.name, self.post_params['name'])
    self.assertEqual(record.description, self.post_params['description'])
    self.assertEqual(record.license, self.post_params['license'])
    self.assertEqual(record.main_admin.key(), self.data.user.key())
    self.assertEqual(record.backup_admin.key(), backup_admin.user.key())

    retake_url = self.retake_url_raw % (self.gci.key().name(),
                                        record.key().id())
    self.assertResponseRedirect(response, retake_url + '?validated')

    response = self.get(retake_url)
    self.assertResponseOK(response)

    params = {'backup_admin_id': backup_admin.user.link_id}
    params.update(self.post_params)
    params['name'] = 'New title'

    response = self.post(retake_url, params)
    self.assertResponseRedirect(response, retake_url + '?validated')
    record = OrgAppRecord.get_by_id(record.key().id())
    self.assertEqual(record.name, params['name'])


class GCIOrgAppRecordsPageTest(MailTestCase, GCIDjangoTestCase):
  """Tests for organization applications edit page.
  """

  def setUp(self):
    super(GCIOrgAppRecordsPageTest, self).setUp()
    self.init()
    self.record = SurveyHelper(self.gci, self.dev_test, self.org_app)
    self.url = '/gci/org/application/records/%s' % self.gci.key().name()

  def assertTemplatesUsed(self, response):
    """Asserts all the templates for edit page were used.
    """
    self.assertGCITemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/soc/org_app/records.html')

  def dataPostSingle(self, url, record, status):
    return self.dataPost(url, {record: status})

  def dataPost(self, url, changes):
    values = {}

    for record, status in changes.iteritems():
      record_data = {
          'status': status,
      }
      record_id = record.key().id()

      values[record_id] = record_data

    data = simplejson.dumps(values)

    postdata = {
        'data': data,
        'button_id': 'save',
        'idx': 0,
    }

    return self.post(url, postdata)

  def testGetRecords(self):
    self.data.createHost()
    record = self.record.createOrgApp('org1', self.data.user,
                                      {'status': 'needs review'})

    response = self.get(self.url)
    self.assertTemplatesUsed(response)

    list_data = self.getListData(self.url, 0)
    self.assertEqual(1, len(list_data))

    self.dataPostSingle(self.url, record, 'bogus')
    record = db.get(record.key())
    self.assertEqual('needs review', record.status)
    self.assertEmailNotSent()

    self.dataPostSingle(self.url, record, 'pre-accepted')
    record = db.get(record.key())
    self.assertEqual('pre-accepted', record.status)
    self.assertEmailNotSent()

    self.dataPostSingle(self.url, record, 'pre-rejected')
    record = db.get(record.key())
    self.assertEqual('pre-rejected', record.status)
    self.assertEmailNotSent()

    self.dataPostSingle(self.url, record, 'accepted')
    record = db.get(record.key())
    self.assertEqual('accepted', record.status)
    html = 'Organization accepted'
    self.assertEmailSent(n=1, html=html)

    self.dataPostSingle(self.url, record, 'rejected')
    record = db.get(record.key())
    self.assertEqual('rejected', record.status)
    html = 'Organization rejected'
    self.assertEmailSent(n=1, html=html)
    self.assertEmailSent(n=2)
