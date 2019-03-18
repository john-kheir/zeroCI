## 0-Test Continuous-Integration

### Server life cycle:

#### Pushing in branch X, the following steps will be done:

    - Server will build an ubuntu 18 image from X branch
    - Create a docker container from this image
    - Get tests commands from 0-Test.sh file from this X branch
    - Run those commands one by one against this docker container
    - Produce a log file with all results 
    - Send log file url to Telegram chat and Change commit status on github

### How to install:

- Create a vm with Ubuntu:18.04.
- Install [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-using-the-repository)
- Create a Telegram group chat.
- Create Telegram bot and add it to this group chat
- Create a docker account (only used after the nightly bulid to push the image)
- config.ini:

```
[main]

server_ip=                          # (http://ip:port) ip should be public
result_path=                        # The result log file will stored in

[telegram]
chat_id=                            # Telegram chat ID
bot_token=                          # Telegram bot token

[github]
access_token=                       # Github access token for user
repo=threefoldtech/jumpscaleX       # Repository name

[exports]                           # under this a list of environment variables needed to be exported before running tests.
```

- Add server IP as webhook in Repository's settings.

### How tests run:

Repo/0-Test.sh should has bash commands(should one line for each test) for how to run tests.

If this file is not found, it will result in `Didn't find tests` in result log file.
### How to run the server:

```bash
python3.6 0-Test.py
```
