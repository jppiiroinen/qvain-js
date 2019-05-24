#!/usr/bin/env python3
################################################################
# This contains the base class QvainTestCase with some helper
# functions for tests.
#
# This file is part of Qvain project.
#
# Author(s):
#     Juhapekka Piiroinen <juhapekka.piiroinen@csc.fi>
#
# Copyright 2019 CSC - IT Center for Science Ltd.
# Copyright 2019 The National Library Of Finland
# All Rights Reserved.
################################################################

import os
import sys
import logging
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


class QvainTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("./chromedriver")
        self.wait = WebDriverWait(self.driver, 10)
        self.logger = logging.getLogger()
        self.logger.level = logging.DEBUG
        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(self.stream_handler)
        if self.start_test:
            self.start_test()

    def start_memory_measure(self):
        self.memory_usage_at_start = int(self.memory_usage())

    def end_memory_measure(self):
        currentMemoryUsage = int(self.memory_usage())
        return currentMemoryUsage - self.memory_usage_at_start, currentMemoryUsage, self.memory_usage_at_start

    def end_memory_measure_and_report(self):
        memory_diff, memory_end, memory_start = self.end_memory_measure()
        self.logger.info("\n{id} | JS Memory start: {start}Mb | end: {end}Mb | diff: {diff}Mb".format(
            id=self.id(),
            start=int(memory_start/1024/1024),
            end=int(memory_end/1024/1024),
            diff=int(memory_diff/1024/1024)
        ))

    def memory_usage(self):
        return self.driver.execute_script("return window.performance.memory.usedJSHeapSize")

    def is_frontend_running(self):
        # This is the xpath for default error page header in nginx
        # We do not have such xpath in our frontend
        assert self.elem_is_not_found_xpath("/html/body/center[1]/h1"), "It looks like that the frontend process is not running. NGINX error page?"

    def login(self, username=os.environ["TEST_USERNAME"], password=os.environ["TEST_PASSWORD"], address=os.environ["TEST_ADDRESS"]):
        # lets ensure that we are on our first initial page
        self.driver.get(address)
        self.is_frontend_running()
        self.wait.until(EC.title_is("Qvain"))

        # lets tap the Login now button on our landing page
        login_button = self.driver.find_element_by_link_text("Login now!")
        login_button.click()

        # we will get a page redirection to another service
        self.wait.until(EC.title_is("Web Login Service"))
        loginHakaTestBtn = self.driver.find_element_by_link_text("authn/LoginHakaTest")
        loginHakaTestBtn.click()

        # we will get a page redirection to another service again
        self.wait.until(EC.title_is("Haka — WAYF"))
        userIdpSelectDropDown = Select(self.driver.find_element_by_id("userIdPSelection"))
        userIdpSelectDropDown.select_by_value("https://testidp.funet.fi/idp/shibboleth")
        userIdpSelectButton = self.driver.find_element_by_name("Select")
        userIdpSelectButton.click()

        # we will get a page redirection to another service again too
        self.wait.until(EC.title_is("CSC - Haka test IdP"))
        usernameInput = self.driver.find_element_by_id("username")
        usernameInput.send_keys(username)
        passwordInput = self.driver.find_element_by_id("password")
        passwordInput.send_keys(password)

        loginButton = self.driver.find_element_by_name("_eventId_proceed")
        loginButton.click()

        # we should have been redirected back to the our web service
        self.wait.until(EC.title_is("Qvain"))

    def open_usermenu(self):
        userDropdown = self.driver.find_element_by_id("usermenu")
        userDropdown.click()

    def close_usermenu(self):
        userDropdown = self.driver.find_element_by_id("usermenu")
        userDropdown.click()

    def open_datasets_view(self):
        # lets tap the navigation bar where we should see the link
        myDatasetsLink = self.driver.find_element_by_link_text("My Datasets")
        myDatasetsLink.click()

        # lets wait until the page has been loaded
        header = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="component-title"]')))
        assert 'My datasets' in header.text, "We are not in My datasets view, it seems that we are in {header}".format(header=header.text)

    def open_editor_view(self):
        self.open_datasets_view()

        # lets tap on the create new record button
        createNewDataset = self.driver.find_element_by_id('datasets_button_create-new-record')
        createNewDataset.click()

        # we should end up into new dataset page
        header = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="component-title"]')))
        assert 'Dataset' in header.text, "We are not in Dataset view, it seems that we are in {header}".format(header=header.text)

    def logout(self):
        self.open_usermenu()
        signoutMenuItem = self.driver.find_element_by_id("usermenu_signout")
        signoutMenuItem.click()

    def verify_that_user_is_logged_in(self):
        self.open_usermenu()
        usermenu_fullname = self.driver.find_element_by_xpath('//*[@id="usermenu"]/div/h6/a')
        assert os.environ["TEST_FULLNAME"] in usermenu_fullname.text, "It seems that the user ({user} != {expected}) is not logged in".format(user=usermenu_fullname.text, expected=os.environ["TEST_FULLNAME"])
        self.close_usermenu()

    def close(self):
        self.driver.close()

    def print(self, message):
        self.logger.info(message)

    def tearDown(self):
        if self.end_test:
            self.end_test()
        self.driver.quit()
        self.logger.removeHandler(self.stream_handler)

    def button_is_disabled(self, btn):
        assert "disabled" in btn.get_attribute("class"), "It looks like that the button was ENABLED."

    def button_is_enabled(self, btn):
        assert "disabled" not in btn.get_attribute("class"), "It looks like that the button was DISABLED"

    def elem_is_not_found(self, elemid):
        try:
            btn = self.driver.find_element_by_id(elemid)
            return False
        except NoSuchElementException:
            return True

    def elem_is_not_found_xpath(self, xpath):
        try:
            btn = self.driver.find_element_by_xpath(xpath)
            return False
        except NoSuchElementException:
            return True

    def scroll_to_element(self, elem):
        actions = ActionChains(self.driver)
        actions.move_to_element(elem)
        actions.perform()

    def scroll_to_up(self):
        self.driver.execute_script("window.scroll(0, 0);")

    def scroll_to_bottom(self):
        self.driver.find_element_by_tag_name('body').send_keys(Keys.END)

    def close_alert(self):
        close_alert_btn = self.wait.until(EC.presence_of_element_located((By.ID, 'root_alert'))).find_element_by_class_name("close")
        close_alert_btn.click()

    def click_elem(self, elemId):
        self.driver.find_element_by_id(elemId).click()

    def select_option(self, elemId, option):
        selectBox = Select(self.driver.find_element_by_id(elemId))
        selectBox.select_by_visible_text(option)

    def is_option_selected(self, elemId, option):
        selectBox = Select(self.driver.find_element_by_id(elemId))
        return option in selectBox.first_selected_option.text

    def enter_text(self, elemId, text):
        elem = self.driver.find_element_by_id(elemId)
        elem.click()
        elem.send_keys(text)
        elem.send_keys(Keys.TAB)

    def find_element(self, elemId):
        return self.driver.find_element_by_id(elemId)

    def open_dropdown(self, elemId):
        self.driver.find_element_by_id(elemId).find_element_by_class_name("dropdown-toggle").click()

    def select_dropdown_option(self, elemId, option):
        self.driver.find_element_by_id(elemId).find_element_by_class_name("dropdown-menu").find_element_by_partial_link_text(option).click()

    def select_option_from_multiselect(self, elemId, optionValue):
        # lets open the multiselect
        elem = self.driver.find_element_by_id(elemId)
        multiselect = elem.find_element_by_class_name("multiselect")
        multiselect.click()

        # lets scan for the options which are available.
        multiselect_content = elem.find_element_by_class_name("multiselect__content")
        multiselect_options = multiselect_content.find_elements_by_class_name("multiselect__element")

        # this can fail when the network connection is not working properly.
        # so lets ensure that we did get more than zero options
        assert len(multiselect_options) > 0, "We did not find any options from the multiselect"

        # lets find the option from the list of found options
        for option in multiselect_options:
            if option.text.find(optionValue) > -1:
                # once we found it we click on it
                option.click()
                return

        # we did not find the option from the list
        raise NoSuchElementException("{option} was not found from {elem} ".format(option=optionValue, elem=elemId))

