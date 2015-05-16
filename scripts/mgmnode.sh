#!/bin/sh

#####################################
#Management Node
#####################################

export DEBIAN_FRONTEND=noninteractive
rm -rf /var/lib/mysql
rm -rf /etc/mysql/
rm -f /etc/mysql/my.cnf

apt-get -y remove mysql*
apt-get -y --purge remove
apt-get -y autoremove
dpkg --get-selections | grep mysql
aptitude -y purge $(dpkg --get-selections | grep deinstall | sed s/deinstall//)


cd /var/tmp/

wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.4/mysql-cluster-gpl-7.4.6-linux-glibc2.5-x86_64.tar.gz

tar -xvzf mysql-cluster-gpl-7.4.6-linux-glibc2.5-x86_64.tar.gz

cp /var/tmp/mysql-cluster-gpl-7.4.6-linux-glibc2.5-x86_64/bin/ndb_mgm* /usr/local/bin/

chmod +x /usr/local/bin/ndb_mgm*

mkdir -p /var/lib/mysql-cluster/

#rm -rf /var/tmp/*