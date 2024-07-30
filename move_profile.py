from random import randint
from aiohttp import ClientSession
from bs4 import BeautifulSoup


async def move_to_profile(moodle: str, user: str, password: str, link: str) -> bool:
    headers: dict = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"}
    async with ClientSession(headers=headers) as session:
        # Get logintoken
        #print("Get logintoken...")
        async with session.get(moodle + "/login/index.php") as resp:
            login_html = await resp.text()

            login_payload = {
                "anchor": "",
                "username": user,
                "password": password,
                "rememberusername": 1,
            }
            try:
                soup = BeautifulSoup(login_html, "html.parser")
                logintoken = soup.find("input", attrs={"name": "logintoken"})["value"]
                login_payload["logintoken"] = logintoken
                #print("Logintoken:", logintoken)
            except:
                pass

        # Attemp login
        #print("Attemp login...")
        async with session.post(url=moodle + "/login/index.php", data=login_payload) as resp:
            dashboard_html = await resp.text()
            if str(resp.url).lower().endswith("/login/index.php"):
                print("LoginERROR")
                return False
            print("Logged")

        # Getting basic profile data
        #print("Getting profile current data...")
        async with session.get(moodle + "/user/edit.php") as resp:
            profile_html = await resp.text()
            try:
                soup = BeautifulSoup(profile_html, "html.parser")
                sesskey = soup.find("input", attrs={"name": "sesskey"})["value"]
                firstname = soup.find("input", attrs={"name": "firstname"})["value"]
                lastname = soup.find("input", attrs={"name": "lastname"})["value"]
                email = soup.find("input", attrs={"name": "email"})["value"]
                try:
                    description = str(soup.find("textarea", attrs={"name": "description_editor[text]"}).contents[0])
                except:
                    description = ""
            except:
                print("profileERROR")
                return False

        # Edit profile description
        #print("Attemp edit profile...")
        profile_payload = {
            "sesskey": sesskey,
            "_qf__user_edit_form": "1",
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "description_editor[format]": "1",
            "description_editor[itemid]": str(randint(100000000, 999999999)),
            "description_editor[text]": description + "\n<p>" + link + "</p>",
        }
        async with session.post(url=moodle + "/user/edit.php", data=profile_payload) as resp:
            await resp.text()

        # Get the last item of the list
        #print("Get last link...")
        async with session.get(moodle + "/user/profile.php") as resp:
            new_profile_html = await resp.text()
            try:
                soup = BeautifulSoup(new_profile_html, "html.parser")
                description = str(soup.find("div", attrs={"class": "description"}))
                #print(description)
                soup = BeautifulSoup(description, "html.parser")
                last_link = soup.findAll("p")[-1].contents[0]
                #print("Last link:", last_link)
                return last_link
            except:
                print("getlinkERROR")
                return False
