import toml


class ValidationError(Exception):
    pass


class ConfigurationError(Exception):
    pass


class Configs:
    def __init__(self, **kwargs):
        self._config = self._from_file("config.toml")
        self._load()

    def _load(self):
        self.iyo_id = self._config["iyo"]["id"]
        self.validate(self.iyo_id, str)
        self.iyo_secret = self._config["iyo"]["secret"]
        self.validate(self.iyo_secret, str)
        self.serverip = self._config["main"]["server_ip"]
        self.validate(self.serverip, str)
        self.result_path = self._config["main"]["result_path"]
        self.validate(self.result_path, str)
        self.chat_id = self._config["telegram"]["chat_id"]
        self.validate(self.chat_id, str)
        self.bot_token = self._config["telegram"]["token"]
        self.validate(self.bot_token, str)
        self.github_token = self._config["github"]["token"]
        self.validate(self.github_token, str)
        self.repos = self._config["github"]["repos"]
        self.validate(self.repos, list)
        self.db_name = self._config["db"]["name"]
        self.validate(self.db_name, str)
        self.db_host = self._config["db"]["host"]
        self.validate(self.db_host, str)
        self.db_port = self._config["db"]["port"]
        self.validate(self.db_port, int)
        self.environment = self._config["environment"]
        self.validate(self.environment, dict)

    def _from_file(self, filepath):
        try:
            config = toml.load(filepath)
        except toml.TomlDecodeError as e:
            raise ConfigurationError(e)
        return config

    def validate(self, value, type):
        if not isinstance(value, type):
            raise ValidationError(f"{value} should be {type}")
