SETUP DATABASE
======
MYSQL database must be turned into READ COMMITTED isolation level:
command:

SET GLOBAL TRANSACTION ISOLATION LEVEL READ COMMITTED;

CREATE DATABASE freeschool CHARACTER SET utf8 COLLATE utf8_unicode_ci;
GRANT ALL PRIVILEGES ON freeschool.* TO admin@localhost IDENTIFIED BY 'freeschool';
FLUSH PRIVILEGES;
GRANT ALL ON test_freeschool.* TO admin@localhost;
QUIT;

python manage schemamigration app --initial
python manage schemamigration school --initial
python manage schemamigration sms --initial
python manage syncdb
python manage migrate
