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

### Sass

For the theme to work you need to install `sass` and have it available in your path.

### Python

Install `poetry`

`pip install --upgrade poetry`

Create environment and install requirements

`poetry install`

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

`python .\src\manage.py dumpdata --natural-foreign --exclude=auth --exclude=contenttypes --exclude=admin --exclude=sessions --exclude=django_q --exclude=crew.CrewMember --exclude=crew.TeamMember --exclude=crm --exclude=exhibitors.ExhibitorAttendance --exclude=exhibitors.ExhibitorAsset --exclude=exhibitors.Exhibitor > .\examples\example_data.json`

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

## dumpdata / loaddata

Full dump:`python -Xutf8 ./src/manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e admin -e auth.Permission -e django_q -e sessions --indent 2 -o ./dumpall.json`

Disable _all_ signals in models for reimport as thay can interfere with loaddata, e.g. comment them out.

Signals are used in

- crm user_profile

import: `python -Xutf8 ./src/manage.py loaddata ./dumpall.json`

Reenable signals.

### Export used default groups

To export the default groups use the following command:

`python -Xutf8 .\src\manage.py dumpdata --natural-foreign --natural-primary --indent 2 contenttypes.contenttype auth.permission auth.group -o .\src\rockon\fixtures\base_groups.json`

## Docs

### Bootstrap

<https://getbootstrap.com/docs/5.3/getting-started/introduction/>

### Django

<https://docs.djangoproject.com/en/5.0/>

### Django Q2

<https://django-q2.readthedocs.io/en/master/index.html>

### Chart.js

<https://www.chartjs.org/docs/latest/>

### Luxon

<https://moment.github.io/luxon/>

### Wavesurfer

<https://wavesurfer.xyz/>

### Simple-lightbox

<https://github.com/andreknieriem/simplelightbox>
