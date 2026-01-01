#!/usr/bin/env bash
set -e

# Run all pre-start tasks (DB wait, migrations, initial data)
python -m app.prestart

# Execute the CMD passed to the container
exec "$@"
