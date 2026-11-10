# CDNFLY
仅支持CentOS 7.x

web目录为云端验证文件，请自行搭建

wget https://raw.githubusercontent.com/freejbgo/CDNFLY/main/web/web.tar.gz

tar -zxvf web.tar.gz



注意：验证服务器用bt安装，并且php版本为5.6


0.0.0.0改成(自己搭建的验证服务器IP，主控全部需要设置，节点只需要设置auth)

vi /etc/hosts

0.0.0.0 auth.cdnfly.cn (主控和节点都要设置)

0.0.0.0 monitor.cdnfly.cn（只需主控设置）

0.0.0.0 update.cdnfly.cn（只需主控设置）


主控登录地址为: http://主控IP/

管理员账号和密码： wenjian/wenjian

普通用户账号和密码： ceshi/ceshi



备注：

监控默认是使用云端服务器去请求CDN节点，因此要保持云端和CDN节点之间的网络畅通。另外如果是用宝塔面板，php不要安装bt_safe扩展，否则无法使用tcp类型监控；如果要用ping类型监控，还需要允许exec函数。

支持多节点监控（和官方一样），要添加其它监控节点，可以编辑config.php配置文件，根据里面的注释说明添加。



v5.1.13主控

curl -fsSL https://github.com/freejbgo/CDNFLY/raw/main/master.sh -o master.sh && chmod +x master.sh && ./master.sh --es-dir /home/es

或者

curl -fsSL https://github.com/freejbgo/CDNFLY/raw/main/master.sh -o master.sh && chmod +x master.sh && ./master.sh --ver v5.1.13 --es-dir /home/es


v5.1.16被控

curl -fsSL https://github.com/freejbgo/CDNFLY/raw/main/agent.sh -o agent.sh  && chmod +x agent.sh && ./agent.sh --master-ver v5.1.13 --master-ip 1.2.3.4 --es-ip 1.2.3.4 --es-pwd 12345678





一、主控问题解决：
1、
增加安全性，把相关端口只对节点放行：80,88,443,9200,9300


二、节点问题解决：
1、
增加安全性，只允许主控和127.0.0.1访问节点5000端口 (节点重启后可能需要重新执行此命令)

iptables -A INPUT -s 主控ip -p tcp --dport 5000 -j ACCEPT

iptables -A INPUT -s 127.0.0.1 -p tcp --dport 5000 -j ACCEPT

iptables -A INPUT -p tcp --dport 5000 -j DROP

iptables -nL



三、主控操作命令：

1、
修改elasticsearch内存使⽤量

打开⽂件/etc/elasticsearch/jvm.options，找到

-Xms和-Xmx

如：

-Xms4g

-Xmx4g

表示⽬前elasticsearch允许最⼤使⽤4g内存。

修改之后，执⾏重启elasticsearch

service elasticsearch restart



2、
更换yum源


1、cd /etc/yum.repos.d

2、rm -rf CentOS-Base.repo

3、wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo

4、yum clean all

5、rm -rf epel.repo

6、wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo

7、yum clean all

8、yum makecache


如果执行了第4步就可以了，那么后面的可以不做。



3、
升级centOS linux 7.9内核：

先导入一个公钥。

rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org

安装一下CentOS 7.x的ELRepo包。

yum install -y https://www.elrepo.org/elrepo-release-7.el7.elrepo.noarch.rpm

然后依次执行下面的命令，等待进度条走完，下载升级：

yum --enablerepo=elrepo-kernel install kernel-ml -y &&

sed -i s/saved/0/g /etc/default/grub &&

grub2-mkconfig -o /boot/grub2/grub.cfg


重启系统：

reboot



4、
修改文件，vi /etc/sysctl.conf

net.ipv6.conf.all.disable_ipv6 = 0

net.ipv6.conf.default.disable_ipv6 = 0

net.ipv6.conf.lo.disable_ipv6 = 0

net.ipv4.tcp_max_syn_backlog=8192

net.core.somaxconn=40000

net.core.netdev_max_backlog=8096

net.ipv4.tcp_max_tw_buckets=5000

net.ipv4.tcp_fin_timeout=60

net.ipv4.tcp_keepalive_time=7200

net.ipv4.tcp_synack_retries=2

net.ipv4.tcp_syn_retries=6

net.ipv4.ip_local_port_range=32768 60999

net.ipv4.tcp_window_scaling=1

net.ipv4.tcp_moderate_rcvbuf=1

net.core.default_qdisc=pfifo_fast

net.ipv4.tcp_rmem=4096        87380   6291456

net.ipv4.tcp_wmem=4096        16384   4194304

net.core.rmem_max=212992

net.core.wmem_max=212992

net.ipv4.tcp_mem=22746        30329   45492

net.ipv4.tcp_max_orphans=8192

net.core.default_qdisc=fq

net.ipv4.tcp_congestion_control=bbr




5、
重启主控

supervisorctl -c /opt/cdnfly/master/conf/supervisord.conf restart all

重启节点

supervisorctl -c /opt/cdnfly/agent/conf/supervisord.conf restart all




6、
⼿动恢复数据库

假设数据库备份⽂件在/root/cdn.sql.gz，执⾏如下命令恢复:

supervisorctl -c /opt/cdnfly/master/conf/supervisord.conf stop all;

eval grep MYSQL_PASS /opt/cdnfly/master/conf/config.py;

