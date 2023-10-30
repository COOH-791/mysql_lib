# -*- coding: utf-8 -*-
import os
import sys
import math
import time
import socket
import random
import argparse
import subprocess
from collections import OrderedDict

__author__ = 'wenruo@dtstack.com'


class MySQLInstall(object):
    def __init__(self, mysql_zip_name, tmp_base_path, tmp_data_path, tmp_port):
        # Initialize variable
        self.base_path = tmp_base_path
        self.data_base_path = tmp_data_path
        self.mysql_port = tmp_port
        self.mysql_zip = mysql_zip_name

        # Initialization method
        self.start_instructions()

        self.data_base, self.db_version = self.verify_package(self.data_base_path)

    def install_run(self):
        """
        Program entrance.
        :return:
        """
        print('loading....')
        time.sleep(1)
        self.check_sys_env()
        self.create_sys_mysql_user()
        self.unzip()
        self.create_data_base()
        self.authorization_set()
        self.write_conf()
        self.init_mysql()
        self.start_mysql()

    def start_mysql(self):
        """
        Start the database.
        :return:
        """
        print('Starting MySQL...')
        dos_start_mysql = '{}/mysql/bin/mysqld_safe --defaults-file=/etc/my.cnf --user=mysql &'.format(self.base_path)
        os.system(dos_start_mysql)
        print('\n')
        if self.check_mysql():
            print('Successful! Please enter to exit the program.')
            self.get_password()
        else:
            print('Error: Database startup failure.')
            sys.exit(0)

    def get_password(self):
        """
        Get the password from the error log.
        :return:
        """
        dos_grep_password = 'grep "password" {}/logs/error.log'.format(self.data_base)
        response_dos = self.exec_dos_command(dos_grep_password)
        temp_password = response_dos[response_dos.rfind(' ') + 1:]
        dos_login_mysql = "{}/mysql/bin/mysql -uroot -p'{}' -S {}/data/mysql.sock".format(self.base_path,
                                                                                          temp_password, self.data_base)
        print('=' * 100)
        print(dos_login_mysql.replace('\n', '').replace('\r', ''))
        print('=' * 100)

    def check_mysql(self):
        """
        Verify that MySQL started successfully.
        :return:
        """
        response_dos = self.exec_dos_command('ps -ef | grep mysql')
        if response_dos.find('mysqld'):
            return True
        else:
            return False

    def init_mysql(self):
        """
        Initialize the MySQL.
        :return:
        """
        print('Initializing MySQL...')
        dos_init_mysql = '{}/mysql/bin/mysqld --initialize --user=mysql --basedir={}/mysql/ --datadir={}/data'.format(
            self.base_path, self.base_path, self.data_base)

        self.exec_dos_command(dos_init_mysql)

        if len(os.listdir(self.data_base + '/data')) >= 6:
            print('Successful!')
        else:
            print('=' * 100)
            print('Error: An exception occurred during initialization.')
            print('=' * 100)
            sys.exit(0)

    def authorization_set(self):
        """
        Directory authorization.
        :return:
        """
        print('Permission setting in progress...')
        dos_auth_base_set = 'chown -R mysql:mysql {}/mysql'.format(self.base_path)
        dos_auth_data_set = 'chown -R mysql:mysql {}'.format(self.data_base)
        self.exec_dos_command(dos_auth_base_set)
        self.exec_dos_command(dos_auth_data_set)

    def create_sys_mysql_user(self):
        """
        Create system users or user groups.
        :return:
        """
        print('Checking system permissions...')
        # if os.popen('echo $LANG $LANGUAGE').read() != 'zh_CN.UTF-8':
        #     print('[Warning]: A system supported language other than zh_CN.UTF-8 may fail.')

        dos_group = self.exec_dos_ask('cat /etc/group | grep mysql')
        dos_user = self.exec_dos_ask('cat /etc/passwd | grep mysql')

        if dos_group == '':
            self.exec_dos_command('groupadd mysql')
            print('User group creation successful!')
        else:
            print('50% System Permission Detection!')

        if dos_user == '':
            self.exec_dos_command('useradd -r -g mysql -s /bin/false mysql')
            print('User created successfully')
        else:
            print('100% System Permission Detection!')

    def verify_package(self, data_path):
        """
        Verify installation md5 package.
        :param data_path:
        :return:
        """
        print('Validating the installation package...')
        dos_md5 = 'md5sum ' + self.mysql_zip
        md5_response = self.exec_dos_command(dos_md5)

        if md5_response == '':
            print(md5_response)
            print('Error: Please specify the correct installation package.')
            sys.exit(0)
        else:
            print(md5_response)

        sp_name = self.mysql_zip.split('-')[1]
        db_version = int(sp_name[0:1] + sp_name[2:3])

        return (os.path.join(data_path, 'mysql_') + str(db_version)), str(db_version)

    def check_sys_env(self):
        """
        Check if a path meets the requirements.
        :return:
        """
        if os.path.isdir(self.data_base):
            print('Error: The set data directory already exists.{0}'.format(self.data_base))
            sys.exit(0)

        if os.path.isdir(os.path.join(self.base_path, 'mysql')):
            print('Error: The base directory already exists.{0}'.format(os.path.join(self.base_path, 'mysql')))
            sys.exit(0)

    def unzip(self):
        """
        unzip mysql
        :return:
        """
        print('Unpacking the installation package...')
        dos_comm_unzip = 'tar -xvf {} -C {}'.format(self.mysql_zip, self.base_path)
        self.exec_dos_command(dos_comm_unzip)
        temp_path = os.path.join(self.base_path, self.mysql_zip)
        now_base_path = temp_path[: temp_path.find('tar') - 1]
        dos_comm_mv = 'mv {} {}'.format(now_base_path, os.path.join(self.base_path, 'mysql'))
        self.exec_dos_command(dos_comm_mv)

    def write_conf(self):
        """
        Write configuration file.
        :return:
        """
        print('Writing my.conf...')

        client_conf_dict = {
            'port': self.mysql_port,
            'socket': self.data_base + '/data/mysql.sock'
        }
        mysql_conf_dict = {
            'port': self.mysql_port,
            'socket': self.data_base + '/data/mysql.sock',
            'prompt': '"\u@mysql \R:\m:\s [\d]>"'
        }

        with open('/etc/my.cnf', 'w') as r1:
            r1.truncate()
            # write client conf
            r1.write('[client]\n')
            for x, y in client_conf_dict.items():
                temp_write = x + ' = ' + str(y) + '\n'
                r1.write(temp_write)
                r1.write('\n')

            # write mysql conf
            r1.write('[mysql]\n')
            for x, y in mysql_conf_dict.items():
                temp_write = x + ' = ' + str(y) + '\n'
                r1.write(temp_write)
                r1.write('\n')

            # write mysqld conf
            r1.write('[mysqld]\n')
            for x, y in self.set_mysqld_conf().items():
                temp_write = x + ' = ' + str(y) + '\n'
                r1.write(temp_write)
                r1.write('\n')

    def create_data_base(self):
        """
        Creating a data path.
        :return:
        """
        print('Creating a data directory...')
        dos_create_data_path = 'mkdir -p %s/{data,logs,tmp,run}' % self.data_base
        dos_create_error_log = 'touch {}'.format(self.data_base + '/logs/error.log')
        self.exec_dos_command(dos_create_data_path)
        self.exec_dos_command(dos_create_error_log)

    def get_server_id(self):
        """
        server_id = ip[-3:] + port
        :return:
        """
        ip = socket.gethostbyname(socket.gethostname())
        return str(ip.split('.')[-1]) + str(self.mysql_port)

    def get_system_mem_size(self):
        """
        Obtain the memory size of the operating system
        :return:
        """
        dos_response = self.exec_dos_command('cat /proc/meminfo | grep MemTotal')
        size = float(dos_response[dos_response.find(':') + 1:dos_response.find('kB')])
        system_mem_size = int(round(size / math.pow(1024, 2), 0))

        return system_mem_size

    def get_innodb_settings(self):
        """
        Calculate innodb settings based on server memory.
        :return:
        """
        system_mem = self.get_system_mem_size()
        innodb_buffer_size = '128M'
        innodb_instances = 2

        innodb_log_file_size = '48M'
        innodb_log_files_in_group = 2

        if 1 < system_mem <= 4:
            innodb_buffer_size = str(int(system_mem / 2)) + 'G'
            innodb_log_file_size = '128M'
        elif 4 < system_mem <= 8:
            innodb_buffer_size = str(int(system_mem * 0.75)) + 'G'
            innodb_log_file_size = '512M'
        elif 8 < system_mem <= 16:
            innodb_buffer_size = str(int(system_mem * 0.75)) + 'G'
            innodb_log_file_size = '1024M'
        elif 16 < system_mem:
            innodb_buffer_size = str(int(system_mem * 0.75)) + 'G'
            innodb_log_file_size = '2048M'
            innodb_instances += 2

        print('innodb_buffer_pool_size = {0}'.format(innodb_buffer_size))
        print('innodb_log_file_size = {0}'.format(innodb_log_file_size))

        settings_dict = {
            'innodb_buffer_pool_size': innodb_buffer_size,
            'innodb_buffer_pool_instances': innodb_instances,
            'innodb_log_file_size': innodb_log_file_size,
            'innodb_log_files_in_group': innodb_log_files_in_group
        }

        return settings_dict

    def set_mysqld_conf(self):
        """
        Set up the configuration file associated with mysqld
        :return: mysqld_conf_odict obj
        """
        mysqld_conf_odict = OrderedDict()

        # base
        mysqld_conf_odict['user'] = 'mysql'
        mysqld_conf_odict['port'] = self.mysql_port
        mysqld_conf_odict['basedir'] = os.path.join(self.base_path, 'mysql')
        mysqld_conf_odict['datadir'] = self.data_base + '/data'
        mysqld_conf_odict['socket'] = self.data_base + '/data/mysql.sock'
        mysqld_conf_odict['tmpdir'] = self.data_base + '/tmp'

        # server_id
        mysqld_conf_odict['server_id'] = self.get_server_id()

        # binlog
        mysqld_conf_odict['log-bin'] = self.data_base + '/logs/mysql-bin'
        mysqld_conf_odict['binlog_format'] = 'ROW'
        mysqld_conf_odict['sync_binlog'] = 1
        mysqld_conf_odict['binlog_cache_size'] = '4M'
        mysqld_conf_odict['max_binlog_cache_size'] = '4G'
        mysqld_conf_odict['max_binlog_size'] = '500M'
        mysqld_conf_odict['master_info_repository'] = 'TABLE'
        mysqld_conf_odict['relay_log_info_repository'] = 'TABLE'

        # relay log
        mysqld_conf_odict['relay_log'] = self.data_base + '/logs/mysql-relay'

        if self.db_version == '57':
            mysqld_conf_odict['expire_logs_days'] = 10
            # innodb uodo logging
            mysqld_conf_odict['innodb_undo_tablespaces'] = 2
            mysqld_conf_odict['innodb_undo_log_truncate'] = 1

        elif self.db_version == '80':
            mysqld_conf_odict['binlog_expire_logs_seconds'] = 864000

        # GTID
        mysqld_conf_odict['gtid_mode'] = 'on'
        mysqld_conf_odict['enforce_gtid_consistency'] = 'on'

        # level
        mysqld_conf_odict['transaction_isolation'] = 'READ-COMMITTED'

        # innodb
        innodb_settings = self.get_innodb_settings()
        mysqld_conf_odict['innodb_buffer_pool_size'] = innodb_settings.get('innodb_buffer_pool_size')
        mysqld_conf_odict['innodb_buffer_pool_instances'] = innodb_settings.get('innodb_buffer_pool_instances')
        mysqld_conf_odict['innodb_flush_log_at_trx_commit'] = 1
        mysqld_conf_odict['innodb_data_file_path'] = 'ibdata1:500M:autoextend'
        mysqld_conf_odict['innodb_temp_data_file_path'] = 'ibtmp1:200M:autoextend'
        mysqld_conf_odict['innodb_sort_buffer_size'] = 1048576
        mysqld_conf_odict['innodb_doublewrite'] = 1

        # innodb redo logging
        mysqld_conf_odict['innodb_log_file_size'] = innodb_settings.get('innodb_log_file_size')
        mysqld_conf_odict['innodb_log_files_in_group'] = innodb_settings.get('innodb_log_files_in_group')
        mysqld_conf_odict['innodb_log_buffer_size'] = '32M'
        mysqld_conf_odict['innodb_flush_neighbors'] = 0
        mysqld_conf_odict['innodb_io_capacity'] = 1000

        # error_log
        mysqld_conf_odict['log-error'] = self.data_base + '/logs/error.log'

        # Slow log
        mysqld_conf_odict['slow_query_log'] = 1
        mysqld_conf_odict['slow_query_log_file'] = self.data_base + '/logs/slow.log'
        mysqld_conf_odict['long_query_time'] = 1
        # Whether to record full table scan SQL
        # mysqld_conf_odict['log_queries_not_using_indexes'] = 0

        # connections
        mysqld_conf_odict['max_connections'] = 2000

        # other
        mysqld_conf_odict['pid-file'] = 'mysql.pid'
        mysqld_conf_odict['character-set-server'] = 'utf8mb4'
        mysqld_conf_odict['collation_server'] = 'utf8mb4_general_ci'
        mysqld_conf_odict['autocommit'] = 1
        mysqld_conf_odict['explicit_defaults_for_timestamp'] = 1
        mysqld_conf_odict['log_timestamps'] = 'SYSTEM'
        # password plug-in
        mysqld_conf_odict['default_authentication_plugin'] = 'mysql_native_password'

        # How do I need to add a custom configuration in the following code format
        # mysqld_conf_odict[''] = 'xxx'

        return mysqld_conf_odict

    @staticmethod
    def exec_dos_ask(command):
        """
        Execute system commands.
        """
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        content = process.stdout.read()
        process.communicate()
        if process.returncode != 0:
            return ''
        else:
            return content

    @staticmethod
    def exec_dos_command(command):
        """
        Execute system commands.
        """
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        content = process.stdout.read()
        process.communicate()
        if process.returncode != 0:
            print('Program Error: {0}'.format(command))
            print(content)
            sys.exit(0)
        else:
            return content.decode()

    @staticmethod
    def start_instructions():
        mysql_str = """
            __  __       ____   ___  _       _           _        _ _
           |  \/  |_   _/ ___| / _ \| |     (_)_ __  ___| |_ __ _| | |
           | |\/| | | | \___ \| | | | |     | | '_ \/ __| __/ _` | | |
           | |  | | |_| |___) | |_| | |___  | | | | \__ \ || (_| | | |
           |_|  |_|\__, |____/ \__\_\_____| |_|_| |_|___/\__\__,_|_|_|
                   |___/
               """
        print(mysql_str)
        time.sleep(1.5)

    @staticmethod
    def get_random_password():
        chars = "012345#6789ab#!c%def#$ghijk*lmnopqrstuvwxyz#ABCDEF$GHIJK%LMNOP#*QRSTUVWXYZ"
        pwd_str = ''.join(random.choice(chars) for i in range(16))
        passwd = pwd_str[0:12]
        mysql_dos = "Random password: {0}".format(passwd)
        return mysql_dos


if __name__ == '__main__':
    # https://dev.mysql.com/downloads/mysql/
    # # yum search libaio

    parser = argparse.ArgumentParser(description=MySQLInstall.get_random_password())
    parser.add_argument('--path', '-p', type=str, help='MySQL binary installation package path.', default=None)
    parser.add_argument('--port', type=int, help='Install the port specified by MySQL, Default: 3306', default=3306)
    parser.add_argument('--datadir', type=str, help='Data directory. Default to /data', default='/data')
    parser.add_argument('--basedir', type=str, help='Base directory. Default to /usr/local', default='/usr/local')
    args = parser.parse_args()

    if not args.path:
        parser.print_help()
        sys.exit(0)

    install_obj = MySQLInstall(mysql_zip_name=args.path,
                               tmp_base_path=args.basedir,
                               tmp_data_path=args.datadir,
                               tmp_port=args.port)

    install_obj.install_run()
