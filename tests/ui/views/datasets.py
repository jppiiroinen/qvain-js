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


class Datasets(object):
    def __init__(self, testcase):
        self.testcase = testcase
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

    def exists(self, title):
        return self.testcase.find_element_by_text(title)

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
