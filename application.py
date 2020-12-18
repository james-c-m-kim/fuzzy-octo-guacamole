import sys
import time
import random

import getpass

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import pandas as pd

class LinkedinScrapper():
    browser = None
    contact_cards = []
    profiles = {}

    login = ""
    password = ""

    def __init__(self, path_to_exec):
        self.browser = webdriver.Chrome(executable_path=path_to_exec)

    def perform_login(self):
        login_field = self.browser.find_element_by_id("session_key")
        password_field = self.browser.find_element_by_id("session_password")
        submit_btn = self.browser.find_element_by_class_name("sign-in-form__submit-button")

        self.browser.minimize_window()

        self.login = input("Type your Linkedin email here: ")
        self.password = getpass.getpass(prompt="Type your Linkedin password on the hidden field...")

        self.browser.maximize_window()

        login_field.send_keys(self.login)
        password_field.send_keys(self.password)
        submit_btn.submit()
        self.browser.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")

    def load_connections(self):
        contact_card_class = "mn-connection-card"
        self.contact_cards = self.browser.find_elements_by_class_name(contact_card_class)

    # just name, email, phone number (if available), company name, current job
    def extract_info_and_save(self, contact_card):
        link_class_name = "mn-connection-card__picture"
        info = {}
        body = self.browser.find_element_by_tag_name("body")
        
        card_link = contact_card.find_element_by_class_name(link_class_name)
        link_address = card_link.get_attribute("href")

        self.browser.execute_script("window.open('');")
        self.browser.switch_to.window(self.browser.window_handles[1])
        self.browser.get(link_address + "detail/contact-info/")
        info["name"] = self.browser.find_element_by_id("pv-contact-info").text
        try:
            info["email"] = self.browser.find_element_by_xpath("//a[contains(@href, 'mailto')]").text
            info["occupation"] = self.browser.find_element_by_xpath("//h2[contains(@class, 'mt1 t-18 t-black t-normal break-words')]").text
            info["company name"] = self.browser.find_element_by_xpath("//span[contains(@class, 'text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view')]").text
            info["phone number"] = self.browser.find_element_by_xpath("//li[contains(@class, 'pv-contact-info__ci-container t-14')]/span[contains(@class, 't-14 t-black t-normal')]").text
        except:
            pass
        self.browser.close()
        self.browser.switch_to.window(self.browser.window_handles[0])

        self.profiles[info["name"]] = info

    def save_data(self):
        sheet = pd.DataFrame(self.profiles)
        sheet = sheet.T
        sheet.to_csv("contacts.csv")
        self.browser.quit()

    def begin_extract_info(self):
        lastCount = 0
        count = len(self.contact_cards)
        while True:
            if count == lastCount:
                break
            self.browser.find_element_by_tag_name("body").send_keys(Keys.END)
            self.load_connections()
            for idx in range(len(self.contact_cards)):
                contact_card = self.contact_cards[idx]

                self.extract_info_and_save(contact_card)
            lastCount = count
            count = len(self.contact_cards)
            
        self.save_data()

    def run(self):
        self.browser.get("https://linkedin.com")

        self.perform_login()
        self.load_connections()
        self.begin_extract_info()

if __name__ == "__main__":
    app = LinkedinScrapper(sys.argv[1])
    app.run()