eval grep MYSQL_IP /opt/cdnfly/master/conf/config.py;

eval grep MYSQL_PORT /opt/cdnfly/master/conf/config.py;

eval grep MYSQL_DB /opt/cdnfly/master/conf/config.py;

eval grep MYSQL_USER /opt/cdnfly/master/conf/config.py;

mysql -h$MYSQL_IP -u$MYSQL_USER -p$MYSQL_PASS -P$MYSQL_PORT -e "drop database $MYSQL_DB;create database $MYSQL_DB;"

gunzip < /root/cdn.sql.gz | mysql -h$MYSQL_IP -u$MYSQL_USER -p$MYSQL_PASS -P$MYSQL_PORT $MYSQL_DB

supervisorctl -c /opt/cdnfly/master/conf/supervisord.conf start all;


7、
主控更换ip后节点修改命令

new_master_ip="这里替换为主控IP"

(后台系统升级里查看es_pwd密码)

es_pwd="这里替换为es密码"


sed -i "s/ES_IP =.*/ES_IP = \"$new_master_ip\"/" /opt/cdnfly/agent/conf/config.py

sed -i "s/MASTER_IP.*/MASTER_IP = \"$new_master_ip\"/g" /opt/cdnfly/agent/conf/config.py

sed -i "s/hosts:.*/hosts: [\"$new_master_ip:9200\"]/" /opt/cdnfly/agent/conf/filebeat.yml

chattr -i /usr/local/openresty/nginx/conf/ /usr/local/openresty/nginx/conf/listen_80.conf /usr/local/openresty/nginx/conf/listen_other.conf

sed -i "s#http://.*:88#http://$new_master_ip:88#" /usr/local/openresty/nginx/conf/listen_80.conf /usr/local/openresty/nginx/conf/listen_other.conf

chattr +i /usr/local/openresty/nginx/conf/ /usr/local/openresty/nginx/conf/listen_80.conf /usr/local/openresty/nginx/conf/listen_other.conf

sed -i "s/ES_PWD =.*/ES_PWD = \"$es_pwd\"/" /opt/cdnfly/agent/conf/config.py

sed -i "s/password:.*/password: \"$es_pwd\"/" /opt/cdnfly/agent/conf/filebeat.yml

sed -i "s/agent-pwd:.*/agent-pwd: \"$es_pwd\"/" /opt/cdnfly/agent/conf/filebeat.yml

ps aux | grep [/]usr/local/openresty/nginx/sbin/nginx | awk '{print $2}' | xargs kill -HUP true

supervisorctl -c /opt/cdnfly/agent/conf/supervisord.conf restart filebeat

supervisorctl -c /opt/cdnfly/agent/conf/supervisord.conf restart agent

supervisorctl -c /opt/cdnfly/agent/conf/supervisord.conf restart task


8、
清空绑定的域名

eval grep MYSQL_PASS /opt/cdnfly/master/conf/config.py;

eval grep MYSQL_IP /opt/cdnfly/master/conf/config.py;

eval grep MYSQL_PORT /opt/cdnfly/master/conf/config.py;

eval grep MYSQL_DB /opt/cdnfly/master/conf/config.py;

eval grep MYSQL_USER /opt/cdnfly/master/conf/config.py;

mysql -h$MYSQL_IP -u$MYSQL_USER -p$MYSQL_PASS -P$MYSQL_PORT $MYSQL_DB -e "update config set value='' where name='admin_domain';"

mysql -h$MYSQL_IP -u$MYSQL_USER -p$MYSQL_PASS -P$MYSQL_PORT $MYSQL_DB -e "update config set value='' where name='user_domain';"

mysql -h$MYSQL_IP -u$MYSQL_USER -p$MYSQL_PASS -P$MYSQL_PORT $MYSQL_DB -e "update config set value='' where name='bind-master-host';"

cd /opt/cdnfly/master/conf;

sed -i 's/ALLOW_HOSTS.*/ALLOW_HOSTS=""/' config.py;

supervisorctl restart all;


9、
如何初始化elasticsearch

当elasticsearch出现⽆法解决的异常，或者elasticsearch数据占满了硬盘，可以执⾏此操作来初始化elasticsearch，注意：初始化elasticsearch会清空其所有的数据。

执⾏如下命令初始化:


cd /tmp

wget http://us.centos.bz/cdnfly/int_es.sh -O int_es.sh;

chmod +x int_es.sh; ./int_es.sh /home/es;


10、
如何重置主控密码

执⾏如下命令，重置⽤户名为admin的密码为cdnfly，如果不是admin⽤户，可以修改命令中的admin成其它的


eval  `grep MYSQL_PASS /opt/cdnfly/master/conf/config.py`;

eval  `grep MYSQL_IP /opt/cdnfly/master/conf/config.py`;

eval  `grep MYSQL_PORT /opt/cdnfly/master/conf/config.py`;

eval  `grep MYSQL_DB /opt/cdnfly/master/conf/config.py`;

eval  `grep MYSQL_USER /opt/cdnfly/master/conf/config.py`;

mysql -h$MYSQL_IP -u$MYSQL_USER -p$MYSQL_PASS -P$MYSQL_PORT  $MYSQL_DB  -e 'update user set password="$2b$12$UV5ttpNQizMfO.tiBk9ereZ53hDBW0.kak3qa/GRP6aVBfNMB1NsK" where name="admin" ';







