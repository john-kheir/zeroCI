from subprocess import run, PIPE
import sys, unittest


class Black(unittest.TestCase):
    def execute_cmd(self, cmd):
        response = run(cmd, shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE, encoding="utf-8")
        return response

    def black_test(self, path):

        cmd = 'black {} -l 120 -t py37 --diff --exclude "templates"'.format(path)
        response = self.execute_cmd(cmd)
        if response.returncode:
            raise RuntimeError(response.stderr)
        else:
            self.assertNotIn("reformatted", response.stderr.strip())


if __name__ == "__main__":
    path = sys.argv[1]
    black = Black()
    black.black_test(path)
