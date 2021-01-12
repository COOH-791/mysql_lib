# MySQL 自动化部署脚本

#### 一、环境说明

* 操作系统：CentOS
* 数据库版本：MySQL 5.7/8.0
* 参数：buffer pool 会根据系统内存指定、默认双一、GTID、SlowLog
* 脚本默认安装路径：/usr/local/mysql
* 脚本默认数据路径：/data/mysql*（根据安装包版本适应 比如 5.7 mysql57）

#### 二、使用方法

1. 服务器上创建一个 /myinstall 临时文件夹

   ```
   mkdir /myinstall
   ```

2. 将本地的 MySQL 安装包 和 mysql_install.py 上传到服务器：

   ```
   [root@172-16-104-56 test01]# ll
   总用量 645732
   -rw-r--r--. 1 root root 661214270 1月  11 13:59 mysql-5.7.32-linux-glibc2.12-x86_64.tar.gz
   -rw-r--r--. 1 root root     10727 1月  12 18:34 mysql_install.py
   ```

3. 运行 mysql_install.py 即可执行

   ```sh
   python mysql_install.py mysql-5.7.32-linux-glibc2.12-x86_64.tar.gz
   ```

   [![sYlsIO.md.png](https://s3.ax1x.com/2021/01/12/sYlsIO.md.png)](https://imgchr.com/i/sYlsIO)

4. 脚本执行完成后会将登入数据库的命令打印出来，直接登入即可

   [![sYlUz9.md.png](https://s3.ax1x.com/2021/01/12/sYlUz9.md.png)](https://imgchr.com/i/sYlUz9)

5. 接下来修改密码即可：

   ```
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'YouPassword';
   ```

6. 将 MySQL 添加到 .bash_profile 中：

   ```
   vi /root/.bash_profile
   -- 添加到文件中
   PATH=$PATH:$HOME/bin:/usr/local/mysql/bin
   -- 保存后 source
   source /root/.bash_profile
   ```

7. 验证：

   ```
   [root@db01 /]# mysql
   mysql                       mysql_embedded
   mysqladmin                  mysqlimport
   mysqlbinlog                 mysql_install_db
   mysqlcheck                  mysql_plugin
   mysql_client_test_embedded  mysqlpump
   mysql_config                mysql_secure_installation
   mysql_config_editor         mysqlshow
   mysqld                      mysqlslap
   mysqld-debug                mysql_ssl_rsa_setup
   mysqld_multi                mysqltest_embedded
   mysqld_safe                 mysql_tzinfo_to_sql
   mysqldump                   mysql_upgrade
   mysqldumpslow               mysqlxtest
   [root@db01 /]#
   ```

   

