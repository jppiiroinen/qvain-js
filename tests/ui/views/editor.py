#!/usr/bin/env python3
################################################################
# This file contains the helper wrapper for Editor view.
#
# This file is part of Qvain project.
#
# Author(s):
#     Juhapekka Piiroinen <juhapekka.piiroinen@csc.fi>
#
# Copyright 2019 CSC - IT Center for Science Ltd.
# All Rights Reserved.
################################################################

from .datasets import Datasets


class Editor(object):
    def __init__(self, testcase):
        self.testcase = testcase
        self.dataset_id = None
        self.set_input_language()

    def set_input_language(self, language="English", language_short="en"):
        self.language = language
        self.language_short = language_short

    def show(self):
        self.testcase.open_frontpage()
        datasets = Datasets(self.testcase)
        datasets.show()

        # lets tap on the create new record button
        self.testcase.find_element('datasets_button_create-new-record').click()

        # we should end up into new dataset page
        self.testcase.ensure_view_title(
            title="Dataset",
            error_msg="We are not in Dataset view, it seems that we are in {header}"
        )

    def close(self):
        self.dataset_id = None
        self.testcase.open_frontpage()

    def select_schema(self, schema):
        self.testcase.select_option("editor_select_schema", schema)

    def save(self):
        self.testcase.scroll_to_up()
        self.testcase.click_elem("editor_button_save_top")
        # If this is a save of an old item then the message is
        #  "Dataset successfully saved"
        # if this is a new save then the message is
        #  "Success! Created as 0589ec6d4452eeae99c0647346f98e40"
        alert_text = self.testcase.get_alert_text()
        resave = True
        if (alert_text.find("Created as") != -1):
            self.testcase.print("was a new save")
            self.dataset_id = alert_text.replace("Success! Created as ","")
            resave = False
        self.testcase.print(alert_text)
        self.testcase.close_alert()
        return self.dataset_id, resave

    def show_content_description_tab(self):
        self.testcase.scroll_to_up()
        self.testcase.click_elem("nav-link_description")

    def show_actors_tab(self):
        self.testcase.scroll_to_up()
        self.testcase.click_elem("nav-link_actors")

    def show_rights_and_licenses_tab(self):
        self.testcase.scroll_to_up()
        self.testcase.click_elem("nav-link_rights")

    def set_title(self, title):
        self.testcase.select_option("title_language-select", self.language)
        self.testcase.enter_text(
            "title_{language_short}_input".format(language_short=self.language_short),
            title
        )

    def set_description(self, description):
        self.testcase.select_option("description_language-select", self.language)
        self.testcase.enter_text(
            "description_textarea-{language_short}".format(language_short=self.language_short),
            description
        )

    def set_creator_organization(self, organizationName):
        # Creator of the dataset
        self.testcase.click_elem("creator_array_button_add")

        # add then an organization
        self.testcase.open_dropdown("creator_array_0_object")
        self.testcase.select_dropdown_option("creator_array_0_object", "Organization")
        self.testcase.select_option("name_language-select", self.language)
        self.testcase.enter_text("name_{language_short}_input".format(language_short=self.language_short), organizationName)

    def set_access_rights_description(self, accessRightsDescription):
        access_rights_object = self.testcase.find_element("access_rights_object")
        self.testcase.select_option("description_language-select", self.language)
        self.testcase.enter_text("description_{language_short}_input".format(language_short=self.language_short), accessRightsDescription)

    def set_access_type(self, access_type):
        self.testcase.select_option_from_multiselect("access_type_object", "Open")

    def verify_owner(self, owner):
        assert self.testcase.is_option_selected(
                    "editor_select_owner",
                    owner
                ), "The currently logged in user is not marked as owner of the dataset."

    def verify_publish_and_save_buttons(self, save, publish, bottom_visible):
        saveButtons = []
        publishButtons = []

        saveButtons.append(self.testcase.find_element("editor_button_save_top"))
        publishButtons.append(self.testcase.find_element("editor_button_publish_top"))

        if bottom_visible:
            publishButtons.append(self.testcase.find_element("editor_button_publish_bottom"))
            saveButtons.append(self.testcase.find_element("editor_button_save_bottom"))
        else:
            assert self.testcase.elem_is_not_found("editor_button_publish_bottom"), "editor_button_publish_bottom was visible"
            assert self.testcase.elem_is_not_found("editor_button_save_bottom"), "editor_button_save_bottom was visible"

        for btn in saveButtons:
            if save:
                self.testcase.button_is_enabled(btn)
            else:
                self.testcase.button_is_disabled(btn)

        for btn in publishButtons:
            if publish:
                self.testcase.button_is_enabled(btn)
            else:
                self.testcase.button_is_disabled(btn)