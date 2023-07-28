from bs4 import BeautifulSoup
import configparser
import argparse
import sys
import requests
import re
import urllib
import os
import shutil
import zipfile
from tqdm import tqdm



class Argument:
    def __init__(self):

        self.version = "Kiry.py v0.0.3-28.07.23_testing"
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-v", "--version", action="version", version=self.version, help="Print version number then exit.")
        self.parser.add_argument("-s", "--search", help="Search comic title")
        self.parser.add_argument("-p", "--page", help="Display page number of choice, instead of starting from 1st page")
        self.parser.add_argument("-d", "--directory", help="Set directory to safe the downloaded file.(Default is current directory.)")
        self.parser.add_argument("-D", "--directory-presist", help="Set directory to safe the downloaded file permanently.")
        self.parser.add_argument("-C", "--cookie", help="Use cookie incase of Cloudflare low level blocking. it won't work on high level. to remove cookie use \"--cookie off\".")
        self.parser.add_argument("-U", "--user-agent", help="Change UA. Make sure it match with your browser(that you take the cookie from) if you use cookie. to set UA to default value use \"--user-agent default\"")
        self.args = self.parser.parse_args()
        config.read("config.ini")

    def directory(self):
        if self.args.directory:
            self.directory = str(self.args.directory)
        elif self.args.directory_presist:
            config["Settings"]["tmp_dir"] = self.args.directory_presist
            with open("config.ini", "w") as new_config:
                config.write(new_config)
            self.directory = str(self.args.directory_presist)
        else:
            self.directory = config.get("Settings", "tmp_dir")
        return self.directory

    def page(self, page_num):
        if self.args.page:
            page_num = int(self.args.page)
        return page_num

    def search(self, base_url, page_num):
        if self.args.search:
            self.issearch = True
            self.query = self.args.search.replace(" ", "+").lower()
            if page_num == 1:
                self.url = base_url + "?s=" + self.query
            else:
                self.url = base_url + "page/" + str(page_num) + "/?s=" + self.query
        else:
            self.url = ""
            self.issearch = False
        return self.url,self.issearch

    def cookie(self):
        if str(self.args.cookie).lower() == "off":
            config["Settings"]["is_cookie"] = "False"
            if config.has_section("CookieValue") or config.has_section("CookieName"):
                config.remove_section("CookieName")
                config.remove_section("CookieValue")
                #config.remove_section("CookieName")
        elif self.args.cookie:
            if not config.has_section("CookieName"):
                config.add_section("CookieName")
            if not config.has_section("CookieValue"):
                config.add_section("CookieValue")
            self.cookies = self.args.cookie.split(sep=", ")
            for n, cookie in enumerate(self.cookies):
                self.cookie = cookie.split(sep="=")
                self.cookie_name = "cookie" + str(n)
                config["CookieName"][self.cookie_name] = self.cookie[0]
                config["CookieValue"][self.cookie_name] = self.cookie[1]
                config["Settings"]["is_cookie"] = "True"
        with open("config.ini", "w") as new_config:
            config.write(new_config)

    def user_agent(self):
        if str(self.args.user_agent).lower() == "default":
            config["Settings"]["user_agent"] = config.get("Default", "user_agent")
        elif self.args.user_agent:
            config["Settings"]["user_agent"] = self.args.user_agent
        with open("config.ini", "w") as new_config:
            config.write(new_config)


