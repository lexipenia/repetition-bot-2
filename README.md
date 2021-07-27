# repetition-bot-2

An updated version of the [original repetition-bot](https://github.com/lexipenia/repetition-bot) that bypasses the Twitter API and instead uses Selenium to control an automated Chrome instance. This may prove more resilient against Twitter's attempts to block people posting the same thing again and again.

The bot is able to navigate a couple of Twitter's login flows fairly well:
* Standard login
* "Get started" login that seems to appear at random, including 2-, 3- and 4-step versions
* "Account security" follow-up requests after first login succeeds

By making the bot save Chrome user preferences, however, it should avoid having recourse to using these flows frequently. The "get started" flow proves especially resistent to automation and may only work on my local machine.

## `config.py` and `chromedriver` location

The bot assumes that the appropriate version of [chromedriver](https://chromedriver.chromium.org/downloads) is installed at `/usr/local/bin/chromedriver`.

A `config.py` file in the same directory as the bot must be supplied, containing:
* The root of the path where `/chrome` and `/debug` directories will be created
* The desired Twitter login credentials

Example:
```
# choose how to extend the path for saving files (remote = absolute, for cronjob)
path_extensions = {
  "local": "./",
  "remote": "/home/<user>/repetition-bot-2/"
}

# Twitter login credentials
username = ""
password = ""
email = ""
phone = ""
```

## Dependencies
```
pip install selenium
```