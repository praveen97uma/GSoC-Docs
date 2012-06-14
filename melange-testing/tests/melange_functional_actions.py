#!/usr/bin/env python2.5
#
# Copyright 2012 the Melange authors.
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

"""Base module for writing functional test scripts.
"""

import random
import string
import time
import logging

from selenium import webdriver
from selenium.common import exceptions

import xlrd

from test_utils import DjangoTestCase

class FunctionalTests(DjangoTestCase):  
  """ Base Class for all the Melange Functional Tests.
      Contains actions which will be used in writing Test scripts.
  """

  def init(self):
    self.obj_id = {}
    self.obj_val = {}
    self.Browser = webdriver.Firefox()
  
  def getParameters(self, name_of_workbook, name_of_sheet):
    """ Read the test data from excel sheets.

    Args:
      name_of_workbook: Workbook from which the test data will be imported.
      name_of_sheet: Particular sheet whose contents will be imported.
    """
    log = logging.getLogger("melange_functional_actions")
    log.setLevel(logging.DEBUG)
    logging.basicConfig()
    try:
      workbook = xlrd.open_workbook(name_of_workbook)
    except IOError as e:
      log.debug("Workbook %s not found" % (name_of_workbook))
      raise e               
    #Get a sheet by name.
    sheet = workbook.sheet_by_name(name_of_sheet)                        
    #Pulling all the element values from spreadsheet.
    for x in range(1, sheet.nrows):
      for y in range(0,1):
        obj = sheet.cell_value(x,y)
        id = sheet.cell_value(x,y+1)
        value = sheet.cell_value(x,y+2)
        self.obj_id[obj] = id
        self.obj_val[obj] = value

  def wait(self, sec):
    """ Delay the execution of script for specified number of seconds.

    Args:
      sec: Number of seconds for which the script should wait.
    """

    print "waiting for page to load for %s seconds " % sec
    time.sleep(sec)

  def writeTextField(self, id_type="", element=""):
    """ Write text field in a form.

    Args:
      id_type: Type of identification used to uniquely identify an element.
      element: Particular text field which will be written.
    """

    if id_type == "id":
      self.Browser.find_element_by_id(self.obj_id[element]).send_keys(\
                                                      self.obj_val[element])
    elif id_type == "xpath":
      self.Browser.find_element_by_xpath(self.\
                           obj_id[element]).send_keys(self.obj_val[element])
    else:
      raise NoSuchElementException 

  def toggleCheckBox(self, id_type="", chk_box=""):
    """ Toggle a check box.

    Args:
      id_type: Type of identification used to uniquely identify an element.
      chk_box: particular check box which will be selected/not selected.
    """

    if id_type == "id":
      self.Browser.find_element_by_id(self.obj_id[chk_box]).click()
    elif id_type == "xpath":
      self.Browser.find_element_by_xpath(self.obj_id[chk_box]).click()
    else:
      raise NoSuchElementException

  def setDropDownList(self, select_opt=""):
    """ Selects one option from the drop down list.

    Args:
      select_opt: The option which should be selected from the drop down list.       
    """

    selection = self.Browser.find_element_by_xpath\
                                                  (self.obj_id[select_opt])
    all_options = selection.find_elements_by_tag_name("option")
    for option in all_options:
      if (option.get_attribute("value") == self.obj_val[select_opt]):
        option.click()
    
  def waitAndEnterText(self, sec, id_type="", element=""):
    """ Wait and enter text in a particular field.

    Args:
      sec: Number of seconds script should wait.
      id_type: Type of identification used to uniquely identify an element.
      element: The field in which we we want to enter some text.      
    """

    self.wait(sec)
    if id_type == "id":
      self.Browser.find_element_by_id(self.obj_id[element]).send_keys\
                                                        (self.obj_val[element])
    elif id_type == "xpath":
      self.Browser.find_element_by_xpath(self.obj_id[element]).send_keys\
                                                        (self.obj_val[element])
    else:
      raise NoSuchElementException   

  def clearFieldAssertErrorMessageAndEnterData(self, error_element , element=""):
    """Assert the error message , clear the input field and enter a new value.

    Args:
      erro_element: It is the element which is showing error message.
      element: The correct value for the input field.                 
    """

    self.assertTextIn(error_element)
    self.clearField("xpath", element)
    self.writeTextField("xpath", element)
 
  def clearField(self, id_type="", clear_element=""):
    """ Wait and clear a particular field.

    Args:
      clear_element: The field which we want to clear.
      id_type: Type of identification used to uniquely identify an element.
    """
    if id_type == "id":
      self.Browser.find_element_by_id(self.obj_id[clear_element]).clear()
    elif id_type == "xpath":
      self.Browser.find_element_by_xpath(self.obj_id[clear_element]).clear()
    else:
      raise NoSuchElementException   
 
  def clickOn(self, id_type="", click_element=""):
    """ Click on the specified element.

    Args:
      click_element: The element which will be clicked.
      id_type: Type of identification used to uniquely identify an element.
    """

    if id_type == "id":
      self.Browser.find_element_by_id(self.obj_id[click_element]).click()
    elif id_type == "xpath":
      self.Browser.find_element_by_xpath(self.obj_id[click_element]).click()
    else:
      raise NoSuchElementException

  def assertError(self, msg):
    """Print the message and raise assertion error.

    Args:
      msg: The message which should be printed.  
    """

    print msg
    raise AssertionError(msg)

  def assertLink(self, link_text=""):
    """Assert if a link is there.

    Args:
      link_text: The link which will be tested.  
    """

    try:
      link = self.Browser.find_element_by_link_text(link_text)      
    except NoSuchElementException as e :
      msg = "The text %s is not part of a Link" % link_text
      self.assertError(msg)

  def assertText(self, text_element=""):
    """Assert a particular text.

    Args:
      text_element: The text which will be checked. 
    """

    txt = self.Browser.find_element_by_xpath(self.obj_id[text_element]).text
    if txt is None:
        msg = "Element %s has no text %s " % (text_element, txt)
        self.assertError(msg)
    if txt != self.obj_val[text_element]:
        msg = "Element text should be %s. It is %s."\
                                            % (self.obj_val[text_element], txt)
        self.assertError(msg)

  def assertMessageAndEnterText(self, error_element="", input_field=""):
    """Assert a message and enter value in the text field.

    Args:
      error_element : the error message from the application which will be checked.
      input_field : input box in which a value will be entered.
    """

    self.assertText(error_element)
    self.writeTextField("xpath", input_field)

  def assertTextIn(self, text_element):
    """check for the contents present in a text message.

    Args:
      text_element : the message content which will be checked with the
                     message from the application.      
    """

    error_msg = self.Browser.find_element_by_xpath(\
                                               self.obj_id[text_element]).text
    if error_msg is None:
        msg = "Element %s has no text %s " % (text_element, error_msg)
        self.assertError(msg)
    if error_msg not in self.obj_val[text_element]:
        msg = "Element text should be %s.  It is %s." % (self.obj_val[\
                                                         text_element], error_msg)
        self.assertError(msg)

  def waitAndAssertIfDisplayed(self, sec, element_displayed=""):
    """ Wait and check if a particular element is displayed.

    Args:
      sec: Number of seconds script should wait.
      element_displayed: The element which we want to check if it displayed, if
                         it is displayed then return true else raise exception.
    """
  
    self.wait(sec)
    try:
      self.Browser.find_element_by_xpath\
           (self.obj_id[element_displayed]).is_displayed()
      return True
    except:
      raise NoSuchElementException

  def isElementDisplayed(self, sec, element_displayed=""):
    """ Wait and check if a particular element is displayed.

    Args:
      sec: Number of seconds script should wait.
      element_displayed: A particular message which we want to check if it is 
                         displayed, if the message is absent, we wish the normal
                         execution of test to continue.
    """
   
    self.wait(sec)
    try:
      self.Browser.find_element_by_xpath\
                                 (self.obj_id[element_displayed]).is_displayed()
      return True
    except:
      pass

  def fillRandomValue(self, element=""):
    """ It takes a value , add random string at the end and fill it in the form.

    Args:
      element: The element whose value will be changed by adding a random string 
               at the end.
    """

    N=5
    val = self.obj_val[element] + ''.join(random.choice(string.ascii_lowercase\
                                             + string.digits) for x in range(N))
    self.wait(1)
    self.clearField("xpath", element)
    self.Browser.find_element_by_xpath(self.obj_id[element]).send_keys(val)

  def waitAndClick(self, sec, id_type="", elem_click = ""):
    """ wait and click on a particular element.

    Args:
      sec: Number of seconds script should wait.
      id_type: Type of identification used to uniquely identify an element.
      elem_click: The element which we want to click.
    """
    
    self.wait(sec)
    if id_type == "id":
      self.Browser.find_element_by_id(self.obj_id[click_element]).click()
    elif id_type == "xpath":
      self.Browser.find_element_by_xpath(self.obj_id[click_element]).click()
    else:
      raise NoSuchElementException    
        
  def takeScreenshot(self):
    """Take screenshot.
    """

    self.Browser.save_screenshot("Melange.png")

  def teardown(self):
    """Take a screenshot and close the browser.
    """

    self.wait(2)
    self.takeScreenshot()
    self.Browser.close()

  def login(self):
    """ Logs in to the melange.
    """

    self.clearField("xpath", "Login_email")
    self.writeTextField("xpath", "Login_email")
    self.clickOn("xpath", "Sign_in_button")
