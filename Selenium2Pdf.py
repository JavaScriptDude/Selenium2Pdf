# Selenium2Pdf.py - Basic example of using Selenium to Generate PDF
#                   which includes page formatting, headers, footers
# Dependencies
# * python3 -m pip install selenium==4.1.3
# * Download and place or create symlink to chromedriver in current directory
#    URL: (http://chromedriver.chromium.org/)
# Author: Timothy.c.quinn@gmail.com (https://github.com/JavaScriptDude)
# License: MIT

import sys
import os
import json
import base64
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def main(args):
  # sw = StopWatch()
  url = 'https://www.google.com'
  out_file = f'z_test_{datetime.now().strftime("%y%m%d-%H%M%S.%f")}.pdf'
  out_path = os.path.split(sys.argv[0])[0]
  if out_path == '': out_path = os.getcwd()

  out_path_full = f"{out_path}/{out_file}"

  wd_dcap = webdriver.DesiredCapabilities.CHROME.copy()

  wd_opts = webdriver.chrome.options.Options()
  # Note: headless must be enabled for PDF to avoid the
  #       ambiguous 'Printing is not available' error.
  wd_opts.add_argument('--headless')
  wd_opts.add_argument('--disable-gpu')

  chr_svc = webdriver.chrome.service.Service('./chromedriver')

  with webdriver.Chrome(service=chr_svc, options=wd_opts, desired_capabilities=wd_dcap) as driver:
    driver.get(url)

    # (optional) Wait for document.readyState = complete
    # WebDriverWait(driver, timeout=5, poll_frequency=0.5).until(_waitForDocReady)

    assert driver.page_source != '<html><head></head><body></body></html>' \
              ,f"Url could not be loaded: {url}"

    result = send_cmd(driver, "Page.printToPDF", params={
             'landscape': True
            ,'margin':{'top':'1cm', 'right':'1cm', 'bottom':'1cm', 'left':'1cm'}
            ,'format': 'A4'
            ,'displayHeaderFooter': True
            ,'headerTemplate': '<span style="font-size:8px; margin-left: 5px">Page 1 of 1</span>'
            ,'footerTemplate': f'<span style="font-size:8px; margin-left: 5px">Generated on {datetime.now().strftime("%m/%d/%Y at %H:%M")}</span>'
            ,'scale': 1.65
            ,'pageRanges': '1'
    })

    with open(out_path_full, 'wb') as file:
        file.write(base64.b64decode(result['data']))

  if not os.path.isfile(out_path_full):
    raise Exception(f"PDF WAS NOT GENERATED: {out_path_full}")

  print(f"PDF Generated - ./{out_path_full}") # . Time: {sw.elapsed(1)}s


def _waitForDocReady(driver):
  rs = driver.execute_script('return document.readyState;')
  if rs == 'complete': return True
  return False
    

def send_cmd(driver, cmd, params={}):
  response = driver.command_executor._request(
     'POST'
    ,f"{driver.command_executor._url}/session/{driver.session_id}/chromium/send_command_and_get_result"
    ,json.dumps({'cmd': cmd, 'params': params}))
  if response.get('status'): raise Exception(response.get('value'))
  return response.get('value')


class StopWatch:
    def __init__(self):
        self.start()
    def start(self):
        self._startTime = time.time()
    def getStartTime(self):
        return self._startTime
    def elapsed(self, prec=3):
        prec = 3 if prec is None or not isinstance(prec, int) else prec
        diff= time.time() - self._startTime
        return round(diff, prec)


if __name__ == '__main__':
    main(sys.argv[1:])
