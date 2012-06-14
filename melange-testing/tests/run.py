#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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



import sys
import os

HERE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     '..'))
appengine_location = os.path.join(HERE, 'thirdparty', 'google_appengine')
extra_paths = [HERE,
               os.path.join(appengine_location, 'lib', 'django'),
               os.path.join(appengine_location, 'lib', 'webob'),
               os.path.join(appengine_location, 'lib', 'yaml', 'lib'),
               os.path.join(appengine_location, 'lib', 'antlr3'),
               appengine_location,
               os.path.join(HERE, 'app'),
               os.path.join(HERE, 'thirdparty', 'coverage'),
              ]

import nose
from nose import plugins

import logging
# Disable the messy logging information
logging.disable(logging.INFO)
log =  logging.getLogger('nose.plugins.cover')
logging.disable(logging.INFO)


def setup_gae_services():
  """Setups all google app engine services required for testing.
  """
  from google.appengine.api import apiproxy_stub_map
  from google.appengine.api import mail_stub
  from google.appengine.api import user_service_stub
  from google.appengine.api import urlfetch_stub
  from google.appengine.api.capabilities import capability_stub
  from google.appengine.api.memcache import memcache_stub
  from google.appengine.api.taskqueue import taskqueue_stub
  from google.appengine.api import datastore_file_stub
  apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
  apiproxy_stub_map.apiproxy.RegisterStub(
      'urlfetch', urlfetch_stub.URLFetchServiceStub())
  apiproxy_stub_map.apiproxy.RegisterStub(
      'user', user_service_stub.UserServiceStub())
  apiproxy_stub_map.apiproxy.RegisterStub(
      'memcache', memcache_stub.MemcacheServiceStub())
  apiproxy_stub_map.apiproxy.RegisterStub('datastore',
      datastore_file_stub.DatastoreFileStub('test-app-run', None, None))
  apiproxy_stub_map.apiproxy.RegisterStub('mail', mail_stub.MailServiceStub())
  yaml_location = os.path.join(HERE, 'app')
  apiproxy_stub_map.apiproxy.RegisterStub(
      'taskqueue', taskqueue_stub.TaskQueueServiceStub(root_path=yaml_location))
  apiproxy_stub_map.apiproxy.RegisterStub(
      'capability_service', capability_stub.CapabilityServiceStub())


def clean_datastore():
  from google.appengine.api import apiproxy_stub_map
  datastore = apiproxy_stub_map.apiproxy.GetStub('datastore')
  # clear datastore iff one is available
  if datastore is not None:
    datastore.Clear()


def begin(self):
  """Used to stub out nose.plugins.cover.Coverage.begin.

  The difference is that it loads Melange after coverage starts, so
  the loading of models, logic and views can be tracked by coverage.
  """
  log.debug("Coverage begin")
  import coverage
  self.skipModules = sys.modules.keys()[:]
  if self.coverErase:
    log.debug("Clearing previously collected coverage statistics")
    coverage.erase()
  coverage.exclude('#pragma[: ]+[nN][oO] [cC][oO][vV][eE][rR]')
  coverage.start()
  load_melange()


def load_melange():
  """Prepare Melange for usage.

  Registers a core, the GSoC and GCI modules, and calls the sitemap, sidebar
  and rights services.
  """

  from soc.modules import callback
  from soc.modules.core import Core

  # Register a core for the test modules to use
  callback.registerCore(Core())
  current_core = callback.getCore()
  #modules = ['gsoc', 'gci', 'seeder', 'statistic']
  modules = ['gsoc', 'gci', 'seeder']
  fmt = 'soc.modules.%s.callback'
  current_core.registerModuleCallbacks(modules, fmt)

  # Make sure all services are called
  current_core.callService('registerViews', True)
  current_core.callService('registerWithSitemap', True)
  current_core.callService('registerWithSidebar', True)
  current_core.callService('registerRights', True)


class AppEngineDatastoreClearPlugin(plugins.Plugin):
  """Nose plugin to clear the AppEngine datastore between tests.
  """
  name = 'AppEngineDatastoreClearPlugin'
  enabled = True
  def options(self, parser, env):
    return plugins.Plugin.options(self, parser, env)

  def configure(self, parser, env):
    plugins.Plugin.configure(self, parser, env)
    self.enabled = True

  def afterTest(self, test):
    clean_datastore()


