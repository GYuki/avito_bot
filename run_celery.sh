#!/bin/sh

celery -A parserapp worker --loglevel=info --beat
