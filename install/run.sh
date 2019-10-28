cp ./services/* /etc/systemd/system
systemctl start zeroci
systemctl enable zeroci
systemctl start rq_scheduler
systemctl enable rq_scheduler
for i in {1..5}
do 
systemctl start rqworker\@$i
systemctl enable rqworker\@$i
done