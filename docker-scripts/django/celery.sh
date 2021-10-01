#!/bin/bash

set -o errexit
set -o nounset

celery -A api_config worker -l INFO