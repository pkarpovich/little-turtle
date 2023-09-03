#!/bin/bash

if ! command -v restic &> /dev/null; then
    echo "restic is not installed. Please install it first."
    exit 1
fi

ENV_FILE_PATH=".env"
if [ -f "$ENV_FILE_PATH" ]; then
    source "$ENV_FILE_PATH"
else
    echo "No .env file found at $ENV_FILE_PATH. Please ensure the custom RESTIC variables are set."
    exit 1
fi

if [[ -z "$LT_RESTIC_REPO" ]] || [[ -z "$LT_RESTIC_PASS" ]]; then
    echo "LT_RESTIC_REPO and/or LT_RESTIC_PASS environment variables are not set."
    exit 1
fi

export RESTIC_REPOSITORY="$LT_RESTIC_REPO"
export RESTIC_PASSWORD="$LT_RESTIC_PASS"

restic init

if [ $? -ne 0 ]; then
    echo "Error initializing restic repository."
    exit 1
fi

echo "Restic repository initialized successfully."
