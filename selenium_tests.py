from selenium import selenium
import unittest, time, re

class tests(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",
                4444,
                "*chrome",
                "http://localhost:8000/")
        self.selenium.start()
    
    def test_tests(self):
        sel = self.selenium
        sel.open("/login/")
        sel.type("id=id_username", "demohp")
        sel.type("id=id_password", "demohp")
        sel.click("//input[@id='login']")
        sel.wait_for_page_to_load("30000")
        sel.click("//section[@id='classes']/div/div/div/a")
        sel.wait_for_page_to_load("30000")
        # sel.()
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
