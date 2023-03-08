# rock.on

Hyper customized Rocktreff data entry and lists thingamajig (Django)

## ChatGPT über rockon

Eine Festivalverwaltung könnte Folgendes beinhalten:

- Eine Datenbank mit Informationen zu den Künstlern, die beim Festival auftreten, einschließlich ihres Namens, ihrer Musikrichtung und ihres Managementteams.
- Eine Funktion zur Verwaltung von Tickets und Eintrittsbändchen, einschließlich der Möglichkeit, Tickets online zu verkaufen und den Verkauf von Eintrittsbändchen an der Tür zu verfolgen.
- Eine Funktion zur Verwaltung von Sponsoren und Ausstellern, einschließlich der Möglichkeit, Sponsorenverträge zu verwalten und Ausstellerplätze zu verwalten.
- Eine Funktion zur Verwaltung von Dienstleistern wie Catering-Unternehmen, Sicherheitsfirmen und anderen Dienstleistern, die für das Festival benötigt werden.
- Eine Funktion zur Verwaltung von Transport und Unterkunft für Künstler und Festivalmitarbeiter.
- Eine Funktion zur Verwaltung von Logistik und Infrastruktur, einschließlich der Verwaltung von Zelten, Ständen und anderen Einrichtungen, die für das Festival benötigt werden.
- Eine Funktion zur Verwaltung von Marketing- und PR-Aktivitäten, einschließlich der Verwaltung von Social-Media-Konten und der Erstellung von Pressemitteilungen.
- Eine Funktion zur Verwaltung von Finanzen und Buchhaltung, einschließlich der Verwaltung von Einnahmen und Ausgaben und der Erstellung von Finanzberichten.
- Eine Funktion zur Verwaltung von Sicherheits- und Notfallmaßnahmen, einschließlich der Verwaltung von Sicherheitsplänen und der Koordination von Notfallprozeduren.
- Eine Funktion zur Verwaltung von Freiwilligen und temporären Mitarbeitern, einschließlich der Verwaltung von Anwendungen, Einsätzen und Schulungen.

## Setup

### Python

Install `pipenv`

`pip install --upgrade pipenv`

Create environment and install requirements

`pipenv sync --dev`

### Precommit

Install `pre-commit` hooks to git: `pre-commit install`

Create `pre-commit` environment and install dependencies: `pre-commit`

If you want to run `pre-commit` before commits: `pre-commit run --all-files`

### Prepare environment

Copy `.env.example` to `.env` and adjust acording to your local enivronment.

### Database

Run `docker compose up -d postgres` to start Postgres, or use the `.env` file to configure the use of the SQLite3 backend.

## Debug mailserver

Run `docker compose up -d mailhog` to start the debug mail server.

## Dev Django

### Collect statics

This needs to be run once and everything assets are added to `src/static`: `python src/manage.py collectstatic`

### Run migrations

`python src/manage.py migrate`

### Load sample data

`python src/manage.py loaddata examples/example_data.json`

The sample data does not contain a user, you still need to create a super user.

### Update sample data

Use this to update the sample data:

`python .\src\manage.py dumpdata --exclude=auth --exclude=contenttypes --exclude=admin --exclude=sessions --exclude=django_q --exclude=crew.CrewMember --exclude=crew.TeamMember --exclude=crm --exclude=exhibitors.ExhibitorAttendance --exclude=exhibitors.ExhibitorAsset --exclude=exhibitors.Exhibitor > .\examples\example_data.json`

Certain database entries must be excluded, the file must be utf8 encoded.

### Create super user

`python src/manage.py createsuperuser`

### Run server

Either use the provied VScode launch configurations or run `python src/manage.py runserver`

Start the async queue cluster with `python src/manage.py qcluster`

## Mail templates

Source of template: <https://github.com/leemunroe/responsive-html-email-template>

Copy the `base_template.html` and modify to your liking, then use <https://htmlemail.io/inline/> to inline the CSS, save result (HTML+inlined CSS) as mail template.

## Docker

For easy setup there is a compose file included for running the app without a local tool chain, setup your environment as follows:

```bash
docker compose -f docker-compose.deploy.yml up -d app
docker compose -f docker-compose.deploy.yml exec -it app ./manage.py loaddata examples/example_data.json
```

## Docs

### Bootstrap

<https://getbootstrap.com/docs/5.3/getting-started/introduction/>

### Django

<https://docs.djangoproject.com/en/4.1/>

### Django Q2

<https://django-q2.readthedocs.io/en/master/index.html>
