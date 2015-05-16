#!/bin/sh

####################################
#             SQL Node             #
####################################


export DEBIAN_FRONTEND=noninteractive
apt-get -y update
rm -rf /var/lib/mysql
rm -rf /etc/mysql/
apt-get -y remove mysql*
apt-get -y --purge remove
apt-get -y autoremove
dpkg --get-selections | grep mysql
aptitude -y purge $(dpkg --get-selections | grep deinstall | sed s/deinstall//)

sudo apt-get -y install libaio1 libaio-dev

groupadd mysql
useradd -g mysql mysql


cd /var/tmp/

wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.4/mysql-cluster-gpl-7.4.6-linux-glibc2.5-x86_64.tar.gz

tar -C /usr/local -zxvf mysql-cluster-gpl-7.4.6-linux-glibc2.5-x86_64.tar.gz

ln -s /usr/local/mysql-cluster-gpl-7.4.6-linux-glibc2.5-x86_64 /usr/local/mysql

cat > /etc/apparmor.d/usr.sbin.mysqld << EOF

/usr/local/mysql/data/ r,
/usr/local/mysql/data/** rwk,

EOF

service apparmor reload

/usr/local/mysql/scripts/mysql_install_db --user=mysql --basedir=/usr/local/mysql --datadir=/usr/local/mysql/data --defaults-file=/etc/my.cnf

cp /usr/local/mysql/bin/mysqld_safe /usr/bin/

cp /usr/local/mysql/bin/mysql /usr/bin/

cd /usr/local/mysql

chown -R root .
chown -R mysql data
chgrp -R mysql .

cp /usr/local/mysql/support-files/mysql.server /etc/init.d

#need to set the following variables in file /etc/init.d/mysql.server to
#basedir=/usr/local/mysql/
#datadir=/usr/local/mysql/data/

sed -i 's/^basedir=$/basedir=\/usr\/local\/mysql/g' /etc/init.d/mysql.server
sed -i 's/^datadir=$/datadir=\/usr\/local\/mysql\/data/g' /etc/init.d/mysql.server


cd /etc/init.d/

update-rc.d mysql.server defaults

#rm -rf /var/tmp/*
