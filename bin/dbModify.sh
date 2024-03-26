#!/bin/bash
# SQLGenerator

set -Eeuo pipefail

usage() {
  echo "Usage: $0 (create|destroy|reset|dump)"
}

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

case $1 in
  "create")
    if [ -e "db/discord_bot.sqlite3" ]; then
      echo "Error: database already exists"
    else
      sqlite3 db/discord_bot.sqlite3 < db/schema/schema_v1.sql
    fi
    ;;

  "destroy")
    rm -rf db/discord_bot.sqlite3
    ;;

  "reset")
    rm -rf db/discord_bot.sqlite3
    sqlite3 db/discord_bot.sqlite3 < db/schema/schema_v1.sql
    ;;

  "dump")
    sqlite3 -batch -line db/discord_bot.sqlite3 'SELECT * FROM servers'
    ;;
  *)
    usage
    exit 1
    ;;
esac

