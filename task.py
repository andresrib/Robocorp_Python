from CustomSelenium import CustomSelenium

def yahoo_search():
    selenium = CustomSelenium()
    selenium.set_web_driver()
    selenium.open_url("https://news.yahoo.com/")
    selenium.search("magic, the gathering")

if __name__ == "__main__":
    yahoo_search()
