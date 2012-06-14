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

"""Tests for student_evaluation views.
"""


import urllib

from django import forms as django_forms
from django.utils import simplejson as json
from django.utils.html import escape

from tests import timeline_utils
from tests.profile_utils import GSoCProfileHelper
from tests.survey_utils import SurveyHelper
from tests.test_utils import GSoCDjangoTestCase


from soc.views import forms

from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.models.project_survey import ProjectSurvey

from soc.modules.seeder.logic.providers.string import LinkIDProvider


class StudentEvaluationTest(GSoCDjangoTestCase):
  """Tests proposal review page.
  """

  def setUp(self):
    super(StudentEvaluationTest, self).setUp()
    self.init()
    self.evaluation = SurveyHelper(self.gsoc, self.dev_test)

  def assertEvaluationCreateTemplateUsed(self, response):
    """Asserts that all the evaluation create/edit templates were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/form_base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_evaluation.html')

  def assertEvaluationTakeTemplateUsed(self, response):
    """Asserts that all the evaluation take templates were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/form_base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_evaluation_take.html')

  def assertEvaluationShowTemplateUsed(self, response):
    """Asserts that all the evaluation show templates were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_survey/show.html')

  def assertFieldChoices(self, schema_choices, form_choices):
    """Asserts if the form field has the same choices as defined in the schema.
    """
    choices = [c['value'] for c in schema_choices]
    self.assertEqual(choices.sort(), form_choices.sort())

  def assertFormFromSchema(self, form, schema_json):
    """Asserts if the form built from the schema is same as the schema defined.
    """
    order, fields = json.loads(urllib.unquote(schema_json))

    for field in order:
      field_dict = fields[field]
      form_field = form.fields[field]

      if field_dict['field_type'] == 'checkbox':
        self.assertTrue(isinstance(form_field,
                                   django_forms.MultipleChoiceField))
        self.assertTrue(isinstance(form_field.widget,
                                   forms.CheckboxSelectMultiple))
        self.assertFieldChoices(field_dict['values'], form_field.choices)
      elif field_dict['field_type'] == 'radio':
        self.assertTrue(isinstance(form_field, django_forms.ChoiceField))
        self.assertTrue(isinstance(form_field.widget,
                                   django_forms.RadioSelect))
        self.assertFieldChoices(field_dict['values'], form_field.choices)
      elif field_dict['field_type'] == 'textarea':
        self.assertTrue(isinstance(form_field, django_forms.CharField))
        self.assertTrue(isinstance(form_field.widget, django_forms.Textarea))
      elif field_dict['field_type'] == 'input_text':
        self.assertTrue(isinstance(form_field, django_forms.CharField))

      self.assertEqual(field_dict['label'], form_field.label)
      self.assertEqual(field_dict['required'], form_field.required)

  def createProject(self, override_properties={}):
    properties = {
        'is_featured': False, 'mentors': [],
        'status': 'accepted', 'program': self.gsoc, 'org': self.org,

    }
    properties.update(override_properties)
    return self.seed(GSoCProject, properties)

  def getStudentEvalRecordProperties(self, show=False):
    eval = self.evaluation.createStudentEvaluation()

    mentor_profile = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor_profile.createOtherUser('mentor@example.com')
    mentor = mentor_profile.createMentor(self.org)

    student_profile = GSoCProfileHelper(self.gsoc, self.dev_test)
    student_profile.createOtherUser('student_with_proj@example.com')
    student_profile.createStudentWithProject(self.org, mentor)

    project = GSoCProject.all().get()

    suffix = "%s/%s/%s/%s" % (
        self.gsoc.key().name(), eval.link_id,
        project.parent().link_id, project.key().id())

    base_url = '/gsoc/eval/student'
    if show:
      url = '%s/show/%s' % (base_url, suffix)
    else:
      url = '%s/%s' % (base_url, suffix)

    return (url, eval, mentor)

  def ffPastEval(self, eval):
    eval.survey_start = timeline_utils.past(20)
    eval.survey_end = timeline_utils.past(10)
    eval.put()

  def testCreateEvaluationForStudentWithoutProject(self):
    link_id = LinkIDProvider(ProjectSurvey).getValue()
    suffix = "%s/%s" % (self.gsoc.key().name(), link_id)

    self.data.createStudent()
    # test review GET
    url = '/gsoc/eval/student/edit/' + suffix
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testCreateEvaluationForMentorWithoutProject(self):
    link_id = LinkIDProvider(ProjectSurvey).getValue()
    suffix = "%s/%s" % (self.gsoc.key().name(), link_id)

    self.data.createMentor(self.org)
    # test review GET
    url = '/gsoc/eval/student/edit/' + suffix
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testCreateEvaluationForStudent(self):
    link_id = LinkIDProvider(ProjectSurvey).getValue()
    suffix = "%s/%s" % (self.gsoc.key().name(), link_id)

    mentor_profile = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor_profile.createOtherUser('mentor@example.com')
    mentor = mentor_profile.createMentor(self.org)

    self.data.createStudentWithProject(self.org, mentor)
    # test review GET
    url = '/gsoc/eval/student/edit/' + suffix
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testCreateEvaluationForMentor(self):
    link_id = LinkIDProvider(ProjectSurvey).getValue()
    suffix = "%s/%s" % (self.gsoc.key().name(), link_id)

    student_profile = GSoCProfileHelper(self.gsoc, self.dev_test)
    student_profile.createOtherUser('student_with_proj@example.com')
    student = student_profile.createStudent()

    self.data.createMentorWithProject(self.org, student)
    # test review GET
    url = '/gsoc/eval/student/edit/' + suffix
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testCreateEvaluationForOrgAdmin(self):
    link_id = LinkIDProvider(ProjectSurvey).getValue()
    suffix = "%s/%s" % (self.gsoc.key().name(), link_id)

    self.data.createOrgAdmin(self.org)
    # test review GET
    url = '/gsoc/eval/student/edit/' + suffix
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testCreateEvaluationForHost(self):
    host = self.data.createHost()

    link_id = LinkIDProvider(ProjectSurvey).getValue()
    suffix = "%s/%s" % (self.gsoc.key().name(), link_id)

    # test student evaluation create/edit GET
    url = '/gsoc/eval/student/edit/' + suffix
    response = self.get(url)
    self.assertEvaluationCreateTemplateUsed(response)

    self.assertContains(
        response, 'Create new student evaluation')
    self.assertContains(
        response, '<input name="schema" type="hidden" id="schema" value="" />')

    self.assertEqual(response.context['page_name'],
                     'Create new student evaluation')
    self.assertEqual(response.context['post_url'], url)
    form = response.context['forms'][0]

    expected_fields = ['author', 'title', 'short_name', 'content',
                       'survey_start', 'survey_end', 'schema'].sort()
    actual_fields = form.fields.keys().sort()
    self.assertEqual(expected_fields, actual_fields)

    # TODO(Madhu): Get rid of scope and author fields once the data
    # conversion is done.
    override = {
        'survey_content': None,
        'author': host.key(),
        'created_by': host.key(),
        'program': self.gsoc.key(),
        'modified_by': host.key(),
        'schema': self.evaluation.evalSchemaString(),
        }
    response, _ = self.modelPost(url, ProjectSurvey, override)
    self.assertResponseRedirect(response, url+'?validated')

    eval = ProjectSurvey.all().get()

    response = self.get(url)
    self.assertEvaluationCreateTemplateUsed(response)

    self.assertContains(
        response, 'Edit - %s' % (eval.title,))
    self.assertContains(
        response,
        '<input name="schema" type="hidden" id="schema" value=%s />'
        % (json.dumps(escape(eval.schema)),))

    self.assertEqual(response.context['page_name'],
                     'Edit - %s' % (eval.title,))
    self.assertEqual(response.context['post_url'], url)
    form = response.context['forms'][0]

    expected_fields = ['author', 'title', 'short_name', 'content',
                       'survey_start', 'survey_end', 'schema'].sort()
    actual_fields = form.fields.keys().sort()
    self.assertEqual(expected_fields, actual_fields)

  def testTakeEvaluationForMentor(self):
    url, eval, _ = self.getStudentEvalRecordProperties()

    mentor = self.data.createMentor(self.org)

    # test student evaluation take GET for a mentor of the same organization
    response = self.get(url)
    self.assertResponseForbidden(response)

    response = self.client.post(url)
    self.assertResponseForbidden(response)

    project = GSoCProject.all().get()
    project.mentors.append(mentor.key())
    project.put()
    # test student evaluation take GET for the mentor of the project
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testTakeEvaluationForAnotherOrgMentor(self):
    url, eval, _ = self.getStudentEvalRecordProperties()

    another_org = self.createOrg()
    self.data.createMentor(another_org)
    # test student evaluation take GET for a mentor of another organization
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testTakeEvaluationForAnotherOrgAdmin(self):
    url, eval, _ = self.getStudentEvalRecordProperties()

    another_org = self.createOrg()
    self.data.createOrgAdmin(another_org)
    # test student evaluation take GET for an org admin of another organization
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testTakeEvaluationForOrgAdmin(self):
    url, eval, _ = self.getStudentEvalRecordProperties()

    project = GSoCProject.all().get()

    suffix = "%s/%s/%s/%s" % (
        self.gsoc.key().name(), eval.link_id,
        project.parent().link_id, project.key().id())

    base_url = '/gsoc/eval/student'

    show_url = '%s/show/%s' % (base_url, suffix)
    self.data.createOrgAdmin(self.org)
    response = self.get(url)
    self.assertResponseRedirect(response, show_url)

  def testTakeEvalForStudentWithNoProject(self):
    self.data.createStudent()

    # test student evaluation show GET for a for a student who
    # does not have a project in the program
    url, eval, _ = self.getStudentEvalRecordProperties()
    response = self.get(url)
    self.assertResponseForbidden(response)

    project = GSoCProject.all().get()

    suffix = "%s/%s/%s/%s" % (
        self.gsoc.key().name(), eval.link_id,
        project.parent().link_id, project.key().id())

    base_url = '/gsoc/eval/student'

    self.ffPastEval(eval)
    response = self.get(url)
    show_url = '%s/show/%s' % (base_url, suffix)
    self.assertResponseRedirect(response, show_url)

  def testTakeEvalForAnotherStudentWithProject(self):
    url, eval, mentor = self.getStudentEvalRecordProperties()

    self.data.createStudentWithProject(self.org, mentor)
    # test student evaluation show GET for a for a student who
    # has another project in the same org and whose mentor is
    # same as the student whose survey is being accessed
    response = self.get(url)
    self.assertResponseForbidden(response)

    project = GSoCProject.all().get()

    suffix = "%s/%s/%s/%s" % (
        self.gsoc.key().name(), eval.link_id,
        project.parent().link_id, project.key().id())

    base_url = '/gsoc/eval/student'

    self.ffPastEval(eval)
    response = self.get(url)
    show_url = '%s/show/%s' % (base_url, suffix)
    self.assertResponseRedirect(response, show_url)

  def testTakeEvalForStudentProjectWithAnotherMentor(self):
    url, eval, _ = self.getStudentEvalRecordProperties()

    mentor_profile = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor_profile.createOtherUser('mentor_another@example.com')
    mentor = mentor_profile.createMentor(self.org)

    self.data.createStudentWithProject(self.org, mentor)
    # test student evaluation show GET for a for a student who
    # has another project whose mentor is different than the current
    # mentor but the project is in the same org
    response = self.get(url)
    self.assertResponseForbidden(response)

    project = GSoCProject.all().get()

    suffix = "%s/%s/%s/%s" % (
        self.gsoc.key().name(), eval.link_id,
        project.parent().link_id, project.key().id())

    base_url = '/gsoc/eval/student'

    self.ffPastEval(eval)
    response = self.get(url)
    show_url = '%s/show/%s' % (base_url, suffix)
    self.assertResponseRedirect(response, show_url)

  def testTakeEvalForStudentProjectWithAnotherOrg(self):
    url, eval, _ = self.getStudentEvalRecordProperties()
    other_org = self.createOrg()

    mentor_profile = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor_profile.createOtherUser('mentor_other_org@example.com')
    mentor = mentor_profile.createMentor(other_org)

    self.data.createStudentWithProject(other_org, mentor)
    # test student evaluation show GET for a for a student who
    # has another project in a different organization
    response = self.get(url)
    self.assertResponseForbidden(response)

    project = GSoCProject.all().get()

    suffix = "%s/%s/%s/%s" % (
        self.gsoc.key().name(), eval.link_id,
        project.parent().link_id, project.key().id())

    base_url = '/gsoc/eval/student'

    self.ffPastEval(eval)
    response = self.get(url)
    show_url = '%s/show/%s' % (base_url, suffix)
    self.assertResponseRedirect(response, show_url)

  def testTakeEvalForStudent(self):
    eval = self.evaluation.createStudentEvaluation()

    mentor_profile = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor_profile.createOtherUser('mentor@example.com')
    mentor = mentor_profile.createMentor(self.org)

    self.data.createStudentWithProject(self.org, mentor)

    project = GSoCProject.all().get()

    base_url = '/gsoc/eval/student'
    suffix = "%s/%s/%s/%s" % (
        self.gsoc.key().name(), eval.link_id,
        project.parent().link_id, project.key().id())

    url = '%s/%s' % (base_url, suffix)

    # test student evaluation show GET for a for a student who
    # has another project in a different organization
    response = self.get(url)
    self.assertEvaluationTakeTemplateUsed(response)

    self.assertContains(response, '%s' % (eval.title))
    self.assertContains(response, 'Project: %s' % (project.title))

    self.assertEqual(response.context['page_name'],
                     '%s' % (eval.title))
    form = response.context['forms'][0]

    self.assertFormFromSchema(form, eval.schema)

    postdata = {
        'frm-t1309871149671-item': 'one line text message',
        'frm-t1309871322655-item': ['Option 2', 'Option 3'],
        'frm-t1309871157535-item': """A quick brown fox jumped over a lazy dog.
        A quick brown fox jumped over a lazy dog. A quick brown fox jumped 
        over a lazy dog. A quick brown fox jumped over a lazy dog.""",
        }
    response = self.post(url, postdata)
    self.assertResponseOK(response)
    self.assertFormError(
        response, 'form', 'frm-t1310822212610-item',
        'This field is required.')

    postdata = {
        'frm-t1309871149671-item': 'one line text message',
        'frm-t1309871322655-item': ['Option 2', 'Option 3'],
        'frm-t1309871157535-item': """A quick brown fox jumped over a lazy dog.
        A quick brown fox jumped over a lazy dog. A quick brown fox jumped 
        over a lazy dog. A quick brown fox jumped over a lazy dog.""",
        'frm-t1310822212610-item': "Wa Wa",
        }
    response = self.post(url, postdata)
    self.assertResponseRedirect(response, '%s?validated' % (url,))

    self.ffPastEval(eval)
    response = self.get(url)
    show_url = '%s/show/%s' % (base_url, suffix)
    self.assertResponseRedirect(response, show_url)

  def testShowEvalForStudentWithNoProject(self):
    self.data.createStudent()

    # test student evaluation show GET for a for a student who
    # does not have a project in the program
    url, eval, _ = self.getStudentEvalRecordProperties(show=True)
    response = self.get(url)
    self.assertResponseForbidden(response)

    self.ffPastEval(eval)
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testShowEvalForAnotherStudentWithProject(self):
    url, eval, mentor = self.getStudentEvalRecordProperties(show=True)

    self.data.createStudentWithProject(self.org, mentor)
    # test student evaluation show GET for a for a student who
    # has another project in the same org and whose mentor is
    # same as the student whose survey is being accessed
    response = self.get(url)
    self.assertResponseForbidden(response)

    self.ffPastEval(eval)
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testShowEvalForStudentProjectWithAnotherMentor(self):
    url, eval, _ = self.getStudentEvalRecordProperties(show=True)

    mentor_profile = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor_profile.createOtherUser('mentor_another@example.com')
    mentor = mentor_profile.createMentor(self.org)

    self.data.createStudentWithProject(self.org, mentor)
    # test student evaluation show GET for a for a student who
    # has another project whose mentor is different than the current
    # mentor but the project is in the same org
    response = self.get(url)
    self.assertResponseForbidden(response)

    self.ffPastEval(eval)
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testShowEvalForStudentProjectWithAnotherOrg(self):
    url, eval, _ = self.getStudentEvalRecordProperties(show=True)
    other_org = self.createOrg()

    mentor_profile = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor_profile.createOtherUser('mentor_other_org@example.com')
    mentor = mentor_profile.createMentor(other_org)

    self.data.createStudentWithProject(other_org, mentor)
    # test student evaluation show GET for a for a student who
    # has another project in a different organization
    response = self.get(url)
    self.assertResponseForbidden(response)

    self.ffPastEval(eval)
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testShowEvalForStudent(self):
    eval = self.evaluation.createStudentEvaluation()

    mentor_profile = GSoCProfileHelper(self.gsoc, self.dev_test)
    mentor_profile.createOtherUser('mentor@example.com')
    mentor = mentor_profile.createMentor(self.org)

    self.data.createStudentWithProject(self.org, mentor)

    project = GSoCProject.all().get()

    suffix = "%s/%s/%s/%s" % (
        self.gsoc.key().name(), eval.link_id,
        project.parent().link_id, project.key().id())

    url = '/gsoc/eval/student/show/%s' % (suffix,)

    # test student evaluation show GET for a for a student who
    # has another project in a different organization
    response = self.get(url)
    self.assertEvaluationShowTemplateUsed(response)

    self.ffPastEval(eval)
    response = self.get(url)
    self.assertEvaluationShowTemplateUsed(response)

  def testShowEvaluationForMentor(self):
    # test student evaluation show GET for a mentor of the same organization
    url, eval, mentor = self.getStudentEvalRecordProperties(show=True)
    response = self.get(url)
    self.assertResponseForbidden(response)

    project = GSoCProject.all().get()

    project_mentors = project.mentors
    project.mentors.append(mentor.key())
    project.put()
    # test student evaluation show GET for the mentor of the project
    response = self.get(url)
    self.assertResponseForbidden(response)

    self.ffPastEval(eval)
    project.mentors = project_mentors
    project.put()

    response = self.get(url)
    self.assertResponseForbidden(response)

    project.mentors.append(mentor.key())
    project.put()

    response = self.get(url)
    self.assertResponseForbidden(response)

  def testShowEvaluationForOtherOrgMentor(self):
    another_org = self.createOrg()
    self.data.createMentor(another_org)
    url, eval, _ = self.getStudentEvalRecordProperties(show=True)

    # test student evaluation show GET for a mentor of another organization
    response = self.get(url)
    self.assertResponseForbidden(response)

    self.ffPastEval(eval)
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testShowEvaluationForOtherOrgAdmin(self):
    another_org = self.createOrg()
    self.data.createOrgAdmin(another_org)
    url, eval, _ = self.getStudentEvalRecordProperties(show=True)

    # test student evaluation show GET for an org admin of another organization
    response = self.get(url)
    self.assertResponseForbidden(response)

    self.ffPastEval(eval)
    response = self.get(url)
    self.assertResponseForbidden(response)

  def testShowEvaluationForOrgAdmin(self):
    self.data.createOrgAdmin(self.org)
    url, eval, _ = self.getStudentEvalRecordProperties(show=True)
    # test student evaluation show GET for an org admin of the org
    # to which project belongs to
    response = self.get(url)
    self.assertResponseForbidden(response)

    self.ffPastEval(eval)
    response = self.get(url)
    self.assertEvaluationShowTemplateUsed(response)
