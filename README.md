## Zero Continuous-Integration:

ZeroCI is continuous integration dedicated for python projects that generates test summary into xml file and it is integrated with Github and Telegram.

### ZeroCI life cycle:
This (section)[] is added to talk more about the ZeroCI life cycle and explain how things work internally.

#### There are two scenarios in which a build will be triggered:

##### 1- Pushing in repo already defined in [config file](config.toml):
 For such a scenario, the following steps will be done:

- When a commit is pushed, Automatically a job is created and stored in redis.
- A worker will take this job and start to execute it. (Note: There are 5 workers that can handle only up to 5 jobs max).
- A vm will be created using flist on freefarm.
- Run installation commands against this vm as defined in zeroCI.yaml.
- Store the result in database in failure case.
- Run tests commands one by one against this vm as defined in zeroCI.yaml.
- Store the result in database.
- Send result url to telegram and update commit status on github.

##### 2- Scheduled nightly builds:
For such a scenario, the following steps will be done:

- Make post request with install commands, tests commands, timeout, execution time.
- Store this job in scheduler.
- A worker will pick up this job at the specified execution time defined by the scheduler.
- A vm will be created using flist on freefarm.
- Run installation commands against this vm as defined in zeroCI.yaml.
- Store the result in database in case of failure.
- Run tests commands one by one against this vm as defined in zeroCI.yaml.
- Store the result in database.
- Send result url to Telegram.

### ZeroCI Installation:

For installation and running ZeroCI, please check it [here](/install/README.md)

### Github Repository Under Test (RUT) configuration:

There are 3 main steps to hook the RUT and make it run against ZeroCI:

#### 1- Configure RUT Webhook:

Go to the repository's setting to configure the webhook
- Add payload URL with providing the server ip and make sure it ends with `/trigger`.
- Content type should be `application/json`.
- Select when the webhook will trigger the server. (**Note:** `Just the push event` is the only supported option for now)
![webhook](pictures/webhook.png)

#### 2- Add zeroCI.yaml file to the RUT:

- Add a file called `zeroCI.yaml` to the home of your repository.
  ![zeroci location](/pictures/repo_home.png)
- This file contains the project's prerequisites, installation and test scripts:
    - `prequisties`: requirements needed to be installed before starting project installation.
      (**Note:** `jsx` and `docker` only supported)
    - `install`: list of bash commands required to install the project.
    - `script`: list of bash commands needed to run the tests ([more details](#zeroci-script-configuration)).

![zeroci](/pictures/zeroci.png)

#### 3- Update ZeroCI [config.toml](config.toml):

- Full name of the repository should be added to [config.toml](config.toml).
- Restart the server: `systemctl restart zero_ci`

### Getting the results:

#### 1- ZeroCI Dashboard:

- Go to server ip that has been already added in `config.toml`
- Once a commit has been pushed, it will be found with a pending status.
  ![server pending](/pictures/server_pending.png)
- When the test finishes, the status will be updated.
- Press the result ID to view the [result details](#result-details).
  ![server done](/pictures/server_done.png)
- Please browse to ZeroCI [dashboard](/pictures/dashboard.png) to view repos cards in which each card contains  info about current
  repo, last build status, etc.
(**Note:** The only current used branch is `development`)



#### 2- Github status

- Once a commit has been pushed to RUT, if you go to the repository commits, you will find a yellow message indicating 
  that some checks haven't been compeleted yet.
  ![github pending](/pictures/github_pending.png)
- When the tests run finishes, the status will be updated.
  ![github done](/pictures/github_done.png)
- Please press 'Details' link to view [result details](#result-details).


#### 3- Telegram group chat:

- If you want to get a message with the build status on telegram chat, please provide the telegram required info in  `config.toml`.

  ![telegram done](/pictures/telegram_done.png)
- Please press the `Result` button for viewing [result details](#result-details).

#### Result details:

- Black formatting result will appear at the beginning.
- Then you can see the run results related to the tests added under `script` field in [ZeroCI.yaml](#2--zerociyaml).
  ![result details](/pictures/result_details.png)

- For more details about every test, please press on the test name.
  ![more details](/pictures/more_details.png)
  (**Note:** if the test run didn't generate junit test summary into xml file, the result will appear in log format as running in shell.)

### zeroci script configuration:

This part is important for getting result in this [view](#result-details)

#### Nosetests:

`--with-xunit`: to enable the plugin to generate junit test summary into xml file.
`--xunit-file`: specify the output file name, in this case MUST be `/test.xml`.  
`--xunit-testsuite-name`: name of testsuite that will appear in the result.

##### Example:
```bash
nosetests-3.4 -v testcase.py --with-xunit --xunit-file=/test.xml --xunit-testsuite-name=Simple_nosetest
```
For more details about the plugin [Xunit](https://nose.readthedocs.io/en/latest/plugins/xunit.html)

#### Pytest:

`--junitxml`: to enable the plugin and specify the output file name, in this case MUST be `/test.xml`.
`-o junit_suite_name`: name of testsuite that will appear in the result.

##### Example:
```bash
pytest -v testcase.py --junitxml=/test.xml -o junit_suite_name=Simple_pytest
```
For more details about the plugin [junitxml](https://docs.pytest.org/en/latest/usage.html#creating-junitxml-format-files)

### Nightly tests:

There is an API for adding nightly testsuite, but its page hasn't been added yet.


### Roadmap
Using more of jsx tools as soon as there is a stable release.
