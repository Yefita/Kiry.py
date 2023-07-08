from bs4 import BeautifulSoup
import requests
import sys
import re
import os
import zipfile
import shutil
import configparser
import urllib.parse

def status_get():
    while True:
        answer = input("Comics status(Default is All.).\n1. All.\n2. Ongoing.\n3. Completed.\n4. Hiatus.\n\nSelect comics status or (C)lose the script(c, 1-4): ")
        if answer == "1" or answer.lower() == "":
            m_status = ""
            return m_status
        elif answer == "2":
            m_status = "&status=ongoing"
            return m_status
        elif answer == "3":
            m_status = "&status=completed"
            return m_status
        elif answer == "4":
            m_status = "&status=hiatus"
            return m_status
        elif answer.lower() == "c" or answer.lower() == "close" or answer.lower() == "cancel":
            clear_terminal()
            sys.exit(0)
        else:
            print("Infalid Input.")

def type_get():
    while True:
        answer = input("Comics type(Novels is not supported, Default is All).\n1. All.\n2. Manga(Japanese).\n3. Manhua(Chinese).\n4. Manhwa(Korean).\n5. Others.\n\nSelect comics type or (C)lose the script(c, 1-5): ")
        if answer == "1" or answer.lower() == "":
            m_type = ""
            return m_type
        elif answer == "2":
            m_type = "&type=manga"
            return m_type
        elif answer == "3":
            m_type = "&type=manhua"
            return m_type
        elif answer == "4":
            m_type = "&type=manhwa"
            return m_type
        elif answer == "5":
            m_type = "&type=comic"
            return m_type
        elif answer.lower() == "c" or answer.lower() == "close" or answer.lower() == "cancel":
            clear_terminal()
            sys.exit(0)
        else:
            print("Invalid Input.\n")

def sort_get():
    while True:
        answer = input("Listing order(Default is New Update).\n1. Website Default.\n2. Alphabetical A-Z.\n3. Reverse-Alphabetical Z-A.\n4. New Update.\n5. Date Added.\n6. Popular.\n\nSelect listing order or (C)lose the script(c, 1-6): ")
        if answer == "1":
            m_order = ""
            return m_order
        elif answer == "2":
            m_order = "&order=title"
            return m_order
        elif answer == "3":
            m_order = "&order=titlereverse"
            return m_order
        elif answer == "4" or answer == "":
            m_order = "&order=update"
            return m_order
        elif answer == "5":
            m_order = "&order=latest"
            return m_order
        elif answer == "6":
            m_order = "&order=popular"
            return m_order
        elif answer.lower() == "c" or answer.lower() == "close" or answer.lower() == "cancel":
            clear_terminal()
            sys.exit(0)
        else:
            print("Infalid input.\n")

def html_get(url):
    result = requests.get(url, headers=headers)
    html = BeautifulSoup(result.text, "html.parser")
    return html

def display_comic_list(html, page_num):
    print("Page " + str(page_num))
    comic_list = html.find(class_="listupd").contents
    for num, comic_entry in enumerate(comic_list):
        comic_entry = comic_list[num].next_sibling
        entry = comic_entry.find("a")
        title = entry["title"]
        lastest_chapter = entry.find(class_="epxs").string
        print(str(int(num) + 1) + ". " + title + " (" + lastest_chapter + ")")
        if int(num) + 1 >= 50:
            return comic_list

def title_selector(page_num, comic_list):
    while True:
        answer = input("\n\t[ (P)revious page ]   [ Page " + str(page_num) + " ]   [ (N)ext page ]\n\nSelect Entry or (C)lose the script(p, n, c, 1-50): ")
        if isinstance(answer, str) and answer.isdigit() and int(answer) >= 1 and int(answer) <= 50:
            title,comic_url,cover_url = get_entry_info(comic_list, answer)
            return title,comic_url,cover_url
        elif answer.lower() == "n":
            page_num = int(page_num) + 1
            clear_terminal()
            url = base_url + str(page_num) + m_status  + m_type + m_order
            html = html_get(url)
            comic_list = display_comic_list(html, page_num)
        elif answer.lower() == "p":
            page_num = int(page_num) - 1
            clear_terminal()
            url = base_url + str(page_num) + m_status  + m_type + m_order
            html = html_get(url)
            comic_list = display_comic_list(html, page_num)
        elif answer.lower() == "c" or answer.lower() == "close" or answer.lower() == "cancel":
            clear_terminal()
            sys.exit(0)
        else:
            print("Infalid input.")

def get_entry_info(comic_list, entry):
    entry = comic_list[int(entry ) - 1].next_sibling.find("a")
    title = entry["title"]
    comic_url = entry["href"]
    cover_url = entry.find("img")["src"]
    return title,comic_url,cover_url

