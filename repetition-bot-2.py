from sys import argv
from datetime import datetime
from random import choice, randint
from time import sleep
from os import remove, path, mkdir

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from config import *
from invisibles import *

# create an ID for identifying debug files
run_ID = str(randint(10000000,99999999))

# configure environment variables for path extension
if "remote" in argv:                     
    path_extension = path_extensions["remote"]
else:
    path_extension = path_extensions["local"]

# make sure folders are in place
folders = [
    path_extension + "debug/",
    path_extension + "chrome/"
]
for folder in folders:
    if not path.isdir(folder):
        mkdir(folder)

# blueprint for webdriver with required Twitter methods
class Bot:

    # create a webdriver on initialization as self.driver and go to Twitter; handle exception here
    def __init__(self):
        try:
            print("Initializing driver…")
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--remote-debugging-port=9222") # https://stackoverflow.com/a/56638103/13100363
            options.add_argument("--headless")
            options.add_argument("user-data-dir=" +  path_extension + "chrome/")    # stay logged in
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-dev-shm-usage")
            #options.add_argument("--auto-open-devtools-for-tabs")
            self.driver = webdriver.Chrome("/usr/local/bin/chromedriver", options=options)
            self.driver.implicitly_wait(10)
            self.driver.get("https://twitter.com/")
            print("Driver initialized.")
        except Exception as e:
            print("Error initializing driver:",e)
            exit()

    # log in to Twitter on the standard screen; exception handled in run() function
    def login(self,identity,password):
        print("Logging in to Twitter…")

        # wait then take screenshot and save source for debugging
        sleep(1)
        self.driver.get_screenshot_as_file(path_extension + "debug/" + run_ID + "-screenshot-login.png")
        with open(path_extension + "debug/" + run_ID + "-source-login.html", "w") as f:
            f.write(self.driver.page_source)

        username_field = self.driver.find_element_by_name("session[username_or_email]")
        password_field = self.driver.find_element_by_name("session[password]")
        username_field.send_keys(identity)
        password_field.send_keys(password, Keys.ENTER)
        print("Login sent.")

    # NIGHTMARE: log in to Twitter via the random "getting started" popup screen; handle exceptions here
    def getStartedLogin(self,username,email,password):
        try:
            print("Attempting “get started” login…")
            username_field = self.driver.find_element_by_tag_name("input")  # will work on first screen
            username_field.send_keys(username, Keys.ENTER)
            print("Username submitted successfully. Testing password submission…")

            # attempt the password field immediately for the 2-step version
            try:
                # to test which flow we are in, this needs to be explicit
                password_field = self.driver.find_element_by_xpath("//*[@id=\"react-root\"]/div/div/div[2]/main/div/div/div/div[2]/div[2]/div[1]/div/div[2]/div/label/div/div[2]/div/input")
                password_field.send_keys(password, Keys.ENTER)
                print("Password submitted successfully! ”Get started” login complete.")

            # do both email and then password for the 3-step version
            except Exception as e:
                print("Error entering password:",e)
                print("Attempting additional step with email entry…")
                email_field = self.driver.find_element_by_tag_name("input") # for 3-step, we can use "input"
                email_field.send_keys(email, Keys.ENTER)
                password_field = self.driver.find_element_by_tag_name("input")
                password_field.send_keys(password, Keys.ENTER)
                print("”Get started” login sent.")
            
            # changing IP can cause a 4-step version with phone credential to be triggered
            # but it is not worth time trying to navigate it now, it shouldn't appear normally (?)
            # CAPTCHA step will totally defeat the bot, but normal use shouldn't trigger it (?)

        except Exception as e:
            print("“Get started” login failed:",e)
            self.driver.quit()
            exit()

    # send the phone number for the addititional "suspicious activity" screen; handle exception in run()
    def sendPhoneCredential(self):
        phone_field = self.driver.find_element_by_xpath("//*[@id=\"challenge_response\"]")
        phone_field.send_keys(phone, Keys.ENTER)
        print("Phone credential sent.")

    # post a tweet once logged in to Twitter; handle exception in run() function
    def postTweet(self):
        print("Posting tweet…")

        # wait and take screenshot for debugging
        sleep(1)
        self.driver.get_screenshot_as_file(path_extension + "debug/" + run_ID + "-screenshot-post.png")
        with open(path_extension + "debug/" + run_ID + "-source-post.html", "w") as f:
                f.write(self.driver.page_source)

        tweet_box = self.driver.find_element_by_xpath("//*[@id=\"react-root\"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/label/div[1]/div/div/div/div/div[2]/div")
        tweet_box.send_keys(generateTweetText())
        tweet_button = self.driver.find_element_by_xpath("//*[@id=\"react-root\"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[3]/div/div/div[2]/div[3]")
        tweet_button.click()
        print("Tweet sent successfully.")
        self.driver.quit()
        deleteFiles()           # only delete if the tweet was send successfully!
            
# generate the tweet text, containing a novel invisible string each time
# this must be inserted in the middle, since Twitter trims invisibles from the end before posting
def generateTweetText():
    tweet_text = "“What would life be without repetition?”\n"
    tweet_text += generateNonIdentity()
    tweet_text += "\n— Søren Kierkegaard"
    return tweet_text

# 14^20 possible empty strings ought to be enough
# we want short-ish strings so as not to add an extra line
def generateNonIdentity():
    empty_string = ""
    for i in range(20):
        empty_string += choice(list(invisible_characters.values()))
    return(empty_string)

# remove files if the bot ran successfully / no debug required
def deleteFiles():
    debug_files = [
        path_extension + "debug/" + run_ID + "-screenshot-login.png",
        path_extension + "debug/" + run_ID + "-source-login.html",
        path_extension + "debug/" + run_ID + "-screenshot-post.png",
        path_extension + "debug/" + run_ID + "-source-post.html"
    ]
    for debug_file in debug_files:
        if path.isfile(debug_file):
            remove(debug_file)

# instantiate the bot and attempt to navigate the possible screens
def run():

    print("---\nRunning repetition-bot-2.py at",str(datetime.now()),"| Run ID:",run_ID,"| Params:",argv[1:])

    bot = Bot()                 # create bot set to twitter.com

    try:                        # just assume we are logged in and can post a tweet

        bot.postTweet()

    except Exception as e:      # if tweeting fails, try the various login + post flows

        print("Error posting tweet:",e)
        print("Attempting to login…")
        bot.driver.get("https://twitter.com/login/")

        # control for random "get started" popup screen; trigger special login method for this screen
        try:
            bot.login(username,password)
        except Exception as e:
            print("Error logging in to Twitter:",e)
            bot.getStartedLogin(username,email,password)
                
        # control for "suspicious login attempts" messages; try first the phone-number screen then the second login with email credential
        try:
            bot.postTweet()
        except Exception as e:
            print("Error posting Tweet:",e)
            print("Beginning extended login flow.")
            try:
                phone_done = False      # don't repeat the phone test if it was done successfully
                try:
                    print("Attempting to send phone credential…")
                    bot.sendPhoneCredential()
                    phone_done = True
                except:
                    print("Phone credential was not required.")
                try:
                    print("Attempting login with email credential…")
                    bot.login(email,password)
                except:
                    print("Email credential was not required.")
                if not phone_done:
                    try:
                        print("Attempting to send phone credential a second time…")
                        bot.sendPhoneCredential()
                    except:
                        print("Phone credential was not required.")
                bot.postTweet()
            except Exception as e:
                print("Extended login flow failed:",e)
                bot.driver.quit()
                exit()

    print("Finished.")

run()