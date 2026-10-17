# Test run output

Commands run from the project directory with Django 5.2.18 installed.

## `python manage.py check`

```text
System check identified no issues (0 silenced).
```

## `python manage.py makemigrations --check --dry-run`

```text
No changes detected
```

## `python manage.py test boxes`

```text
Creating test database for alias 'default'...
.................
----------------------------------------------------------------------
Ran 17 tests in 0.101s

OK
Destroying test database for alias 'default'...
Found 17 test(s).
System check identified no issues (0 silenced).
```
