## Zero Continuous-Integration:

ZeroCI is continuous integration dedicated for python projects that generates test summary into xml file and it is inetgrated with Github and Telegram.

### Server life cycle:

#### There are two scenarios:

##### 1- Pushing in repo already defined in config file, the following steps will be done:

- Create a job and store it in redis.
- There are 5 workers waiting for jobs, one of them will take this job and start to execute it.
- Create a vm using flist on freefarm.
- Get installation and tests commands from zeroCI.yaml file for this commit.
- Run installation commands against this vm.
- Store the result in DB in failure case.
- Run tests commands one by one against this vm.
- Store the result in DB.
- Send result url to Telegram and update commit status on github.

##### 2- Run nightly testsuites:

- Make post request with install commands, tests commands, timeout, execution time.
- Store this job in scheduler.
- scheduler will run this job on its execution time on workers.
- Create a vm using flist on freefarm.
- Get installation and tests commands from scheduler.
- Run installation commands against this vm.
- Store the result in DB in failure case.
- Run tests commands one by one against this vm.
- Store the result in DB.
- Send result url to Telegram.

### Installation:

For [installation and running](/install/README.md)

### Github repository configuration:

#### 1- Webhook:

Go to the repository's setting to configure the webhook
- Add the ip of the server ended with `/trigger`.
- Content type should be `application/json`.
- Select when the webhook will trigger the server. (**Note:** `Just the push event` is only supported for now)
![webhook](pictures/webhook.png)

#### 2- zeroCI.yaml:

- This file should be at the home of the repository with name `zeroCI.yaml`.
  ![zeroci location](/pictures/repo_home.png)
- Should contain the project prerequisites, installation and test scripts:
    - `prequisties`: requirement needed to be installed before start installing the project.
      (**Note:** `jsx` and `docker` only supported)
    - `install`: list of bash command lines for how to install the project.
    - `script`: list of bash command lines for how to run the tests ([more details](#zeroci-script-configuration)).

![zeroci](/pictures/zeroci.png)

#### 3- Server configuration:

- Full name of the repository should be added in `config.toml`.
- Restart the server `systemctl restart zeroci`

### Getting the results:

#### 1- The server front-end itself:

- Go to server ip that has been already added in `config.toml`
- Once the repository has commit, it will be found.
  ![server pending](/pictures/server_pending.png)
- When the test finishes, the status will be updated.
  ![server done](/pictures/server_done.png)
- result id can be pressed for [result details](#result-details).
(**Note:** if the branch used is `development`, will find a card with the latest status in server dashboard)
![dashboard](/pictures/dashboard.png)


#### 2- Github status

- Once the repository has commit go to repository commits.
  ![github pending](/pictures/github_pending.png)
- When the test finishes, the status will be updated.
  ![github done](/pictures/github_done.png)
- `details` can be pressed for [result details](#result-details).

#### 3- Telegram group chat:

- In telegram group chat has been created in requirement step and added in `config.toml`, a message will be sent to it once the test finishes.

  ![telegram done](/pictures/telegram_done.png)
- `Result` button can be pressed for [result details](#result-details).

#### Result details:

- Black formatting will appear at the beginning.
- Then the rest of tests added in [zeroci](#2--zerociyaml) in `script` field.
  ![result details](/pictures/result_details.png)

- For more details about every test, test name can be pressed.
  ![more details](/pictures/more_details.png)
  (**Note:** if the test running does not generate junit test summary into xml file, the result will appear in log format as running in shell.)

### zeroci script configuration:

This part is important for getting result in this [view](#result-details)

#### Nosetests:

`--with-xunit`: to enable the plugin to generate junit test summary into xml file.
`--xunit-file`: specify the output file name, in this case MUST be `/test.xml`.  
`--xunit-testsuite-name`: name of testsuite that will appear in the result.

**Example:**
```bash
nosetests-3.4 -v testcase.py --with-xunit --xunit-file=/test.xml --xunit-testsuite-name=Simple_nosetest
```
For more details about the plugin [Xunit](https://nose.readthedocs.io/en/latest/plugins/xunit.html)

#### Pytest:

`--junitxml`: to enable the plugin and specify the output file name, in this case MUST be `/test.xml`.
`-o junit_suite_name`: name of testsuite that will appear in the result.

**Example:**
```bash
pytest -v testcase.py --junitxml=/test.xml -o junit_suite_name=Simple_pytest
```
For more details about the plugin [junitxml](https://docs.pytest.org/en/latest/usage.html#creating-junitxml-format-files)

### Nightly tests:

There is an API for adding nightly testsuite, but its page not added yet.


### Roadmap
Using more of jsx tools as soon as there is a stable release.