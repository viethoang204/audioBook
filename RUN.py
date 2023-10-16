from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import subprocess
import re

def get_links():
    webdriver_path = 'geckodriver'
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    service = Service(webdriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.get('https://www.msn.com/vi-vn/money?ocid=hpmsn&cvid=9e9bb350495e41dab2bd5c0d024f9bcc&ei=9')
    time.sleep(10)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', class_='contentCard-DS-EntryPoint1-1')
    urls = []
    urls1 = []
    for link in links:
        href = link.get('href')
        urls.append(href)

    for i in urls:
        match = re.search(r'AA.*\?', i)
        if match:
            result = match.group()
            urls1.append('https://assets.msn.com/content/view/v2/Detail/vi-vn/' + result)
        else:
            print("Không tìm thấy chuỗi phù hợp.")
    driver.quit()
    return urls1


urls = get_links()
if urls:
    print(urls)
    print(len(urls))
    for i, j in enumerate(urls):
        print(i, j)
        command1 = f'python get_content.py "{j}"'
        output = subprocess.check_output(command1, shell=True).decode('utf-8').strip()

        if output == "độ dài bài  viết không phù hợp, bỏ qua!":
            continue
        else:

            subprocess.call(['sh', 'RUN.sh'])

            command2 = f'python News.py output/Video_{i}.mp4'
            subprocess.call(command2, shell=True)
else:
    print("No URLs found.")