class MainPrompt:
    def __init__(self):
        self.comic_status = ""
        self.comic_type = ""
        self.comic_order = ""
        self.invalid = False

    def get_status(self):
        self.answer = input("Comic stauts(Default is All).\n1. All\n2. Ongoing.\n3. Completed.\n4. Hiatus.\n\nSelect comics status or (C)lose the script(C/1-4): ")
        if self.answer.lower() == "c" or self.answer.lower() == "close" or self.answer.lower() == "q":
            sys.exit(0)
        elif self.answer == "1" or self.answer.lower() == "all" or self.answer == "":
            self.comic_status = ""
        elif self.answer == "2" or self.answer.lower() == "ongoing":
            self.comic_status = "ongoing"
        elif self.answer == "3" or self.answer.lower() == "completed":
            self.comic_status = "completed"
        elif self.answer == "4" or self.answer.lower() == "hiatus":
            self.comic_status = "hiatus"
        else:
            self.invalid = True
            Misc.clear_terminal()
            print("Invalid input.\n")
        return self.comic_status,self.invalid
    
    def get_type(self):
        self.answer = input("Comics type(Novels is not supported, Default is All).\n1. All.\n2. Manga(Japanese).\n3. Manhua(Chinese).\n4. Manhwa(Korean).\n5. Others.\n\nSelect comics type or (C)lose the script(c, 1-5): ")
        if self.answer == "1" or self.answer == "" or self.answer.lower() == "all":
            self.comic_type = ""
        elif self.answer == "2" or self.answer.lower() == "manga":
            self.comic_type = "manga"
        elif self.answer == "3" or self.answer.lower() == "manhua": 
            self.comic_type = "manhua"
        elif self.answer == "4" or self.answer.lower() == "manhwa":
            self.comic_type = "manhwa"
        elif self.answer == "5" or self.answer.lower() == "comic":
            self.comic_type = "comic"
        elif self.answer.lower() == "c" or self.answer.lower() == "close" or self.answer.lower() == "cancel" or self.answer.lower() == "q":
            sys.exit(0)
        else:
            self.invalid = True
            Misc.clear_terminal()
            print("Invalid Input.\n")
        return self.comic_type,self.invalid


    def get_order(self):
        self.answer = input("Listing order(Default is New Update).\n1. Alphabetical A-Z.\n2. Reverse-Alphabetical Z-A.\n3. New Update.\n4. Date Added.\n5. Popular.\n\nSelect listing order or (C)lose the script(c, 1-5): ")
        if self.answer == "1" :
            self.comic_order = "title"
        elif self.answer == "2":
            self.comic_order = "titlereverse"
        elif self.answer == "3" or self.answer == "":
            self.comic_order = "update"
        elif self.answer == "4":
            self.comic_order = "latest"
        elif self.answer == "5":
            self.comic_order = "popular"
        elif self.answer.lower() == "c" or self.answer.lower() == "close" or self.answer.lower() == "cancel" or self.answer.lower() == "q":
            sys.exit(0)
        else:
            self.invalid = True
            Misc.clear_terminal()
            print("Infalid input.\n")
        return self.comic_order,self.invalid

    def entry_prompt(self, comic_list, page_num, max_entry, issearch):
        self.istitle = False
        while True:
            self.answer = input("Select comic title(P/N/C/1-" + str(max_entry) + "): ")
            if isinstance(self.answer, str) and self.answer.isdigit() and int(self.answer) >= 1 and int(self.answer) <= max_entry:
                self.istitle = True
                return self.istitle,self.answer,page_num
            elif self.answer.lower() == "n" or self.answer.lower() == "next":
                if issearch == True and not max_entry == 10:
                    print("Already maximum page")
                elif issearch == False and not max_entry == 50:
                    print("Already maximum page")
                else:
                    self.page_num = int(page_num) + 1
                    return self.istitle,self.answer,self.page_num
            elif self.answer.lower() == "p" or self.answer.lower() == "previous":
                if int(page_num) <= 1:
                    print("Already in page 1")
                else:
                    self.page_num = int(page_num) - 1
                    return self.istitle,self.answer,self.page_num
            elif self.answer.lower() == "c" or self.answer.lower() == "close" or self.answer.lower() == "cancel" or self.answer.lower() == "q":
                sys.exit(0)
            else:
                print("Invalid input")

                        
    def chapter_selector(self, tmp_dir, title, first_chapter, lastest_chapter, chapters, chapter_list, cover_url):
        Misc.clear_terminal()
        while True:
            print("[ " + title + " ]")
            self.answer = input("Show (L)ist, select chapter to download or (C)lose the script(L/" + first_chapter + "-" + lastest_chapter + "/C): ")
            if "-" in self.answer:
                Misc.clear_terminal()
                Scrap().multi_chapter_select(tmp_dir, title, chapters, chapter_list, self.answer, cover_url)
            elif "." in self.answer and not "-" in self.answer or self.answer.isdigit():
                Misc.clear_terminal()
                Scrap().chapter_select(tmp_dir, title, chapters, chapter_list, self.answer, cover_url)
            elif self.answer.lower() == "l" or self.answer.lower() == "list":
                Misc.clear_terminal()
                MainPrompt().show_chapter_list(chapters)
            elif self.answer.lower() == "c" or self.answer.lower() == "close" or self.answer.lower() == "cancel" or self.answer.lower() == "q":
                Misc.clear_terminal()
                sys.exit(0)
            else:
                print("Invalid input")

    def show_chapter_list(self, chapters):
        for self.num, self.chapter in enumerate(chapters):
            self.chapter_num = self.chapter.find(class_="chapternum").string
            if self.num % 5:
                print(self.chapter_num, end="\t")
            else:
                print(self.chapter_num, end="\n")
        print("")
        return


