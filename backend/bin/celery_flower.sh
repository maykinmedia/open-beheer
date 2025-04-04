#!/bin/bash
exec celery flower --app openbeheer --workdir src
