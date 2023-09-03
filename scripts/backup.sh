#!/bin/bash

ENV_FILE_PATH=".env"

if [ -f "$ENV_FILE_PATH" ]; then
    source "$ENV_FILE_PATH"
else
    echo "No .env file found at $ENV_FILE_PATH"
    exit 1
fi

if [[ -z "$MONGODB_USERNAME" ]] || [[ -z "$MONGODB_PASSWORD" ]]; then
    echo "MONGODB_USERNAME and/or MONGODB_PASSWORD environment variables are not set."
    exit 1
fi

if [[ -z "$LT_RESTIC_REPO" ]] || [[ -z "$LT_RESTIC_PASS" ]]; then
    echo "LT_RESTIC_REPO and/or LT_RESTIC_PASS environment variables are not set."
    exit 1
fi

export RESTIC_REPOSITORY="$LT_RESTIC_REPO"
export RESTIC_PASSWORD="$LT_RESTIC_PASS"

mkdir -p "$HOST_DUMP_PATH"

docker exec story-store mongodump --username "$MONGODB_USERNAME" --password "$MONGODB_PASSWORD" --archive="$CONTAINER_DUMP_PATH" --gzip
docker cp story-store:"$CONTAINER_DUMP_PATH" "$HOST_DUMP_PATH"

TEMP_PATH="/tmp/temp_backup"
mkdir -p "$TEMP_PATH"

rsync -a --progress "$HOST_DUMP_PATH/" "$TEMP_PATH/"

restic backup "$TEMP_PATH"
rm -rf "$TEMP_PATH"

echo "Backup completed."