def chapter_selector():
    while True:
        print("[ ", title, " ]")
        answer = input("Show (L)ist, (C)lose the script or select chapter to Download(l, c, " + first_chapter + "-" + lastest_chapter + "): ")
        if answer.isdecimal():
            if float(answer) >= float(first_chapter) and float(answer) <= float(lastest_chapter):
                if answer.isdigit():
                    answer = f"{int(answer):02d}"
                chapter_url = chapter_list.find("li", {"data-num": answer}).find('a', href=True)['href']
                chapter_num = str(answer)
                return chapter_url,chapter_num
            else:
                print("Invalid input. Number is out of range")
        else:
            if answer.lower() == "l" or answer.lower() == "list":
                clear_terminal()
                for num, chapter in enumerate(chapters):
                    chapter_num = chapter.find(class_="chapternum").string
                    if num % 5:
                        print(chapter_num, end="\t")
                    else:
                        print(chapter_num, end="\n")
                print()
            elif answer.lower() == "c" or answer.lower() == "close":
                clear_terminal()
                sys.exit(0)
            else:
                print("Infalid input.")

def get_chapter_info():
    chapter_list = html.find(class_="eplister")
    chapters = chapter_list.find_all("li", {"data-num": True})
    lastest_chapter = chapter_list.find("li")["data-num"]
    first_chapter = chapter_list.find(class_="first-chapter")["data-num"]
    return chapter_list,chapters,lastest_chapter,first_chapter

def get_image_urls(html):
    print("Getting image url..")
    script_tag = html.find('script', string=lambda x: 'ts_reader.run' in str(x))
    script_content = script_tag.string
    match = re.search(r'"source":"Server 1","images":\["(.*?)"\]', script_content)
    if match:
        ts_reader_content = match.group(1)
    else:
        match = re.search(r'ts_reader\.run\((.*?)\);', script_content)
        if match:
            ts_reader_content = match.group(1)
        else:
            print("\rCan't find the image url.")
    ts_reader_content = urllib.parse.unquote(ts_reader_content.replace("\\", ""))
    image_urls = ts_reader_content.split('","')
    print("\r", end="")
    return image_urls

def create_dir(directory):
    if not os.path.exists(directory):
        print("Creating " + directory)
        os.makedirs(directory, exist_ok=True)


def get_cover():
    print("Downloading Cover..")
    response = requests.get(cover_url, stream=True, headers=image_headers)
    response.raise_for_status()

    filename = os.path.basename(cover_url)
    new_filename = "cover" + os.path.splitext(filename)[1]
    with open(os.path.join(tmp_dir, title, new_filename), "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def chapter_image_downloader(image_headers):
    last_dl = False
    files = os.listdir(tmp_dir + "/" + title + "/" + chapter_num)
    if files:
        last_dl = True
        files.sort(reverse=True)
        last_file = "{:01d}".format(int(files[0].split(".")[0]))
    dl_num = 0
    for n, url in enumerate(image_urls):
        if last_dl == True and n < int(last_file) - 1:
            continue
        number = int(n + 1)
        fmt_number = "{:03d}".format(number)
        filename = os.path.basename(url)
        new_filename = str(fmt_number) + os.path.splitext(filename)[1]
        if dl_num <= 0:
            print("Downloading image " + new_filename)
            dl_num = dl_num + 1
        else:
            print("\rDownloading image " + new_filename)
        response = requests.get(url, stream=True, headers=image_headers)
        response.raise_for_status()

        with open(os.path.join(tmp_dir, title, chapter_num, new_filename), "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    print("\rAll image Downloaded.")

def make_cbz(chapter_directory, cbz_path):
    print("Generating .cbz archive..")
    with zipfile.ZipFile(cbz_path, 'w', compression=zipfile.ZIP_DEFLATED) as cbz:
        for root, _, files in os.walk(chapter_directory):
            for file in files:
                file_path = os.path.join(root, file)
                cbz.write(file_path, arcname=os.path.relpath(file_path, chapter_directory))

def remove_dir():
    print("Removing chapter image directory..")
    if os.path.exists(chapter_directory):
        shutil.rmtree(chapter_directory, ignore_errors=True)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    #print("Terminal clear here")

config = configparser.ConfigParser()
config.read('config.ini')
clear_terminal()
m_status = status_get()
clear_terminal()
m_type = type_get()
clear_terminal()
m_order = sort_get()

base_url = config.get("Settings", "base_url")
user_agent = config.get("Settings", "user_agent")
tmp_dir = config.get("Settings", "tmp_dir")
page_num = "1"
headers = { 
           'User-Agent': user_agent,
           'Accept-Language': 'en-US,en;q=0.9',
           'Referer': "https://google.co.id/"
}

url = base_url + str(page_num) + m_status  + m_type + m_order

html = html_get(url)
clear_terminal()

comic_list = display_comic_list(html, page_num)
title,comic_url,cover_url = title_selector(page_num, comic_list)

html = html_get(comic_url)
chapter_list,chapters,lastest_chapter,first_chapter = get_chapter_info()
clear_terminal()

while True:
    chapter_url,chapter_num = chapter_selector()
    html = html_get(chapter_url)

    clear_terminal()
    print("\t[ " +title + " Chapter " + chapter_num + " ]")
    print(chapter_url)
    image_headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': "https://kiryuu.id"
    }
    image_urls = get_image_urls(html)

    chapter_directory = tmp_dir + "/" + title + "/" + chapter_num
    create_dir(chapter_directory)
    get_cover()

    chapter_image_downloader(image_headers)

    cbz_path = tmp_dir + "/" + title + "/" + "Chapter " + chapter_num + ".cbz"
    make_cbz(chapter_directory, cbz_path)

    remove_dir()
    clear_terminal()
