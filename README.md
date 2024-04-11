# Ubiquote

:construction: This project is under construction :construction:

Ubiquote is a personnal project about short texts like books quotes, movies and series quotes, proverbs...

My intend is to have a database + API and use it as a sandbox to tests several way to present, mix and explore these short texts.
Also plan to add some AI tools to generate cool stuffs.

## Overview

Some metrics :
- More than 10 000 shorts texts
- Almost 2000 authors

Features :
- Multilanguage interface (english and french right now)
- Multilinguage contents
- Rest API
- User Management
- Collections of short text

Full Stack :
- Django for the framework
- Htmx for enhancing the web interface
- PostgreSQL for the database
- FastAPI or Django REST Framework for the API 

## Informations for installation

### gettext to manage translations

If you want to create your own message for multilanguage, you must install gettext on your machine.
This is only needed for people who either want to extract message IDs or compile message files (.po). Translation work itself involves editing existing files of this type, but if you want to create your own message files, or want to test or compile a changed message file, download a precompiled binary installer.

For Mac OS :
`brew install gettext`

For Windows
You must install a binary file on your system. Choose the appropriate one [here](https://mlocati.github.io/articles/gettext-iconv-windows.html)

More informations on translation on the [Django Documentation](https://docs.djangoproject.com/fr/4.2/topics/i18n/translation/)

Highly recommand this [Yourube video](https://www.youtube.com/watch?v=z_p8WxFGV5A)

### activate extentions in Postgrsql (15.2 or highter)

You must add 'django.contrib.postgres'  in INSTALLED_APPS of your settings.py

In PGadmin, you can add extentions for your database that enable some capality such as trigram or unaccent query sets.
Click on "Extentions" in your database, then click and choose "Create / Extentions..."
You must select "pg_trgm" to add this capacity.
You also have to add the extention "unaccent" and "pg_vector"

Or you can do it by commande line :

1) Log into postgres
psql -U <DB_USERNAME>

2) After you are connected, switch to the DB you want to install the extension for:
\c <DB_NAME>

3) Then install the extension as answered previously:
CREATE EXTENSION pg_trgm;

pg_vector is not installed by defaut by the postgresql used so it has to be installed.
