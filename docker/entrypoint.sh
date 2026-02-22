#!/bin/bash
set -e

export HOME=/app
#export NUM_WORKERS=$((1 * $(nproc --all)))
export NUM_WORKERS=1

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
    # start daphne ASGI server (handles both HTTP and WebSocket)
    /app/.venv/bin/python -m daphne rockon.asgi:application \
        --bind 0.0.0.0 \
        --port 8000 \
        --unix-socket /run/rockon/app.sock \
        --access-log /dev/null \
        --verbosity 1
      exit $?
fi

if [ "$1" == "qcluster" ] || [ "$STARTMODE" == "qcluster" ]; then
    /app/.venv/bin/python /app/manage.py qcluster
    exit $?
fi

echo "Specify argument: app qcluster version"
exit 1
