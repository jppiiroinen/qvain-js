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
        saveButtonTop = self.driver.find_element_by_id("editor_button_save_top")
        saveButtonTop.click()

        # the publish button should be still disabled
        # save buttons are enabled
        self.publish_and_save_buttons(publish=False, save=True, bottom_visible=True)

        ###############################################
        #### Enter all the details for required fields

        ## Content Description
        navLinkContentDescription = self.driver.find_element_by_id("nav-link_description")
        navLinkContentDescription.click()

        # set title, select language to be english
        titleLanguageSelect = Select(self.driver.find_element_by_id("title_language-select"))
        titleLanguageSelect.select_by_visible_text("English")

        titleInputEnglish = self.driver.find_element_by_id("title_en_input")
        titleInputEnglish.send_keys("Hello Title")

        # set description, select language to be english
        descriptionLanguageSelect = Select(self.driver.find_element_by_id("description_language-select"))
        descriptionLanguageSelect.select_by_visible_text("English")

        descriptionTextAreaEnglish = self.driver.find_element_by_id("description_textarea-en")
        descriptionTextAreaEnglish.send_keys("A description for this test")

        # Save changes
        saveButtonTop.click()

        # Close alert
        self.close_alert()

        ## Actors
        navLinkActors = self.driver.find_element_by_id("nav-link_actors")
        navLinkActors.click()

        # Creator of the dataset
        creator_recordField_button_add = self.driver.find_element_by_id("creator_array_button_add")
        creator_recordField_button_add.click()

        # add then an organization
        creator_chooseType_button = self.driver.find_element_by_id("creator_array_0_oneOf").find_element_by_class_name("dropdown-toggle")
        creator_chooseType_button.click()

        organization_dropdown_option = self.driver.find_element_by_id("creator_array_0_oneOf").find_element_by_class_name("dropdown-menu").find_element_by_partial_link_text("Organizatio")
        organization_dropdown_option.click()

        organization_name_language = Select(self.driver.find_element_by_id("name_language-select"))
        organization_name_language.select_by_visible_text("English")
        organization_name_input = self.driver.find_element_by_id("name_en_input")
        organization_name_input.send_keys("Test Organization")

        ## Rights and Licenses
        self.scroll_to_up()
        navLinkRights = self.driver.find_element_by_id("nav-link_rights")
        navLinkRights.click()

        # TODO: add the required rights and licenses information

        access_rights_object = self.driver.find_element_by_id("access_rights_object")
        access_rights_description_language_select = Select(access_rights_object.find_element_by_id("description_language-select"))
        access_rights_description_language_select.select_by_visible_text("English")
        access_rights_description_input = access_rights_object.find_element_by_id("description_en_input")
        access_rights_description_input.send_keys("Test access rights description")

        access_type_tab_selector = self.driver.find_element_by_id("access_type_tab-selector")
        access_type_tab_selector_multiselect = access_type_tab_selector.find_element_by_class_name("multiselect__tags")
        access_type_tab_selector_multiselect.click()

        # TODO: select value from the multiselect

        # TODO: then save
        # TODO: now the publish buttons are enabled

        self.close()


if __name__ == "__main__":
    unittest.main()
