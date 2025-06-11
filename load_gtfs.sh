#!/bin/bash
export FLASK_APP=app.py
flask db upgrade
python gtfs_loader.py
