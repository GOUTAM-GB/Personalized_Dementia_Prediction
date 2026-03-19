#!/usr/bin/env bash

gunicorn personalised_dementia_prediction.wsgi:application