class Network:
    def __init__(self):
        Argument().user_agent()
        self.user_agent = config.get("Settings", "user_agent")
        self.tmp_dir = Argument().directory() 
        self.headers = {
                "User-Agent": self.user_agent,
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://kiryuu.id/"
                }

    def get_html(self, url):
        Argument().cookie()
        if config.get("Settings", "is_cookie") == "True":
            self.cookie_num = config.options("CookieName")
            self.cookies = requests.cookies.RequestsCookieJar()
            for n, cookie in enumerate(self.cookie_num):
                self.cookies.set(config.get("CookieName", "cookie" + str(n)), config.get("CookieValue", "cookie" + str(n)))
            self.result = requests.get(url, headers=self.headers, cookies=self.cookies)
            self.html = BeautifulSoup(self.result.text, "html.parser")
        else:
            self.result = requests.get(url, headers=self.headers)
            self.html = BeautifulSoup(self.result.text, "html.parser")
        return self.html

    def cover_downloader(self, url, title):
        self.cover_name = "cover" + os.path.splitext(os.path.basename(url))[1]
        self.cover = os.path.join(self.tmp_dir, title, self.cover_name)
        if not os.path.exists(self.cover):
            self.response = requests.get(url, stream=True, headers=self.headers)
            self.total_size= int(self.response.headers.get('content-length', 0))
            self.progress_bar = tqdm(total=self.total_size, unit='iB', unit_scale=True, desc="Downloading " + self.cover_name)
            with open(self.cover, "wb") as file:
                for data in self.response.iter_content(chunk_size=1024):
                    self.progress_bar.update(len(data))
                    file.write(data)
            self.progress_bar.close()

    def image_downloader(self, title, chapter_num, urls):
        self.files = os.listdir(os.path.join(tmp_dir, title, chapter_num))
        self.last_dl = False
        if self.files:
            self.last_dl = True
            self.files.sort(reverse=True)
            self.last_file = "{:01d}".format(int(self.files[0].split(".")[0]))
            print("Continuing unfinished download..")
        for n, url in enumerate(urls):
            if self.last_dl == True and n < int(self.last_file) - 1:
                continue
            self.number = int(n + 1)
            self.fmt_number = "{:03d}".format(self.number)
            self.filename = os.path.basename(url)
            self.new_filename = str(self.fmt_number) + os.path.splitext(self.filename)[1]
            self.response = requests.get(url, stream=True, headers=self.headers)

            self.total_size= int(self.response.headers.get('content-length', 0))
            self.progress_bar = tqdm(total=self.total_size, unit='iB', unit_scale=True, desc="Downloading " + self.new_filename + "(" + str(n + 1) + "/" + str(len(urls)) + ")")

            with open(os.path.join(tmp_dir, title, chapter_num, self.new_filename), "wb") as file:
                for data in self.response.iter_content(chunk_size=1024):
                    self.progress_bar.update(len(data))
                    file.write(data)
            self.progress_bar.close()
        Misc.clear_terminal()


