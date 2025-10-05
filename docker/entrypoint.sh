#!/bin/bash
set -e

export HOME=/app
export NUM_WORKERS=$((1 * $(nproc --all)))

cd $HOME

rsync -a --delete /app/dist/. /static_files

if [ "$DJANGO_MIGRATE" == "yes" ] || [ "$STARTMODE" == "init" ]; then
    /app/.venv/bin/python /app/manage.py migrate --noinput
fi

if [ -n "$DJANGO_LOAD_FIXTURE" ]; then
    /app/.venv/bin/python $HOME/manage.py loaddata "$DJANGO_LOAD_FIXTURE"
    exit $?
fi

if [ "$1" == "version" ]; then
    /app/.venv/bin/python $HOME/manage.py appversion
    exit $?
fi

if [ "$1" == "app" ] || [ "$STARTMODE" == "app" ]; then
    # start gunicorn (might be called indirectly via supervisor when started with 'all')
    /app/.venv/bin/python -m gunicorn rockon.wsgi:application \
        --name rockon \
        --workers $NUM_WORKERS \
        --worker-tmp-dir /dev/shm \
        --max-requests 1200 \
        --max-requests-jitter 50 \
        --log-level=info \
        --access-logfile=/dev/null \
        --error-logfile=- \
        --bind=0.0.0.0:8000 \
        --bind=unix:/run/rockon/app.sock
      exit $?
fi

if [ "$1" == "qcluster" ] || [ "$STARTMODE" == "qcluster" ]; then
    /app/.venv/bin/python /app/manage.py qcluster
    exit $?
fi

echo "Specify argument: app qcluster version"
exit 1
