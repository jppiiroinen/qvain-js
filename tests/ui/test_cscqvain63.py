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
# All Rights Reserved.
################################################################

import sys
import os
import time
import unittest

from qvaintestcase import QvainTestCase

from views.editor import Editor
from views.datasets import Datasets


class CSCQVAIN63(QvainTestCase):
    def start_test(self):
        self.login()
        self.verify_that_user_is_logged_in()
        self.start_memory_measure()

    def end_test(self):
        if self.memory_usage_at_start:
            self.end_memory_measure_and_report()
        self.logout()
        self.close()

    def test_1_my_datasets(self):
        self.start_test()

        # ensure that the test datasets does not exist before create.
        datasets = Datasets(self)
        datasets.show()
        test_datasets = [
            "test_1_my_datasets_valid_unpublished",
            "test_1_my_datasets_invalid_unpublished"
        ]
        for test_dataset in test_datasets:
            dataset_ids = datasets.search(test_dataset)
            for dataset_id in dataset_ids:
                datasets.remove(dataset_id)
        datasets.close()
        
        ## create a new dataset
        # valid dataset, unpublished
        self.mark_memory_measure("created valid unpublished dataset")
        editor = Editor(self)
        editor.show()
        editor.select_schema("I want to link Remote resources")
        editor.show_content_description_tab()
        editor.set_title("test_1_my_datasets_valid_unpublished")
        editor.set_description("dataset description")
        editor.show_actors_tab()
        editor.set_creator_organization("Test Organization")
        editor.show_rights_and_licenses_tab()
        editor.set_access_rights_description("Test Access Rights Description")
        editor.set_access_type("Open")
        (test_1_my_datasets_valid_unpublished_id, was_resave) = editor.save()
        assert was_resave == False, "Expected to see first time save"
        self.diff_memory_measure_and_report("created valid unpublished dataset")
        editor.close()

        # invalid dataset, unpublished
        self.mark_memory_measure("created invalid unpublished dataset")
        editor.show()
        editor.select_schema("I want to link Remote resources")
        editor.show_content_description_tab()
        editor.set_title("test_1_my_datasets_invalid_unpublished")
        editor.set_description("dataset description")
        (test_1_my_datasets_invalid_unpublished_id, was_resave) = editor.save()
        assert was_resave == False, "Expected to see first time save"
        self.diff_memory_measure_and_report("created invalid unpublished dataset")

        # test that the buttons are shown correctly and that the status is correct
        datasets.show()

        # we need to do a workaround for the loading bug
        retries = 0
        while retries < 5:
            if (self.elem_is_not_found("test_1_my_datasets_invalid_unpublished")):
                break
            time.sleep(0.5)
            retries += 1
        assert retries < 5, "The datasets could not be loaded"

        dataset_ids = datasets.search("test_1_my_datasets_invalid_unpublished")
        assert len(dataset_ids) == 1, "There should be only one test_1_my_datasets_invalid_unpublished"

        # ensure that publish button is visible for both unpublished cases
        test_ids = [ test_1_my_datasets_valid_unpublished_id, test_1_my_datasets_invalid_unpublished_id ]
        for test_id in test_ids:
            self.print(test_id)
            # scroll to the item
            datasets.scroll_list_to(test_id)

            # if state is Draft then publish button should be enabled.
            assert datasets.is_draft(test_id), "It seems that state is other than draft for {id}".format(id=test_id)

            # the unpublished dataset should have Publish button enabled
            assert datasets.is_publish_visible(test_id), "Publish button should be visible for {id}".format(id=test_id)
        
        # edit one dataset
        datasets.edit(test_1_my_datasets_valid_unpublished_id)

        # publish that dataset
        ## TODO: record the RPC traffic?
        assert editor.publish(), "Publish was failed"
        test_1_my_datasets_valid_published_id = test_1_my_datasets_valid_unpublished_id

        # if published then there should not be Publish button
        datasets.show()
        datasets.scroll_list_to(test_1_my_datasets_valid_published_id)
        assert datasets.is_published(test_1_my_datasets_valid_published_id), "The state should be Published for {id}, but was {state}".format(id=test_1_my_datasets_valid_published_id, state=datasets.get_state(test_1_my_datasets_valid_published_id))
        assert not datasets.is_publish_visible(test_1_my_datasets_valid_published_id), "Publish button should be hidden for {id}".format(id=test_1_my_datasets_valid_published_id)

        # edit the same dataset
        datasets.edit(test_1_my_datasets_valid_published_id)

        editor.set_description("a changed description")

        # just save, no publish
        editor.save()
        test_1_my_datasets_valid_published_pending_changes_id = test_1_my_datasets_valid_published_id

        # if published but the data has been changed, the state should be unpublished changes
        # and publish button should be visible.
        datasets.show()
        datasets.scroll_list_to(test_1_my_datasets_valid_published_id)
        assert datasets.is_pending_changes(test_1_my_datasets_valid_published_id), "The state should be Pending Changes {id}, but was {state}".format(id=test_1_my_datasets_valid_published_id, state=datasets.get_state(test_1_my_datasets_valid_published_id))
        assert datasets.is_publish_visible(test_1_my_datasets_valid_published_id), "Publish button should be visible for {id}".format(id=test_1_my_datasets_valid_published_id)


    def test_2_create_new_dataset(self):
        self.start_test()
        editor = Editor(self)
        self.with_memory_usage("Editor page is shown",
            editor.show
        )
        editor.set_input_language("English", "en")

        # both buttons save and publish should be disabled
        # bottom buttons are not visible
        editor.verify_publish_and_save_buttons(publish=False, save=False, bottom_visible=False)

        # select remote uri as schema
        self.with_memory_usage("Schema is selected",
            editor.select_schema,
            "I want to link Remote resources"
        )

        # the bottom buttons should be now visible
        editor.verify_publish_and_save_buttons(publish=False, save=True, bottom_visible=True)

        # the user should be selected as owner by default
        editor.verify_owner(os.environ["TEST_FULLNAME"])

        # save button should be now enabled
        # publish button should be still disabled
        editor.verify_publish_and_save_buttons(publish=False, save=True, bottom_visible=True)

        # lets save the data once
        self.with_memory_usage("Data saved",
            editor.save
        )

        # the publish button should be still disabled
        # save buttons are enabled
        editor.verify_publish_and_save_buttons(publish=False, save=True, bottom_visible=True)

        ###############################################
        #### Enter all the details for required fields

        ## Content Description
        self.with_memory_usage("Content Description tab",
            editor.show_content_description_tab
        )

        # set title
        self.with_memory_usage("Title is set",
            editor.set_title,
            "Hello Title"
        )

        # set description
        self.with_memory_usage("Description is set",
            editor.set_description,
            "A description for this test"
        )

        # Save changes
        self.with_memory_usage("Data is saved",
            editor.save
        )

        ## Actors
        self.with_memory_usage("Actors tab",
            editor.show_actors_tab
        )

        # add then an organization
        self.with_memory_usage("Organization is set",
            editor.set_creator_organization,
            "Test Organization"
        )

        ## Rights and Licenses
        self.with_memory_usage("Rights and licenses tab",
            editor.show_rights_and_licenses_tab
        )

        # add the required rights and licenses information
        self.with_memory_usage("Access rights description is set",
            editor.set_access_rights_description,
            "Test access rights description"
        )

        # set access type to Open
        self.with_memory_usage("Access type is set",
            editor.set_access_type,
            "Open"
        )

        # then save
        self.with_memory_usage("Data is saved",
            editor.save
        )

        # now the publish buttons are enabled and save button is disabled
        editor.verify_publish_and_save_buttons(publish=True, save=False, bottom_visible=True)


if __name__ == "__main__":
    unittest.main()