def multiprocess_runner(ix, testQueue, resultQueue, currentaddr, currentstart,
           keyboardCaught, shouldStop, loaderClass, resultClass, config):
  """To replace the test runner of multiprocess.

  * Setup gae services at the beginning of every process
  * Clean datastore after each test
  """
  from nose import failure
  from nose.pyversion import bytes_
  import time
  import pickle
  try:
    from cStringIO import StringIO
  except ImportError:
    import StringIO
  from nose.plugins.multiprocess import _instantiate_plugins, \
    NoSharedFixtureContextSuite, _WritelnDecorator, TestLet
  config = pickle.loads(config)
  dummy_parser = config.parserClass()
  if _instantiate_plugins is not None:
    for pluginclass in _instantiate_plugins:
      plugin = pluginclass()
      plugin.addOptions(dummy_parser,{})
      config.plugins.addPlugin(plugin)
  config.plugins.configure(config.options,config)
  config.plugins.begin()
  log.debug("Worker %s executing, pid=%d", ix,os.getpid())
  loader = loaderClass(config=config)
  loader.suiteClass.suiteClass = NoSharedFixtureContextSuite

  def get():
    return testQueue.get(timeout=config.multiprocess_timeout)

  def makeResult():
    stream = _WritelnDecorator(StringIO())
    result = resultClass(stream, descriptions=1,
               verbosity=config.verbosity,
               config=config)
    plug_result = config.plugins.prepareTestResult(result)
    if plug_result:
      return plug_result
    return result

  def batch(result):
    failures = [(TestLet(c), err) for c, err in result.failures]
    errors = [(TestLet(c), err) for c, err in result.errors]
    errorClasses = {}
    for key, (storage, label, isfail) in result.errorClasses.items():
      errorClasses[key] = ([(TestLet(c), err) for c, err in storage],
                 label, isfail)
    return (
      result.stream.getvalue(),
      result.testsRun,
      failures,
      errors,
      errorClasses)

  def setup_process_env():
    """Runs just after the process starts to setup services.
    """
    setup_gae_services()

  def after_each_test():
    """Runs after each test to clean datastore.
    """
    clean_datastore()

  # Setup gae services at the beginning of every process
  setup_process_env()
  for test_addr, arg in iter(get, 'STOP'):
    if shouldStop.is_set():
      log.exception('Worker %d STOPPED',ix)
      break
    result = makeResult()
    test = loader.loadTestsFromNames([test_addr])
    test.testQueue = testQueue
    test.tasks = []
    test.arg = arg
    log.debug("Worker %s Test is %s (%s)", ix, test_addr, test)
    try:
      if arg is not None:
        test_addr = test_addr + str(arg)
      currentaddr.value = bytes_(test_addr)
      currentstart.value = time.time()
      test(result)
      currentaddr.value = bytes_('')
      resultQueue.put((ix, test_addr, test.tasks, batch(result)))
      # Clean datastore after each test
      after_each_test()
    except KeyboardInterrupt:
      keyboardCaught.set()
      if len(currentaddr.value) > 0:
        log.exception('Worker %s keyboard interrupt, failing '
                'current test %s',ix,test_addr)
        currentaddr.value = bytes_('')
        failure.Failure(*sys.exc_info())(result)
        resultQueue.put((ix, test_addr, test.tasks, batch(result)))
      else:
        log.debug('Worker %s test %s timed out',ix,test_addr)
        resultQueue.put((ix, test_addr, test.tasks, batch(result)))
    except SystemExit:
      currentaddr.value = bytes_('')
      log.exception('Worker %s system exit',ix)
      raise
    except:
      currentaddr.value = bytes_('')
      log.exception("Worker %s error running test or returning "
                    "results",ix)
      failure.Failure(*sys.exc_info())(result)
      resultQueue.put((ix, test_addr, test.tasks, batch(result)))
    if config.multiprocess_restartworker:
      break
  log.debug("Worker %s ending", ix)


def main():
  sys.path = extra_paths + sys.path
  os.environ['SERVER_SOFTWARE'] = 'Development via nose'
  os.environ['SERVER_NAME'] = 'Foo'
  os.environ['SERVER_PORT'] = '8080'
  os.environ['APPLICATION_ID'] = 'test-app-run'
  os.environ['USER_EMAIL'] = 'test@example.com'
  os.environ['USER_ID'] = '42'
  os.environ['CURRENT_VERSION_ID'] = 'testing-version'
  os.environ['HTTP_HOST'] = 'some.testing.host.tld'
  setup_gae_services()

  import main as app_main
  import django.test.utils
  django.test.utils.setup_test_environment()

  plugins = [AppEngineDatastoreClearPlugin()]
  # For coverage
  if '--coverage' in sys.argv:
    from nose.plugins import cover
    plugin = cover.Coverage()
    from mox import stubout
    stubout_obj = stubout.StubOutForTesting()
    stubout_obj.SmartSet(plugin, 'begin', begin)
    plugins.append(plugin)

    args = ['--with-coverage',
            '--cover-package=soc.',
            '--cover-erase',
            '--cover-html',
            '--cover-html-dir=coverageResults']

    sys.argv.remove('--coverage')
    sys.argv += args
  else:
    load_melange()

  # For multiprocess
  will_multiprocess = False
  for arg in sys.argv[1:]:
    if '--processes' in arg:
      will_multiprocess = True
      break
  if will_multiprocess:
    from mox import stubout
    from nose.plugins import multiprocess
    stubout_obj = stubout.StubOutForTesting()
    stubout_obj.SmartSet(multiprocess, '__runner', multiprocess_runner)
    # The default --process-timeout (10s) is too short
    sys.argv += ['--process-timeout=300']

  # Ignore functional and old_app tests
  args = ['--exclude=functional',
          '--exclude=^old_app$']
  sys.argv += args
  nose.main(addplugins=plugins)


if __name__ == '__main__':
  main()
