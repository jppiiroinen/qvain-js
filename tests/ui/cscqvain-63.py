#!/usr/bin/env python3
################################################################
# This file contains functional tests for the CSCQAVAIN-63.
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

import sys
import os
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

    def test_2_datasets(self):
        self.print("datasets")
        self.login()
        self.open_datasets()

        # both buttons save and publish should be disabled
        # bottom buttons are not visible
        self.publish_and_save_buttons(publish=False, save=False, bottom_visible=False)

        # select remote uri as schema
        self.select_option("editor_select_schema", "I want to link Remote resources")

        # the bottom buttons should be now visible
        self.publish_and_save_buttons(publish=False, save=True, bottom_visible=True)

        # the user should be selected as owner by default
        assert self.is_option_selected("editor_select_owner", os.environ["TEST_FULLNAME"])

        # save button should be now enabled
        # publish button should be still disabled
        self.publish_and_save_buttons(publish=False, save=True, bottom_visible=True)

        # lets save the data once
        self.scroll_to_up()
        self.click_elem("editor_button_save_top")
        self.close_alert()

        # the publish button should be still disabled
        # save buttons are enabled
        self.publish_and_save_buttons(publish=False, save=True, bottom_visible=True)

        ###############################################
        #### Enter all the details for required fields

        ## Content Description
        self.scroll_to_up()
        self.click_elem("nav-link_description")

        # set title, select language to be english
        self.select_option("title_language-select", "English")
        self.enter_text("title_en_input", "Hello Title")

        # set description, select language to be english
        self.select_option("description_language-select", "English")
        self.enter_text("description_textarea-en", "A description for this test")

        # Save changes
        self.scroll_to_up()
        self.click_elem("editor_button_save_top")
        self.close_alert()

        ## Actors
        self.scroll_to_up()
        self.click_elem("nav-link_actors")

        # Creator of the dataset
        self.click_elem("creator_array_button_add")

        # add then an organization
        self.open_dropdown("creator_array_0_object")
        self.select_dropdown_option("creator_array_0_object", "Organization")
        self.select_option("name_language-select", "English")
        self.enter_text("name_en_input", "Test Organization")

        ## Rights and Licenses
        self.scroll_to_up()
        self.click_elem("nav-link_rights")

        # add the required rights and licenses information
        access_rights_object = self.driver.find_element_by_id("access_rights_object")
        self.select_option("description_language-select", "English")
        self.enter_text("description_en_input", "Test access rights description")

        # set access type to Open
        self.select_option_from_multiselect("access_type_object", "Open")

        # then save
        self.scroll_to_up()
        self.click_elem("editor_button_save_top")
        self.close_alert()

        # now the publish buttons are enabled and save button is disabled
        self.publish_and_save_buttons(publish=True, save=False, bottom_visible=True)

if __name__ == "__main__":
    unittest.main()
