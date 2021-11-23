# Setting up a new league
From the admin console, create a new league.
espn_id: get from url when viewing your team on espn
espn_s2 & swid: For private league you will need to get your swid and espn_s2. You can find these
two values after logging into your espn fantasy football account on espn's website. (Chrome Browser)
Right click anywhere on the website and click inspect option. From there click Application on the
top bar. On the left under Storage section click Cookies then http://fantasy.espn.com. From there
you should be able to find your swid and espn_s2 variables and values.

### To run the server
```
source .venv/bin/activate
python manage.py runserver
```

### After making a database schema change, create a migration, then migrate
```
python manage.py makemigrations [schema name]
python manage.py migrate
```
