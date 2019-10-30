cp ./services/* /etc/systemd/system
systemctl start mongodb
systemctl start redis
systemctl start zero_ci
systemctl enable zero_ci
systemctl start rq_scheduler
systemctl enable rq_scheduler
for i in {1..5}
do 
systemctl start rqworker\@$i
systemctl enable rqworker\@$i
done