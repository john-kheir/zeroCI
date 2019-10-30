## ZeroCI life cycle:
### There are two scenarios in which a build will be triggered:

#### 1- Pushing in repo already defined in [config file](../config.toml):
 For such a scenario, the following steps will be done:

- When a commit is pushed, Automatically a job is created and stored in redis.
- A worker will take this job and start to execute it. (Note: There are 5 workers that can handle only up to 5 jobs max).
- A vm will be created using flist on freefarm.
- Run installation commands against this vm as defined in zeroCI.yaml.
- Store the result in database in failure case.
- Run tests commands one by one against this vm as defined in zeroCI.yaml.
- Store the result in database.
- Send result url to telegram and update commit status on github.

#### 2- Scheduled nightly builds:
For such a scenario, the following steps will be done:

- Make post request with install commands, tests commands, timeout and execution time.
- Store this job in scheduler.
- A worker will pick up this job at the specified execution time defined by the scheduler.
- A vm will be created using flist on freefarm.
- Run installation commands against this vm as defined in zeroCI.yaml.
- Store the result in database in case of failure.
- Run tests commands one by one against this vm as defined in zeroCI.yaml.
- Store the result in database.
- Send result url to Telegram.