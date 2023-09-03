#!/bin/bash

ENV_FILE_PATH=".env"
if [ -f "$ENV_FILE_PATH" ]; then
    source "$ENV_FILE_PATH"
else
    echo "No .env file found at $ENV_FILE_PATH. Exiting."
    exit 1
fi

if [[ -z "$LT_RESTIC_REPO" ]] || [[ -z "$LT_RESTIC_PASS" ]]; then
    echo "LT_RESTIC_REPO and/or LT_RESTIC_PASS environment variables are not set."
    exit 1
fi

export RESTIC_REPOSITORY="$LT_RESTIC_REPO"
export RESTIC_PASSWORD="$LT_RESTIC_PASS"

mkdir -p "$HOST_DUMP_PATH"

if ! command -v restic &> /dev/null; then
    echo "Restic is not installed. Please install it first."
    exit 1
fi

TEMP_PATH="/tmp/temp_backup"

echo "Starting the restore process..."
restic restore latest --target "$HOST_DUMP_PATH"

mv "$HOST_DUMP_PATH/$TEMP_PATH/"* "$HOST_DUMP_PATH"
rm -rf "$HOST_DUMP_PATH/tmp"

if [ $? -eq 0 ]; then
    echo "Data restored successfully to $HOST_DUMP_PATH"
else
    echo "Error occurred during the restore process."
    exit 1
fi

FULL_PATH="$HOST_DUMP_PATH"mongodump.archive

CONTAINER_NAME="story-store"
docker cp "$FULL_PATH" "$CONTAINER_NAME:$CONTAINER_DUMP_PATH"

echo "Applying the MongoDB dump to the container..."
docker exec -i "$CONTAINER_NAME" mongo -u "$MONGODB_USERNAME" -p "$MONGODB_PASSWORD" --authenticationDatabase=admin \
                --eval "db.getSiblingDB('little_turtle').dropDatabase()"
docker exec -i "$CONTAINER_NAME" mongorestore --username "$MONGODB_USERNAME" --password "$MONGODB_PASSWORD" \
                --archive="$CONTAINER_DUMP_PATH" --gzip

if [ $? -eq 0 ]; then
    echo "MongoDB data successfully restored to the container."
else
    echo "Error occurred during the MongoDB restore process."
    exit 1
fi

docker exec -i "$CONTAINER_NAME" rm "$CONTAINER_DUMP_PATH"
