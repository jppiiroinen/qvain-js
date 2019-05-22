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

    def login(self, username=os.environ["TEST_USERNAME"], password=os.environ["TEST_PASSWORD"], address=os.environ["TEST_ADDRESS"]):
        self.driver.get(address)
        self.wait.until(EC.title_is("Qvain"))
        login_button = self.driver.find_element_by_link_text("Login now!")
        login_button.click()

        self.wait.until(EC.title_is("Web Login Service"))
        loginHakaTestBtn = self.driver.find_element_by_link_text("authn/LoginHakaTest")
        loginHakaTestBtn.click()

        self.wait.until(EC.title_is("Haka — WAYF"))
        userIdpSelectDropDown = Select(self.driver.find_element_by_id("userIdPSelection"))
        userIdpSelectDropDown.select_by_value("https://testidp.funet.fi/idp/shibboleth")
        userIdpSelectButton = self.driver.find_element_by_name("Select")
        userIdpSelectButton.click()

        self.wait.until(EC.title_is("CSC - Haka test IdP"))
        usernameInput = self.driver.find_element_by_id("username")
        usernameInput.send_keys(username)
        passwordInput = self.driver.find_element_by_id("password")
        passwordInput.send_keys(password)

        loginButton = self.driver.find_element_by_name("_eventId_proceed")
        loginButton.click()

        # front page of qvain
        self.wait.until(EC.title_is("Qvain"))

    def open_usermenu(self):
        userDropdown = self.driver.find_element_by_id("usermenu")
        userDropdown.click()

    def close_usermenu(self):
        userDropdown = self.driver.find_element_by_id("usermenu")
        userDropdown.click()

    def open_datasets(self):
        myDatasetsLink = self.driver.find_element_by_link_text("My Datasets")
        myDatasetsLink.click()

        # datasets view
        header = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="component-title"]')))
        assert 'My datasets' in header.text
        createNewDataset = self.driver.find_element_by_id('datasets_button_create-new-record')
        createNewDataset.click()

        # new dataset view
        createDatasetHeader = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="component-title"]')))
        assert 'Dataset' in createDatasetHeader.text

    def logout(self):
        self.open_usermenu()
        signoutMenuItem = self.driver.find_element_by_id("usermenu_signout")
        signoutMenuItem.click()

    def close(self):
        self.driver.close()

    def print(self, message):
        self.logger.info(message)

    def tearDown(self):
        self.driver.quit()
        self.logger.removeHandler(self.stream_handler)

    def button_is_disabled(self, btn):
        assert "disabled" in btn.get_attribute("class")

    def button_is_enabled(self, btn):
        assert "disabled" not in btn.get_attribute("class")

    def elem_is_not_found(self, btnid):
        try:
            btn = self.driver.find_element_by_id(btnid)
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

    def open_dropdown(self, elemId):
        self.driver.find_element_by_id(elemId).find_element_by_class_name("dropdown-toggle").click()

    def select_dropdown_option(self, elemId, option):
        self.driver.find_element_by_id(elemId).find_element_by_class_name("dropdown-menu").find_element_by_partial_link_text(option).click()

    def select_option_from_multiselect(self, elemId, optionValue):
        elem = self.driver.find_element_by_id(elemId)
        multiselect = elem.find_element_by_class_name("multiselect")
        multiselect.click()
        multiselect_content = elem.find_element_by_class_name("multiselect__content")
        multiselect_options = multiselect_content.find_elements_by_class_name("multiselect__element")
        for option in multiselect_options:
            if option.text.find(optionValue) > -1:
                option.click()
                return
        raise NoSuchElementException("{option} was not found from {elem} ".format(option=optionValue, elem=elemId))


    def publish_and_save_buttons(self, save, publish, bottom_visible):
        saveButtons = []
        publishButtons = []

        saveButtons.append(self.driver.find_element_by_id("editor_button_save_top"))
        publishButtons.append(self.driver.find_element_by_id("editor_button_publish_top"))

        if bottom_visible:
            publishButtons.append(self.driver.find_element_by_id("editor_button_publish_bottom"))
            saveButtons.append(self.driver.find_element_by_id("editor_button_save_bottom"))
        else:
            assert self.elem_is_not_found("editor_button_publish_bottom")
            assert self.elem_is_not_found("editor_button_save_bottom")

        for btn in saveButtons:
            if save:
                self.button_is_enabled(btn)
            else:
                self.button_is_disabled(btn)

        for btn in publishButtons:
            if publish:
                self.button_is_enabled(btn)
            else:
                self.button_is_disabled(btn)