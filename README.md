# django-settings-custom
A Django interactive command for configuration file generation.

## Getting It

```
pip install django-settings-custom
```

## Installing It

To enable `django_settings_custom` in your project you need to add it to `INSTALLED_APPS` in your projects
`settings.py` file:
```
INSTALLED_APPS = (
    ...
    'django_settings_custom',
    ...
)
```

## Using It

Create a template for your target conf.ini like
```ini
[DATABASE]
NAME = { USER_VALUE }
HOST = { USER_VALUE }
PORT = { USER_VALUE }

[DATABASE_CREDENTIALS]
USER = { USER_VALUE }
PASSWORD = { ENCRYPTED_USER_VALUE }

[DJANGO]
KEY = { DJANGO_SECRET_KEY }

# A constant field
[LDAP]
LDAPGRP = 'ldaps://myldap'
```

Add `settings.py` file
```python
SETTINGS_TEMPLATE_FILE = 'PATH_TO_YOUR_TEMPLATE_CONFIGURATION_FILE'
SETTINGS_FILE_PATH = 'TARGET_FOR_CONFIGURATION_FILE'
```

Launch in command line
```
python manage.py generate_settings
```

## Results
The command ask user to fill missing values from template:
```
[user@localhost a_project]$ ./manage.py generate_conf
** Configuration file generation: **

** Configuration file generation: **
Do you want to generate the secret key for Django ? (Y/n) : y
Django secret key generated

** Enter values for configuration file content **

Value for [DATABASE] NAME: database_name
Value for [DATABASE] HOST: database_host
Value for [DATABASE] PORT: 8000
Value for [DATABASE_CREDENTIALS] USER: an_ident
Value for [DATABASE_CREDENTIALS] PASSWORD (will be encrypted): a_password

Writing file at /home/user/a_project/conf.ini:
Configuration file successfully generated.
[user@localhost a_project]$ 
```

It generates the file /home/user/a_project/conf.ini:
```ini
[DATABASE]
NAME = database_name
HOST = database_host
PORT = 8000

[DATABASE_CREDENTIALS]
USER = an_ident
PASSWORD = JbAwLj5Zwz8lMrvcUZq5sP/v6eaUFY5E7U8Fmg63vxI=

# A constant field
[LDAP]
LDAPGRP = 'ldaps://monldap'

[DJANGO]
KEY = w)r13ne4=id9_8xdojir)3)%%5m3r$co#jwj_)4d*_%%!0+f#sro
```
