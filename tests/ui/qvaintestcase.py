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
# All Rights Reserved.
################################################################

import os
import sys
import logging
import unittest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class QvainTestCase(unittest.TestCase):
    def setUp(self):
        self.memory_usage_at_start = None
        self.test_events = []
        self.start_time = int(time.time())
        self.netlogfile = "{testcase}-{testmethod}-{timestamp}-networktraffic.json".format(timestamp=self.start_time, testcase=self.__class__.__name__, testmethod=self._testMethodName)
        self.netlogfiles.append(self.netlogfile)

        caps = DesiredCapabilities.CHROME.copy()
        caps['loggingPrefs'] = {
            'browser': 'ALL',
            'performance' : 'ALL',
            }

        # This data can be processed, the logs for V8 with:
        # chrome://tracing/
        # and another useful place is
        # chrome://memory-internals/
        opts = webdriver.ChromeOptions()
        opts.add_argument("--no-sandbox")
        #opts.add_experimental_option('perfLoggingPrefs', {
        #    'enableNetwork' : True,
        #    'enablePage' : True,
        #    'traceCategories': "browser,devtools.timeline,devtools",
        #    })
        opts.add_argument("--js-flags=--expose-gc") # --prof --track-gc-object-stats --trace-track-allocation-sites --log-all --heap-profiler-trace-objects --trace-detached-contexts --track-heap-object-fields --stack-trace-limit=10 --allow-natives-syntax --track-retaining-path --track_gc_object_stats --trace_gc_verbose --log_timer_events  --log-internal-timer-events --logfile=v8-%p.log")
        if not "TEST_DEBUG" in os.environ.keys():
            opts.add_argument("--headless")
        opts.add_argument("--enable-precise-memory-info")
        opts.add_argument("--log-net-log={netlogfile}".format(netlogfile=self.netlogfile))
        opts.add_argument("--net-log-capture-mode=IncludeSocketBytes")
        #opts.add_argument("--net-log-capture-mode=IncludeCookiesAndCredentials")

        ##opts.add_argument("--trace-startup=disabled-by-default-memory-infra")
        #opts.add_argument("--trace-startup-file=trace-%p.json")
        #opts.add_argument("--trace-startup-duration=7")
#        opts.add_argument("--disable-dev-shm-usage")
        #opts.add_argument("--enable-heap-profiling=task-profiler")
        #opts.add_argument("--profiling-flush")
