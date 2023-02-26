#!/bin/bash

if [ "$BASH_SOURCE" = "$0" ]; then
    echo "Error: script must be executed with 'source' command"
    exit 1
fi

install_env() {
    python3 -m venv venv \
        && source venv/bin/activate \
        && pip install -r requirements.txt
}

activate_env() {
    [ ! -d "venv" ] && install_env \
        || source venv/bin/activate
}

activate_env \
    && echo " _____ _    _ ______  _____ _____ _____  _    _          _   _
|_   _| |  | |  ____|/ ____/ ____|_   _|/ \  | |        | \ | |
  | | | |__| | |__  | (___| (___   | | / _ \ | |        |  \| |
  | | |  __  |  __|  \___ \\___ \  | |/ ___ \| |        | . \`|
 _| |_| |  | | |____ ____) |___) |_| /_/   \_\_|____    |_|\_|
|_____|_|  |_|______|_____/_____/(_)_/ \_/\_(_|_____|   (_)(_)" \
    || echo "Failed to activate virtual environment"