class Scrap:
    def display_comic_list(self, html, page_num):
        Misc.clear_terminal()
        print("Page " + str(page_num))
        self.comic_list = html.find(class_="listupd").contents
        for n, entry in enumerate(self.comic_list):
            try:
                self.comic_entry = self.comic_list[n].next_sibling.find("a")
                self.title = self.comic_entry["title"]
                self.lastest_chapter = self.comic_entry.find(class_="epxs").string
                print(str(int(n) + 1) + ". " + self.title + " (" + self.lastest_chapter + ")")
            except TypeError:
                print("\n\t[ (P)revious ] [ Page " + str(page_num) + " ] [ (N)ext ]\n")
                return self.comic_list,n

            except AttributeError:
                print("\n\t[ (P)revious ] [ Page " + str(page_num) + " ] [ (N)ext ]\n")
                return self.comic_list,n

    def comic_url(self, comic_status, comic_type, comic_order, page_num):
        if page_num <= 1:
            if comic_status == "" and comic_type == "":
                comic_order = comic_order.replace("&", "")
            elif comic_status == "" and not comic_type == "":
                comic_type = comic_type.replace("&", "")
            self.url = base_url + "manga/?" + comic_status  + comic_type + comic_order
        else:
            if comic_status == "" and comic_type == "":
                comic_order = comic_order.replace("&", "")
            elif comic_status == "" and not comic_type == "":
                comic_type = comic_type.replace("&", "")
            self.url = base_url + "manga/?" + "page=" + str(page_num) + "&" + comic_status + comic_type + comic_order
        return self.url

    def get_comic_info(self, comic_list, entry_num):
        self.entry = comic_list[int(entry_num) - 1].next_sibling.find("a")
        self.title = self.entry["title"]
        self.comic_url = self.entry["href"]
        self.cover_url = self.entry.find("img")["src"]
        return self.entry,self.title,self.comic_url,self.cover_url

    def get_chapter_info(self, html):
        self.chapter_list = html.find(class_="eplister")
        self.chapters = self.chapter_list.find_all("li", {"data-num": True})
        self.lastest_chapter = self.chapter_list.find("li")["data-num"]
        self.first_chapter = self.chapter_list.find(class_="first-chapter")["data-num"]
        return self.chapter_list,self.chapters,self.lastest_chapter,self.first_chapter
    
    def multi_chapter_select(self, tmp_dir, title, chapters, chapter_list, chapter_ranges, cover_url):
        self.ranges = chapter_ranges.split(sep="-")
        for self.num, self.chapter in enumerate(reversed(chapters)):
            self.data_num = self.chapter["data-num"]
            self.data_num_striped = re.sub(r'[^0-9.]', '', self.data_num)
            try:
                float(self.ranges[0])
                float(self.ranges[1])
                float(self.data_num_striped)
            except ValueError:
                continue
            if float(self.data_num_striped) >= float(self.ranges[0]) and float(self.data_num_striped) <= float(self.ranges[1]):
                print("Chapter " + self.data_num)
                self.chapter_entry = chapter_list.find("li", {"data-num": self.data_num})
                self.chapter_url = self.chapter_entry.find('a', href=True)['href']
                self.chapter_html = Network().get_html(self.chapter_url)
                self.image_urls = Scrap().get_image_urls(self.chapter_html)

                self.directory = os.path.join(tmp_dir, title, self.data_num)
                Misc.make_dir(self.directory)
                Network().cover_downloader(cover_url, title)
                Network().image_downloader(title, self.data_num, self.image_urls)
                Misc().make_cbz(self.directory, self.data_num)
                Misc.remove_after_cbz(self.directory)
                if self.num >= len(chapters):
                    return

    def chapter_select(self, tmp_dir, title, chapters, chapter_list, chapter_num, cover_url):
        for self.num, self.chapter in enumerate(reversed(chapters)):
            self.data_num = self.chapter["data-num"]
            self.data_num_striped = re.sub(r'[^0-9.]', '', self.data_num)
            try:
                float(chapter_num)
                float(self.data_num_striped)
            except ValueError:
                continue
            if float(self.data_num_striped) == float(chapter_num):
                print("Chapter " + self.data_num)
                self.chapter_entry = chapter_list.find("li", {"data-num": self.data_num})
                self.chapter_url = self.chapter_entry.find('a', href=True)['href']
                self.chapter_html = Network().get_html(self.chapter_url)
                self.image_urls = Scrap().get_image_urls(self.chapter_html)

                self.directory = os.path.join(tmp_dir, title, self.data_num)
                Misc.make_dir(self.directory)
                Network().cover_downloader(cover_url, title)
                Network().image_downloader(title, self.data_num, self.image_urls)
                Misc().make_cbz(self.directory, self.data_num)
                Misc.remove_after_cbz(self.directory)
                if self.num >= len(chapters):
                    return

    def get_image_urls(self, chapter_html):
        self.script_tag = chapter_html.find('script', string=lambda x: 'ts_reader.run' in str(x))
        self.script_content = self.script_tag.string
        self.match = re.search(r'"source":"Server 1","images":\["(.*?)"\]', self.script_content)
        if self.match:
            self.ts_reader_content = self.match.group(1)
        else:
            self.match = re.search(r'ts_reader\.run\((.*?)\);', self.script_content)
            if self.match:
                self.ts_reader_content = self.match.group(1)
            else:
                print("Can't find image urls")
                sys.exit(1)
        self.ts_reader_content = urllib.parse.unquote(self.ts_reader_content.replace("\\", ""))
        self.image_urls = self.ts_reader_content.split('","')
        return self.image_urls

