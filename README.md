## Zero Continuous-Integration:


### Server life cycle:
#### There are two scenarios:

##### 1- Pushing in repo already defined in config file, the following steps will be done:

    - Create a job on rq and store it in redis.
    - There are 5 workers waiting for jobs, one of them will take this job and start to execute it.
    - Create a vm using flist on freefarm.
    - Get installaltion and tests commands from zeroCI.yaml file for this commit.
    - Run installation commands against this vm.
    - Store the result in DB (mongodb) in failure case.
    - Run tests commands one by one aganist this vm.
    - Store the result in DB (mongodb).
    - Send result url to Telegram and update commit status om github.

##### 2- Run nightly testsuites:

    - Make post request with install commands, tests commands, timeout, executeion time.
    - Store this job in rq scheduler.
    - rq scheduler will run this job on its execution time on rq workers.
    - Create a vm using flist on freefarm.
    - Get installation and tests commands from rq scheduler.
    - Run installation commands against this vm.
    - Store the result in DB (mongodb) in failure case.
    - Run tests commands one by one aganist this vm.
    - Store the result in DB (mongodb).
    - Send result url to Telegram.
    
### How to install:

- Create a vm with Ubuntu:18.04.
- Install [JSX](https://github.com/threefoldtech/jumpscaleX/tree/development_jumpscale_testing/docs/Installation#insystem-install)
- Create a Telegram group chat.
- Create Telegram bot and add it to this group chat.
- Install mongodb `apt-get install -y mongodb`
- Install redis `apt-get install -y redis`
- Install packages required `pip3 install -r requirement.txt`
- config.toml:

```
[main]
domain=                             # The domain that will point to your server
result_path=                        # The result log file will stored in

[telegram]
chat_id=                            # Telegram chat ID
token=                              # Telegran bot token

[iyo]
id=                                 # itsyouonline ID
secret=                             # itsyouonline secret

[github]
access_token=                       # Github access token for user
repo=                               # Repositories Full name that will run on your zeroCI

[db]
name=                               # db name will be used to store the result in
host=                               # hostname that mongodb is running on (exp: localhost)
port=                               # port that mongodb is running on

[environment]                       # under this a list of environment variables needed to be exported before running tests.
```

- Add server IP as webhook in Repository's settings.

### How to run the server:
```bash
./run.sh
```
