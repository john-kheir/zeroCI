from githubs.githubs import Github
from telegrams.telegrams import Telegram
from .config import Configs

github = Github()
telegram = Telegram()
SUCCESS = "success"
FAILURE = "failure"


class Reporter(Configs):
    def report(self, id, db_run, project_name=None):
        """Report the result to github commit status and Telegram chat.

        :param status: test status. 
        :type status: str
        :param file_name: result file name. 
        :type file_name: str
        :param repo: full repo name
        :type repo: str
        :param branch: branch name. 
        :type branch: str
        :param commit: commit hash.
        :type commit: str
        :param committer: committer name on github. 
        :type committer: str
        """
        run = db_run.objects.get(id=id)
        msg = self.report_msg(status=run.status, project_name=project_name)
        if not project_name:
            github.status_send(status=run.status, repo=run.repo, link=self.serverip, commit=run.commit)
            telegram.send_msg(
                msg=msg + self.serverip, repo=run.repo, branch=run.branch, commit=run.commit, committer=run.committer
            )
        else:
            telegram.send_msg(msg=msg + self.serverip)

    def report_msg(self, status, project_name=None):
        if project_name:
            name = f"{project_name} tests"
        else:
            name = "Tests"
            if status == SUCCESS:
                msg = f"✅ {name} passed "
            elif status == FAILURE:
                msg = f"❌ {name} failed "
            else:
                msg = f"⛔️ {name} errored "

        return msg