class Misc:
    def make_cbz(self, chapter_directory, data_num):
        cbz_file_name = "Chapter " + data_num + ".cbz"
        cbz_path = os.path.join(tmp_dir, title, cbz_file_name)
        with zipfile.ZipFile(cbz_path, 'w', compression=zipfile.ZIP_DEFLATED) as cbz:
            for root, dirs, files in os.walk(chapter_directory):
                for file in files:
                    self.file_path = os.path.join(chapter_directory, file)
                    cbz.write(self.file_path)

    def make_dir(directory):
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def remove_after_cbz(chapter_directory):
        if os.path.exists(chapter_directory):
            shutil.rmtree(chapter_directory, ignore_errors=True)

    def clear_terminal():
        os.system('cls' if os.name == 'nt' else 'clear')


config = configparser.ConfigParser()
config.read("config.ini")

base_url = config.get("Settings", "base_url")
tmp_dir = Argument().directory()
page_num = 1

page_num = Argument().page(page_num)
url,issearch = Argument().search(base_url, page_num)
print(url)
Misc.clear_terminal()
if issearch == False:
    while True:
        comic_status,status_invalid = MainPrompt().get_status()
        if status_invalid == True:
            continue
        elif comic_status == "":
            Misc.clear_terminal()
            break
        else:
            comic_status = "status=" + comic_status
            Misc.clear_terminal()
            break
    while True:
        comic_type,type_invalid = MainPrompt().get_type()
        if type_invalid == True:
            continue
        elif comic_type == "":
            Misc.clear_terminal()
            break
        else:
            comic_type = "&type=" + comic_type
            Misc.clear_terminal()
            break
    while True:
        comic_order,order_invalid = MainPrompt().get_order()
        if order_invalid == True:
            Misc.clear_terminal()
            continue
        elif comic_order == "":
            Misc.clear_terminal()
            break
        else:
            comic_order = "&order=" + comic_order
            Misc.clear_terminal()
            break
    url = Scrap().comic_url(comic_status, comic_type, comic_order, page_num)
    print(url)
main_html = Network().get_html(url)
comic_list,max_entry = Scrap().display_comic_list(main_html, page_num)
if max_entry <= 0:
    print("Title not found. try searching with other keyword.")
    sys.exit(1)
else:
    istitle,entry_num,page_num = MainPrompt().entry_prompt(comic_list, page_num, max_entry, issearch)
if istitle == False:
    while True:
        if issearch == True:
            url,issearch = Argument().search(base_url, page_num)
        else:
            url = Scrap().comic_url(comic_status, comic_type, comic_order, page_num)

        main_html = Network().get_html(url)
        comic_list,max_entry = Scrap().display_comic_list(main_html, page_num)
        istitle,entry_num,page_num = MainPrompt().entry_prompt(comic_list, page_num, max_entry, issearch)
        print(entry_num)
        if istitle == True:
            break

comic_entry,title,comic_url,cover_url = Scrap().get_comic_info(comic_list, entry_num)
entry_html = Network().get_html(comic_url)
chapter_list,chapters,lastest_chapter,first_chapter = Scrap().get_chapter_info(entry_html)
while True:
    MainPrompt().chapter_selector(tmp_dir, title, first_chapter, lastest_chapter, chapters, chapter_list, cover_url)
