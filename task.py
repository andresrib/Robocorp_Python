from CustomSelenium import CustomSelenium
from robocorp.tasks import task

@task
def yahoo_search():
    selenium = CustomSelenium()
    selenium.set_web_driver()
    selenium.open_url("https://news.yahoo.com/")
    selenium.search("magic, the gathering")

