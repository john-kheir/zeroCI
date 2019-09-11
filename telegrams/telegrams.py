import time

from telegram import Bot

from utils.config import Configs

RETRIES = 5


class Telegram(Configs):
    def __ini__(self, **kwargs):
        super.__init__(self, **kwargs)
        self.telegram_cl = Bot(self.bot_token)

    def send_msg(self, msg, repo=None, branch=None, commit=None, committer=None):
        """Send Telegram message using Telegram bot.

        :param msg: message to be sent.
        :type msg: str
        :param repo: full repo name
        :type repo: str
        :param branch: branch name
        :type branch: str
        :param commit: commit hash.
        :type commit: str
        :param committer: committer name on github.
        :type committer: str
        """
        if commit:
            msg = "\n".join([msg, repo, branch, committer, commit])
        for _ in range(RETRIES):
            try:
                self.telegram_cl.send_message(chat_id=self.chat_id, text=msg)
                break
            except Exception:
                time.sleep(1)
