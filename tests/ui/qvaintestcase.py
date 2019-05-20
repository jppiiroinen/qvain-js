#!/usr/bin/env python3
################################################################
#
# Author(s): Juhapekka Piiroinen <juhapekka.piiroinen@csc.fi>
#
# (C) 2019 CSC
# All Rights Reserved.
################################################################

import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
import os


class QvainTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome("./chromedriver")
        self.wait = WebDriverWait(self.driver, 10)

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

    def tearDown(self):
        self.driver.quit()

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
