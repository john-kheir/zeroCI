## Installation and running
### Requirements:

- Create a vm with Ubuntu:18.04.
- Install [JSX](https://github.com/threefoldtech/jumpscaleX_core/tree/development/docs/Installation)
- Create a Telegram group chat.
- Create Telegram bot and add it to this group chat.
- Install redis and mongodb `apt-get install -y redis mongodb`
- Clone the repository and install packages required.
    ```bash
    mkdir -p /sandbox/code/github/threefoldtech
    cd /sandbox/code/github/threefoldtech
    git clone https://github.com/threefoldtech/zeroCI.git
    cd zeroCI
    pip3 install -r install/requirement.txt
    ```

### Configuration:

- config.toml:

```
[main]
domain=                             # The domain that will point to your server
result_path=                        # The result log file will stored in

[telegram]
chat_id=                            # Telegram chat ID
token=                              # Telegram bot token

[iyo]
id=                                 # itsyouonline ID
secret=                             # itsyouonline secret

[github]
access_token=                       # Github access token for user
repos=                               # list of  repositories Full name that will run on your zeroCI

[db]
name=                               # db name will be used to store the result in
host=                               # hostname that mongodb is running on (exp: localhost)
port=                               # port that mongodb is running on

[environment]                       # under this a list of environment variables needed to be exported before running tests.
```

### How to run the server:

```bash
bash install/run.sh
```
