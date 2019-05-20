#!/usr/bin/env python3
################################################################
# This file contains functional tests for the CSCQAVAIN-63.
#
# Author(s):
#     Juhapekka Piiroinen <juhapekka.piiroinen@csc.fi>
#
# (C) 2019 CSC
# All Rights Reserved.
################################################################

import sys
import os
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from qvaintestcase import QvainTestCase


class CSCQVAIN63(QvainTestCase):
    def test_1_login(self):
        self.login()

        # check that usermenu is visible
        self.open_usermenu()
        usermenu_fullname = self.driver.find_element_by_xpath('//*[@id="usermenu"]/div/h6/a')
        assert os.environ["TEST_FULLNAME"] in usermenu_fullname.text
        self.close_usermenu()

        self.logout()
        self.close()

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


    def test_2_datasets(self):
        self.login()
        self.open_datasets()

        newDatasetButton = self.driver.find_element_by_id("editor_button_new-dataset")
        publishButtonTop = self.driver.find_element_by_id("editor_button_publish_top")
        saveButtonTop = self.driver.find_element_by_id("editor_button_save_top")

        # both buttons save and publish should be disabled
        # bottom buttons are not visible
        self.publish_and_save_buttons(publish=False, save=False, bottom_visible=False)

        # select remote uri as schema
        selectedSchemaSelect = Select(self.driver.find_element_by_id("editor_select_schema"))
        selectedSchemaSelect.select_by_visible_text("I want to link Remote resources")

        # the bottom buttons should be now visible
        self.publish_and_save_buttons(publish=False, save=True, bottom_visible=True)

        # the user should be selected as owner by default
        ownerSelect = Select(self.driver.find_element_by_id("editor_select_owner"))
        assert os.environ["TEST_FULLNAME"] in ownerSelect.first_selected_option.text

        # save button should be now enabled
        # publish button should be still disabled
        self.publish_and_save_buttons(publish=False, save=True, bottom_visible=True)

        # lets save the data once
        saveButtonTop.click()

        # the publish button should be still disabled
        # save buttons are enabled
        self.publish_and_save_buttons(publish=False, save=True, bottom_visible=True)

        # TODO: insert required fields
        # TODO: then save
        # TODO: now the publish buttons are enabled

        self.close()


if __name__ == "__main__":
    unittest.main()
