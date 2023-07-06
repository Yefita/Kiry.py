from bs4 import BeautifulSoup
import requests
import sys
import re
import json
import os
import zipfile
import shutil

base_url = "https://kiryuu.id/manga/?page="
headers={"User-Agent": "Mozilla/5.0 (Linux; Android 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36"}
tmp_dir = "/storage/79DE-B4B5/Scraper/Kiryuu"

def status_get():
    while True:
        answer = input("Comics status(Default is All.).\n1. All.\n2. Ongoing.\n3. Completed.\n4. Hiatus.\n\nSelect comics status or (C)lose the script(c,1-4): ")
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
        answer = input("Comics type(Novels is not supported, Default is All).\n1. All.\n2. Manga(Japanese).\n3. Manhua(Chinese).\n4. Manhwa(Korean).\n5. Others.\n\nSelect comics type or (C)lose the script(c,1-5): ")
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
        answer = input("Listing order(Default is New Update).\n1. Website Default.\n2. Alphabetical A-Z.\n3. Reverse-Alphabetical Z-A.\n4. New Update.\n5. Date Added.\n6. Popular.\n\nSelect listing order or (C)lose the script(c,1-6): ")
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

def display_comic_list():
    print("Page: " + str(page_num))
    comic_list = html.find(class_="listupd").contents
    for num, comic_entry in enumerate(comic_list):
        comic_entry = comic_list[num].next_sibling
        entry = comic_entry.find("a")
        title = entry["title"]
        lastest_chapter = entry.find(class_="epxs").string
        print(str(int(num) + 1) + ". " + title + " (" + lastest_chapter + ")")
        if int(num) + 1 >= 50:
            return comic_list

def get_entry_info(entry):
    entry = comic_list[int(entry ) - 1].next_sibling.find("a")
    title = entry["title"]
    comic_url = entry["href"]
    cover_url = entry.find("img")["src"]
    return title,comic_url,cover_url

def get_chapter_info():
    chapter_list = html.find(class_="eplister")
    chapters = chapter_list.find_all("li", {"data-num": True})
    lastest_chapter = chapter_list.find("li")["data-num"]
    first_chapter = chapter_list.find(class_="first-chapter")["data-num"]
    return chapter_list,chapters,lastest_chapter,first_chapter

def get_image_urls():
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
            print("Can't find the links.")

    parsed_content = json.loads(ts_reader_content)
    sources = parsed_content.get('sources', [])
    image_urls = [image_url for source in sources for image_url in source.get('images', [])]
    return image_urls

def create_dir():
    if not os.path.exists(chapter_directory):
        os.makedirs(chapter_directory, exist_ok=True)

def chapter_image_downloader():
    for n, url in enumerate(image_urls):
        number = int(n + 1)
        fmt_number = "{:03d}".format(number)
        print("Downloading: " + url)
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()

        filename = os.path.basename(url)
        new_filename = str(fmt_number) + os.path.splitext(filename)[1]
        with open(os.path.join(tmp_dir, title, answer, new_filename), "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

def make_cbz(chapter_directory, cbz_path):
    with zipfile.ZipFile(cbz_path, 'w', compression=zipfile.ZIP_DEFLATED) as cbz:
        for root, _, files in os.walk(chapter_directory):
            for file in files:
                file_path = os.path.join(root, file)
                cbz.write(file_path, arcname=os.path.relpath(file_path, chapter_directory))

def remove_dir():
    if os.path.exists(chapter_directory):
        shutil.rmtree(chapter_directory, ignore_errors=True)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_terminal()
m_status = status_get()
clear_terminal()
m_type = type_get()
clear_terminal()
m_order = sort_get()
page_num = "1"
url = base_url + str(page_num) + m_status  + m_type + m_order
html = html_get(url)
clear_terminal()
comic_list = display_comic_list()
while True:
    answer = input("\t(P)revious page  [ Page " + str(page_num) + " ]  (N)ext page\n\nSelect Entry or (C)lose the script(p,n,c,1-50): ")
    if isinstance(answer, str) and answer.isdigit() and int(answer) >= 1 and int(answer) <= 50:
        title,comic_url,cover_url = get_entry_info(answer)
        break
    elif answer.lower() == "n":
        page_num = int(page_num) + 1
        clear_terminal()
        url = base_url + str(page_num) + m_status  + m_type + m_order
        html = html_get(url)
        display_comic_list()
    elif answer.lower() == "p":
        page_num = int(page_num) - 1
        clear_terminal()
        url = base_url + str(page_num) + m_status  + m_type + m_order
        html = html_get(url)
        display_comic_list()
    elif answer.lower() == "c" or answer.lower() == "close" or answer.lower() == "cancel":
        clear_terminal()
        sys.exit(0)
    else:
        print("Infalid input.")

html = html_get(comic_url)
chapter_list,chapters,lastest_chapter,first_chapter = get_chapter_info()
clear_terminal()

while True:
    print(title)
    answer = input("Select chapter to Download, (L)ist it or (C)lose the script(l,c," + first_chapter + "-" + lastest_chapter + ")")
    if isinstance(answer, str) and answer.isdigit() and int(answer) >= int(first_chapter) and int(answer) <= int(lastest_chapter):
        answer = "{:02d}".format(int(answer))
        chapter_url = chapter_list.find("li", {"data-num": answer}).find('a', href=True)['href']
        print(chapter_url)
        html = html_get(chapter_url)
        image_urls = get_image_urls()
        chapter_directory = tmp_dir + "/" + title + "/" + answer
        create_dir()
        chapter_image_downloader()
        cbz_path = chapter_directory + ".cbz"
        make_cbz(chapter_directory, cbz_path)
        remove_dir()
        clear_terminal()
        print("Chapter " + answer + " Downloaded.")

    elif answer.lower() == "l" or answer.lower() == "list":
        clear_terminal()
        for num, chapter in enumerate(chapters):
            chapter_num = chapter.find(class_="chapternum").string
            if num % 5:
                print(chapter_num, end="\n")
            else:
                print(chapter_num, end="\t")
        print("\n\n")
    elif answer.lower() == "c" or answer.lower() == "close":
        clear_terminal()
        sys.exit(0)
    else:
        print("Invalid input.")
