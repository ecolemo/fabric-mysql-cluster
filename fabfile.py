# -*- coding: utf-8 -*-
from fabric.context_managers import lcd
from fabric.contrib.files import upload_template
from fabric.decorators import roles
from fabric.operations import put, run
from fabric.state import env
from fabric.tasks import execute

env.user = 'root'
env.roledefs = {
    'mgm_nodes': ['10.211.55.33'],
    'data_nodes': ['10.211.55.34'],
    'sql_nodes': ['10.211.55.35'],
}

def create_conf_files():
    configurations = []
    # configuation for config.ini
    configuration_1 = {}
    configuration_1['file'] = 'config.ini'
    configuration_1['replacements'] = {
        '<num_of_replicas>': str(len(env.roledefs['data_nodes'])),
        '<mgm_node>': '',
        '<data_node>': '',
        '<sql_node>': ''
    }

    for host in env.roledefs['mgm_nodes']:
        configuration_1['replacements']['<mgm_node>'] = "[ndb_mgmd]\nhostname=%s\ndatadir=/var/lib/mysql-cluster\n" % host

    for host in env.roledefs['data_nodes']:
        configuration_1['replacements']['<data_node>'] = "[ndbd]\nhostname=%s\ndatadir=/usr/local/mysql/data\n" % host

    for host in env.roledefs['sql_nodes']:
        configuration_1['replacements']['<sql_node>'] = "[mysqld]\nhostname=%s\n" % host

    configurations.append(configuration_1)

    # configuration for my.cnf
    configuration_2 = {}
    configuration_2['file'] = 'my.cnf'
    configuration_2['replacements'] = {'<mgm_node_ip>': env.roledefs['mgm_nodes'][0]}
    configurations.append(configuration_2)

    for configuration in configurations:
        infile = open('confs/base/'+configuration['file'])
        outfile = open('confs/'+configuration['file'], 'w')

        for line in infile:
            for src, target in configuration['replacements'].iteritems():
                line = line.replace(src, target)
            outfile.write(line)

        infile.close()
        outfile.close()


@roles("mgm_nodes")
def setup_mgm_nodes():
    put('scripts/mgmnode.sh', '/var/tmp')
    run('chmod +x /var/tmp/mgmnode.sh')
    run('/var/tmp/mgmnode.sh')
    put('confs/config.ini', '/var/lib/mysql-cluster')

@roles("data_nodes")
def setup_data_nodes():
    put('confs/my.cnf', '/etc')
    put('scripts/datanode.sh', '/var/tmp')
    run('chmod +x /var/tmp/datanode.sh')
    run('/var/tmp/datanode.sh')


@roles("sql_nodes")
def setup_sql_nodes():
    put('confs/my.cnf', '/etc')
    put('scripts/sqlnode.sh', '/var/tmp')
    run('chmod +x /var/tmp/sqlnode.sh')
    run('/var/tmp/sqlnode.sh')


@roles("mgm_nodes")
def start_mgm_nodes():
    run('/usr/local/bin/ndb_mgmd -f /var/lib/mysql-cluster/config.ini --configdir=/var/lib/mysql-cluster')

@roles("data_nodes")
def start_data_nodes():
    run('ndbd')

@roles("sql_nodes")
def start_sql_nodes():
    run('service mysql.server start')

def setup_mysql_cluster():
    create_conf_files()
    execute(setup_mgm_nodes)
    execute(setup_data_nodes)
    execute(setup_sql_nodes)


def start_mysql_cluster():
    execute(start_mgm_nodes)
    execute(start_data_nodes)
    execute(start_sql_nodes)
