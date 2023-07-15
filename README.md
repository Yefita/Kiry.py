# Kiry.py

Kiry.py is a scraper for indonesian-translated-eastern-style-comics pirate site: Kiryuu, written in python.

## Instalation

I write this for use on termux and not anything else. in theory it should work in anything that run lastest python3. but, its not tested.


To install this script just clone the repo:

    git clone https://github.com/Yefita/Kiry.py.git


## Usage
    
To run it: cd to Kiry.py directory then run Kiry.py. also make sure that you have all dependency installed on your devices.

    cd Kiry.py &&
    python3 Kiry.py


There also some argument you can use:

    usage: Kiry.py [-h] [-v] [-s SEARCH] [-p PAGE] [-C COOKIE] [-U USER_AGENT]

    options:
      -h, --help            show this help message and exit
      -v, --version         Print version number then exit.
      -s SEARCH, --search SEARCH
                            Search comic title
      -p PAGE, --page PAGE  Display page number of choice, instead of starting from 1st page
      -C COOKIE, --cookie COOKIE
                            Use cookie incase of Cloudflare low level blocking. it won't work on high level. to remove cookie use "--cookie off".
      -U USER_AGENT, --user-agent USER_AGENT
                            Change UA. Make sure it match with your browser(that you take the cookie from) if you use cookie. to set UA to default value use "--user-agent default"

## User-Agent and Cookies

! IMPORTANT !

Cookie and User Agent are stored on config.ini file in PLAIN TEXT. Dont give it to anyone! only add cookie that belong to domain "https://kiryu.id".



This features is almost never tested. Since I only encounter cloudflare blocking once, and its gone in a day. I added it when i rewrite the script, and I dont want to remove it. Dont use it unless the script needed it to function.

The script doesnt even have a way to check if cloudflare block it. it will only crash trowing some error. in my testing it does work but dont expect too much.

### User-agent

To set the user-agent just use --user-agent or -U :

    python3 Kiry.py --user-agent "<USER-AGENT>"

example :

    python3 Kiry.py --user-agent "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"

### Cookies

For cookies use --cookie or -C the format should like this :

    python3 Kiry.py --cookie "cookie-name1=cookie-value1, cookie-name2=cookie-value1"

exmple :

    python3 Kiry.py --cookie "dsq__=0hv5l7no50o9b, cf_clearance=oFOuTwW6QlIrC0hehkMQUWGB7z3_wK6V3oSl6p9wzEs-16205947-0-160"

## Why?

I write this script to learn about python and web scraping, and just think i'll start from something simple. also yes this is my 1st python script, don't be too harsh to me.

## Others

  - if you encounter an error: well.. good luck!
  - if the website change: thats the day this script die, I wont update this script.
  - if you're the owner of Kiryuu: ma'ap bang. E-mail: zueyenfe@gmail.com or Discord: yellowfin_tuna (will take it down if you ask so)