#        opts.add_experimental_option("useAutomationExtension", False);
        #opts.add_argument("--trace-config-file=trace.config")
        self.test_start_time = time.time() + 1.25
        self.driver = webdriver.Chrome("./chromedriver", options=opts, desired_capabilities=caps)
        self.wait = WebDriverWait(self.driver, 10)

    def with_memory_usage(self, description, fn, *args, **kwargs):
        self.mark_memory_measure(description)
        fn(*args, **kwargs)
        self.diff_memory_measure_and_report(description)

    def start_memory_measure(self, description=None):
        if not description:
            description = "BEGIN"
        timestamp = time.time() - self.test_start_time
        self.memory_usage_at_start = int(self.memory_usage())
        self.test_events.append((timestamp, "{id} | {msg}".format(
            id=self.id(),
            msg=description
        )))

    def end_memory_measure_and_report(self, description=None):
        if not description:
            description = "END"
        timestamp = time.time() - self.test_start_time
        memory_diff, memory_end, memory_start = self.end_memory_measure()
        self.test_events.append((timestamp, "{id} | {msg} | JS Memory start: {start}Kb | end: {end}Kb | diff: {diff}Kb".format(
            id=self.id(),
            msg=description,
            start=int(memory_start/1024),
            end=int(memory_end/1024),
            diff=int(memory_diff/1024)
        )))

    def end_memory_measure(self):
        currentMemoryUsage = int(self.memory_usage())
        return currentMemoryUsage - self.memory_usage_at_start, currentMemoryUsage, self.memory_usage_at_start

    def mark_memory_measure(self, description):
        timestamp = time.time() - self.test_start_time
        self.memory_usage_at_mark = int(self.memory_usage())
        self.test_events.append((timestamp, "{id} | {msg}".format(
            id=self.id(),
            msg=description
        )))

    def diff_memory_measure(self):
        currentMemoryUsage = int(self.memory_usage())
        return currentMemoryUsage - self.memory_usage_at_mark, currentMemoryUsage, self.memory_usage_at_mark

    def diff_memory_measure_and_report(self, msg=None):
        timestamp = time.time() - self.test_start_time
        memory_diff, memory_end, memory_start = self.diff_memory_measure()
        self.test_events.append((timestamp, "{id} | {msg} | JS Memory start: {start}Kb | end: {end}Kb | diff: {diff}Kb".format(
            id=self.id(),
            msg=msg,
            start=int(memory_start/1024),
            end=int(memory_end/1024),
            diff=int(memory_diff/1024)
        )))

    def memory_usage(self):
        self.driver.execute_script("window.gc()")
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
        try:
            self.wait.until(EC.title_is("Login"))
            login_button_container = self.driver.find_element_by_class_name("login-button-container")
            loginHakaTestBtn = login_button_container.find_elements_by_class_name("login-link")[1]
        except TimeoutException:
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

    def open_frontpage(self):
        ## The top does not actually get you to the frontpage
        # appTopBarImage = self.driver.find_element_by_xpath('//*[@id="app-topbar"]/a/img')
        # appTopBarImage.click()
        self.driver.get(os.environ["TEST_ADDRESS"])
        self.is_frontend_running()
        self.wait.until(EC.title_is("Qvain"))

    def logout(self):
        if self.elem_is_not_found("usermenu"):
            return
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

    def run(self, result=None):
        self.netlogfiles = []
        self.logger = logging.getLogger()
        self.logger.level = logging.INFO
        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(self.stream_handler)

        super().run(result)

        ## analyze netlog
        #if len(result.errors) > 0 or len(result.failures) > 0:
        for logfile in self.netlogfiles:
            print("")
            print("======================================================================")
            print("Test Report: " + self.id())
            print("----------------------------------------------------------------------")
            test_events_with_network = self.parse_netlog(logfile) + self.test_events
            test_events_with_network = sorted(test_events_with_network, key=lambda evt: evt[0])
            for event in test_events_with_network:
                print("{time:8.3f} | {data}".format(time=event[0], data=event[1]))
            print("\n")
        self.logger.removeHandler(self.stream_handler)

    def tearDown(self):
        if self.end_test:
            self.end_test()
        self.driver.quit()
        self.test_start_time = None

    def parse_netlog(self, netlog):
        retval = []
        data = ""
        with open(netlog, "r") as f:
            data += f.read()
        data = data.strip().rstrip(",")
        try:
            structure = json.loads(data + "]}")
        except json.decoder.JSONDecodeError:
            structure = json.loads(data)
        first_time = -1
        for event in structure['events']:
            if first_time == -1:
                first_time = int(event['time'])
            if event['source']['type'] == 1:
                if event['type'] == 166:
                    header = event['params']['headers']
                    headerdict = {}
                    for line in header:
                        if line.find(":") == 0:
                            line = line[1:]
                        (key, value) = line.split(":", 1)
                        headerdict[key] = value.strip()
                    actual_time = (int(event['time']) - first_time) / 1000
                    retval.append((actual_time," => " + headerdict["method"] + " " + headerdict['scheme']  + " " + headerdict['authority'] + " " + headerdict['path']))
            if event['type'] == 101:
                location = event['params']['location']
                actual_time = (int(event['time']) - first_time) / 1000
                retval.append((actual_time, " URL CHANGED " + location))
            if event['type'] == 169:
                header = event['params']['headers']
                headerdict = {}
                for line in header:
                    try:
                        (key, value) = line.split(":", 1)
                        headerdict[key] = value
                    except:
                        pass
                if "location" in headerdict.keys():
                    actual_time = (int(event['time']) - first_time) / 1000
                    retval.append((actual_time,"REDIRECTED TO " + headerdict["location"]))
        return retval

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

    def is_element_visible(self, elemId):
        return self.find_element(elemId).is_displayed()

    def wait_until_clickable_by_class(self, parent, class_name):
        return self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))

    def get_alert_text(self):
        #<div role="alert" aria-live="polite" aria-atomic="true" class="alert alert-primary alert-dismissible" id="root_alert" style="z-index: 1000; position: fixed; top: 1rem; left: 0px; right: 0px; width: 90%; margin: 0px auto; opacity: 0.9;">
        # <button type="button" aria-label="Close" class="close">×</button>
        # <p>Dataset successfully saved</p>
        #</div>
        #
        alertTextElem = self.wait.until(EC.presence_of_element_located((By.ID, 'root_alert'))).find_element_by_css_selector("p")
        return alertTextElem.text

    def click_elem(self, elemId):
        self.driver.find_element_by_id(elemId).click()

    def select_option(self, elemId, option):
        selectBox = Select(self.driver.find_element_by_id(elemId))
        selectBox.select_by_visible_text(option)

    def is_option_selected(self, elemId, option):
        selectBox = Select(self.driver.find_element_by_id(elemId))
        return option in selectBox.first_selected_option.text

    def ensure_view_title(self, title, error_msg):
        header = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="component-title"]')))
        assert title in header.text, error_msg.format(header=header.text)

    def enter_text(self, elemId, text):
        elem = self.driver.find_element_by_id(elemId)
        elem.click()
        elem.send_keys(text)
        elem.send_keys(Keys.TAB)

    def wait_until_visible(self, elemId):
        self.wait.until(EC.visibility_of(self.find_element(elemId)))

    def clear_text(self, elemId):
        self.driver.find_element_by_id(elemId).clear()

    def find_element(self, elemId):
        return self.wait.until(EC.presence_of_element_located((By.ID, elemId)))

    def find_element_by_text(self, text):
        return self.driver.find_element_by_link_text(text)

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

        tries = 5
        errors = []
        while tries > 0:
            tries -= 1
            multiselect_options = multiselect_content.find_elements_by_class_name("multiselect__element")

            # this can fail when the network connection is not working properly.
            # so lets ensure that we did get more than zero options
            if len(multiselect_options) == 0:
                errors.append("We did not find any options from the multiselect")
                time.sleep(1.0)
                continue

            # lets find the option from the list of found options
            for option in multiselect_options:
                if option.text.find(optionValue) > -1:
                    # once we found it we click on it
                    self.wait.until(EC.visibility_of(option))
                    option.click()
                    return

            errors.append("Unable to find " + optionValue)
            time.sleep(1.0)

        # we did not find the option from the list
        raise NoSuchElementException("{option} was not found from {elem} ".format(option=optionValue, elem=elemId))

