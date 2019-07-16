set -ex
apt-get update; apt-get install -y python3.6 curl git locales language-pack-en rsync unzip python3-pip
mkdir -p /root
cd /root
git clone --branch $branch https://github.com/AhmedHanafy725/test.git
cd test
git reset --hard $commit
pip3 install pytest nose black