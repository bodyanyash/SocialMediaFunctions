import json
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

#Setup the selenium web driver
PATH = "chromedriver.exe.bak"
#options = Options()
#options.add_argument("--headless")
driver = webdriver.Chrome(PATH)

