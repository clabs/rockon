from __future__ import annotations

import json
import mimetypes
import os
import pathlib
from fileinput import filename

import dateparser
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from bblegacy.models import Bid, Event, Media, Note, Region, Track, User, Vote

DB_REL_PATH = "db/prod"
FILES_REL_PATH = "uploads"


class Command(BaseCommand):
    help = "Imports file based database from legacy system into new database and migrates files to new storage system."

    def add_arguments(self, parser):
        parser.add_argument(
            "directory",
            nargs="?",
            type=str,
            action="store",
            help="Directory to import from",
        )

    def handle(self, *args, **options):
        directory = options["directory"]
        path = pathlib.Path(directory)
        if not path.is_dir():
            raise CommandError("Directory does not exist")
        print(f"Importing from directory: {path}")
        db_path = os.path.join(path, DB_REL_PATH)
        files_path = os.path.join(path, FILES_REL_PATH)

        if not os.path.isdir(db_path):
            raise CommandError("Directory does not contain database")
        print(f"Importing database from: {db_path}")

        # Events
        print("Importing events")
        _class = Event
        _file = "events"
        item_json = json.load(open(os.path.join(db_path, _file), encoding="utf8"))
        for _item_id, item in item_json.items():
            try:
                _class.objects.get(id=item["id"])
                print(f'Skipping {item["name"]}')
                continue
            except _class.DoesNotExist:
                print(f'Importing {item["name"]}')
                item = _class(
                    id=item["id"],
                    name=item["name"],
                    opening_date=item["opening_date"],
                    closing_date=item["closing_date"],
                    created=item["created"],
                    modified=item["created"],
                )
                item.save()

        # Regions
        print("Importing regions")
        _class = Region
        _file = "regions"
        item_json = json.load(open(os.path.join(db_path, _file), encoding="utf8"))
        for _item_id, item in item_json.items():
            try:
                _class.objects.get(id=item["id"])
                print(f'Skipping {item["name"]}')
                continue
            except _class.DoesNotExist:
                print(f'Importing {item["name"]}')
                item = _class(
                    id=item["id"],
                    name=item["name"],
                    created=item["created"],
                    modified=item["created"],
                )
                item.save()

        # Tracks
        print("Importing tracks")
        _class = Track
        _file = "tracks"
        item_json = json.load(open(os.path.join(db_path, _file), encoding="utf8"))
        for _item_id, item in item_json.items():
            try:
                _class.objects.get(id=item["id"])
                print(f'Skipping {item["name"]}')
                continue
            except _class.DoesNotExist:
                print(f'Importing {item["name"]}')
                item = _class(
                    id=item["id"],
                    name=item["name"],
                    event=Event.objects.get(id=item["event"]),
                    visible=item["visible"],
                    created=item["created"],
                    modified=item["created"],
                )
                item.save()

        # Users
        print("Importing users")
        _class = User
        _file = "users"
        item_json = json.load(open(os.path.join(db_path, _file), encoding="utf8"))
        for _item_id, item in item_json.items():
            try:
                _class.objects.get(id=item["id"])
                print(f'Skipping {item["email"]}')
                continue
            except _class.DoesNotExist:
                print(f'Importing {item["email"]}')
                item = _class(
                    id=item["id"],
                    name=item["name"],
                    email=item["email"],
                    password=item["password"],
                    provider=item["provider"],
                    role=item["role"],
                    created=item["created"],
                    modified=item["created"],
                )
                item.save()

        # Bids
        print("Importing bids")
        _class = Bid
        _file = "bids"
        item_json = json.load(open(os.path.join(db_path, _file), encoding="utf8"))
        for _item_id, item in item_json.items():
            try:
                _class.objects.get(id=item["id"])
                print(f'Skipping {item["id"]}')
                continue
            except _class.DoesNotExist:
                print(f'Importing {item["id"]}')
                try:
                    _track = Track.objects.get(id=item.get("track"))
                except Track.DoesNotExist:
                    _track = None
                if _track:
                    _event = _track.event
                else:
                    _event = None
                _created = dateparser.parse(item["created"])
                if item.get("modified"):
                    _modified = dateparser.parse(item.get("modified"))
                else:
                    _modified = _created
                item = _class(
                    id=item.get("id"),
                    event=_event,
                    student=item.get("student"),
                    managed=item.get("managed"),
                    contact=item.get("contact"),
                    phone=item.get("phone"),
                    mail=item.get("mail"),
                    bandname=item.get("bandname"),
                    style=item.get("style"),
                    letter=item.get("letter"),
                    url=item.get("url"),
                    track=_track,
                    created=_created,
                    modified=_modified,
                )
                item.save()

        # Media
        print("Importing media")
        _class = Media
        _file = "media"
        item_json = json.load(open(os.path.join(db_path, _file), encoding="utf8"))
        for _item_id, item in item_json.items():
            try:
                _class.objects.get(id=item["id"])
                print(f'Skipping {item["id"]}')
                continue
            except _class.DoesNotExist:
                print(f'Importing {item["id"]}')
                if item.get("modified") == 0:
                    item["modified"] = item["created"]
                item = _class(
                    id=item.get("id"),
                    type=item.get("type"),
                    mimetype=item.get("mimetype"),
                    filename=item.get("filename"),
                    filesize=item.get("filesize"),
                    bid=Bid.objects.get(id=item.get("bid")),
                    url=item.get("url"),
                    meta=item.get("meta"),
                    created=item.get("created"),
                    modified=item.get("modified"),
                )
                item.save()

        # Votes
        _class = Vote
        _file = "votes"
        item_json = json.load(open(os.path.join(db_path, _file), encoding="utf8"))
        for _item_id, item in item_json.items():
            try:
                _class.objects.get(id=item["id"])
                print(f'Skipping {item["id"]}')
                continue
            except _class.DoesNotExist:
                print(f'Importing {item["id"]}')
                if item.get("modified", 0) == 0:
                    item["modified"] = item["created"]
                item = _class(
                    id=item.get("id"),
                    rating=item.get("rating"),
                    user=User.objects.get(id=item.get("user")),
                    bid=Bid.objects.get(id=item.get("bid")),
                    created=item.get("created"),
                    modified=item.get("modified"),
                )
                item.save()

        # Media files
        print("Copy media files to upload directory")
