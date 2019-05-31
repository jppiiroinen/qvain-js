#!/usr/bin/env python3
################################################################
# This file contains the helper wrapper for My Datasets view.
#
# This file is part of Qvain project.
#
# Author(s):
#     Juhapekka Piiroinen <juhapekka.piiroinen@csc.fi>
#
# Copyright 2019 CSC - IT Center for Science Ltd.
# All Rights Reserved.
################################################################

import time


class Datasets(object):
    def __init__(self, testcase):
        self.testcase = testcase
        self.retries = 0
        self.set_input_language()
    
    def close(self):
        self.testcase.open_frontpage()

    def set_input_language(self, language="English", language_short="en"):
        self.language = language
        self.language_short = language_short

    def create(self):
        pass # TODO

    def remove_all(self):
        pass # TODO

    def search(self, title):
        # get the list of rows
        dataset_list = self.testcase.find_element("dataset-list")
        dataset_rows = dataset_list.find_elements_by_css_selector("tbody > tr")

        # we need to cancel the special case when the data is loading
        # there is an UI issue where "There are no records to show" is shown.
        if len(dataset_rows) == 1:
            if self.retries > 5:
                self.retries = 0
                return False
            time.sleep(1)
            self.retries += 1
            return self.search(title)

        # lets see those titles if we can find any
        found = []
        for row in dataset_rows:
            if row.find_elements_by_css_selector("td")[1].find_element_by_css_selector("h5").text == title:
                found.append(row.get_attribute("id").replace("dataset-list__row_", ""))
        return found

    def exists(self, dataset_id):
        return self.testcase.elem_is_not_found("dataset-list__row_{id}".format(id=dataset_id))

    def remove(self, dataset_id):
        self.testcase.print("Requested removal of {id}".format(id=dataset_id))
        pass # TODO

    def edit(self, dataset_id):
        pass # TODO

    def view_in_etsin(self, dataset_id):
        pass # TODO

    def list_all(self):
        pass # TODO

    def show(self):
        self.testcase.open_frontpage()
        # lets tap the navigation bar where we should see the link
        self.testcase.find_element_by_text("My Datasets").click()

        # lets wait until the page has been loaded
        self.testcase.ensure_view_title(
            title='My datasets',
            error_msg="We are not in My datasets view, it seems that we are in {header}"
        )

        
