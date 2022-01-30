import os
import requests
import time
import json
import argparse
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import progressbar
import urllib.request
import getpass

progress_bar = None
json_file_path = "network_log.json"

def show_progress(block_num, block_size, total_size):
    global progress_bar
    if progress_bar is None:
        progress_bar = progressbar.ProgressBar(maxval=total_size)
        progress_bar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        progress_bar.update(downloaded)
    else:
        progress_bar.finish()
        progress_bar = None

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)



if __name__ == "__main__":
    print(
"""\n
Please do not close the main browser window if you want to be able to keep downloading videos.
\n""")


    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    options.add_argument("--ignore-certificate-errors")

    # parser = argparse.ArgumentParser(description='Downloads selected videos from panopto.')
    # parser.add_argument('-headless', action="store_false", help='If specified opens up with browser')
    # args = parser.parse_args()

    driver = webdriver.Chrome(resource_path('./driver/chromedriver.exe'), options=options, desired_capabilities=desired_capabilities)

    driver.get("http://login.panopto.com/")

    while True:
        check = input("Please type 'yes' if you have logged in to panopto: ")
        if check.lower() == 'yes':
            break

    while True:
        mainUrl = input("Please input the video URL: ")
        if mainUrl.replace(" ", "") == "":
            print('\n')
            continue
        driver.get(mainUrl)

        print("\n Initializing... \n\n")
        time.sleep(3)
        if not len(driver.find_elements(By.ID, "PageContentPlaceholder_loginControl_externalLoginButton")) == 0:
            print("logging in to panopto \n")
            driver.find_element(By.ID, "PageContentPlaceholder_loginControl_externalLoginButton").click()

        time.sleep(.5)
        driver.get(mainUrl)
        time.sleep(3)

        logs = driver.get_log("performance")

        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write("[")

            for log in logs:
                network_log = json.loads(log["message"])["message"]

                if("Network.response" in network_log["method"]
                        or "Network.request" in network_log["method"]
                        or "Network.webSocket" in network_log["method"]):

                    f.write(json.dumps(network_log)+",")
            f.write("{}]")

        with open(json_file_path, "r", encoding="utf-8") as f:
            logs = json.loads(f.read())

        url_found = False
        mp4 = False
        mp4s = []
        for log in logs:
            try:
                url = log["params"]["request"]["url"]

                if url[len(url)-3:] == ".ts":
                    url_found = True
                    print(f'Media file found in URL: \n {url}', end='\n\n')
                    break
                elif log["params"]["type"] == "Media" and ".mp4" in url:
                    url_found = True
                    mp4 = True
                    mp4s.append(url)

            except Exception as e:
                pass

        if url_found:
            if not mp4:
                fileName = input('Output name (Do not put any extension): ')
                while os.path.exists(f'{fileName}.ts'):
                    print("\n File already exists please enter a new name")
                    fileName = input('Output name: ')

                i = 0
                while True:
                    number = '00' + '0' * (3-len(str(i))) + str(i)
                    url = url[ : -8]
                    url = f'{url}{number}.ts'

                    r=requests.get(url)
                    if r.content.startswith(b'<?xml version="1.0" encoding="UTF-8"?>\n<Error>') or r.content == b'':
                        print("\n\n")
                        break
                    print(f'Video index: "{number}"')
                    print(url, end= "\n")

                    open(f'{fileName}.ts', 'ab').write(r.content)
                    i+=1
            else:
                print(
f"""\n\n This is a single mp4 file download, it may not perfectly work.
If it didn't download the right video please send me a message together with the url of video you are trying to download and with this url:
{url} \n\n""")
                fileName = input('Output name (Do not put any extension): ')
                while os.path.exists(f'{fileName}.mp4'):
                    print("\n File already exists please enter a new name")
                    fileName = input('Output name: ')

                    print("Please wait...")
                    r=requests.get(url)

                    urllib.request.urlretrieve(url, f"{fileName}.mp4", show_progress)
                    print(
f"""If it didn't download the right video you can also manually find and download the video you want, from here:
{mp4s} \n""")

        else:
            print("media file couldn't be found.", end="\n\n")

        if os.path.exists("network_log.json"):
            os.remove("network_log.json")
        else:
            print("json file doesn't exist")

    driver.quit()