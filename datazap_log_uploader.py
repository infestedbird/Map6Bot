# how to use:
# 1. get selenium ("pip-install selenium")
# 2. get webdriver-manager ("pip-install webdriver-manager")
# 3. copy this file into the directory of your main script
# 4. import it ("import datazap_log_uploader.py")
# 5. run the function upload_log
# upload_log takes 5 arguments:
# log_path - path to .csv file for the log to be uploaded
# log title - title of the log to be displayed
# log notes - notes associated with the log
# account name - the account name or email address you use to log into datazap
# password - the password for the account
#
# upload_log will return either the URL of the uploaded log or a notification
# that the upload process failed. exception details, if there are any, will be
# printed to the console.

import traceback
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def upload_log(log_path2, log_title, log_notes, account_name, password):
    print(log_path2)
    log_path = "/home/pi/map6/%s" % (log_path2)

    try:
        # scrub the log VIN
        scrub_vin(log_path)

        # get the most recent webdriver for chrome and set up headless mode
        options = webdriver.ChromeOptions()
        options.headless = True
        options.binary_location = "/usr/bin/chromium-browser"
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver' , options=options)

        # wait up to 10 seconds for necessary elements to load
        wait = WebDriverWait(driver, 10)

        # browse to login field
        driver.get("https://datazap.me/login")
        # wait until everything is loaded up
        account_name_field = wait.until(EC.presence_of_element_located((By.ID, "edit-name")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "edit-pass")))
        assert "datazap.me" in driver.title
        # input our user name and password and then move on
        account_name_field.send_keys(account_name)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        # wait for everything to load so we can nab the username
        username_display = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "user-profile-list-name")))
        username = username_display.text.replace("USER SETTINGS", "").strip()

        # browse to the upload page
        driver.get("https://datazap.me/upload-csv")
        # wait until everything is loaded up
        log_select_field = wait.until(EC.presence_of_element_located((By.ID, "droppable-field-datalog-file-csv-und-0")))
        log_title_field = wait.until(EC.presence_of_element_located((By.ID, "edit-title")))
        log_notes_field = wait.until(EC.presence_of_element_located((By.ID, "edit-body-und-0-value")))
        log_submit_button = wait.until(EC.presence_of_element_located((By.ID, "edit-submit")))
        # drop our log on the dialog
        drag_and_drop_file(log_select_field, log_path)
        # wait for the page to update and make sure our log got added before we input the rest of the information
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "file-widget")))
        time.sleep(2)
        log_title_field.send_keys(log_title)
        log_notes_field.send_keys(log_notes)
        log_submit_button.send_keys(Keys.RETURN)
        # wait until the log is finished uploading and we've been redirected so we can grab the log URL
        wait.until(EC.title_contains(username))
        # trim the log url down if we didn't catch it in time before the scripts started
        log_url = driver.current_url.partition('?')[0]
        driver.quit()
        return log_url

    except Exception:
        traceback.print_exc()
        driver.quit()
        return "Oops! datazap upload failed."


def drag_and_drop_file(drop_target, path):
    driver = drop_target.parent
    file_input = driver.execute_script(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(path)

def scrub_vin(log_path):
    log_file = open(log_path, "r+")
    log = log_file.read()
    log_file.seek(0)
    log_file.truncate()
    log_file.write(re.sub(r',[0-9A-Z]{12},', ",(none),", log))



JS_DROP_FILE = """
    var target = arguments[0],
        offsetX = arguments[1],
        offsetY = arguments[2],
        document = target.ownerDocument || document,
        window = document.defaultView || window;

    var input = document.createElement('INPUT');
    input.type = 'file';
    input.onchange = function () {
      var rect = target.getBoundingClientRect(),
          x = rect.left + (offsetX || (rect.width / 2)),
          y = rect.top + (offsetY || (rect.height / 2)),
          dataTransfer = { files: this.files };

      ['dragenter', 'dragover', 'drop'].forEach(function (name) {
        var evt = document.createEvent('MouseEvent');
        evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
        evt.dataTransfer = dataTransfer;
        target.dispatchEvent(evt);
      });

      setTimeout(function () { document.body.removeChild(input); }, 25);
    };
    document.body.appendChild(input);
    return input;
"""
