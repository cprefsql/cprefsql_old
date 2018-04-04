#!/bin/bash

function printUsage(){
  echo "install [-h HOSTNAME -d DATABASENAME -u USER]"
  exit 1
}

# Default options
DB_NAME="benchmark"
USER="postgres"
HOSTNAME="localhost"

# Get options from arguments
while getopts "h:d:u:" OPTION; do
  case $OPTION in
    d) DB_NAME=$OPTARG ;;
    u) USER=$OPTARG ;;
    h) HOSTNAME=$OPTARG ;;
    ?) printUsage ;;
  esac
done

# Copy library
LIBRARY_DIR="/usr/lib/postgresql/libuprefsql"
echo "Enter root password do install library into PostgreSQL."
su -c "mkdir -p $LIBRARY_DIR && chmod 777 $LIBRARY_DIR"
mkdir -p $LIBRARY_DIR/uprefsql/
cp -Rf src/uprefsql/*.py $LIBRARY_DIR/uprefsql/

echo $DB_NAME

# Enable preferences
psql -h $HOSTNAME -d $DB_NAME -U $USER -f sql/enable_preferences.sql
psql -h $HOSTNAME -d $DB_NAME -U $USER -f sql/create_preference.sql
psql -h $HOSTNAME -d $DB_NAME -U $USER -f sql/most_preferred.sql
psql -h $HOSTNAME -d $DB_NAME -U $USER -f sql/most_preferred_optimized.sql
psql -h $HOSTNAME -d $DB_NAME -U $USER -f sql/most_preferred_partition.sql
psql -h $HOSTNAME -d $DB_NAME -U $USER -f sql/mostk_preferred.sql
psql -h $HOSTNAME -d $DB_NAME -U $USER -f sql/mostk_preferred_optimized.sql
psql -h $HOSTNAME -d $DB_NAME -U $USER -f sql/mostk_preferred_partition.sql
psql -h $HOSTNAME -d $DB_NAME -U $USER -f sql/enable_update_preferences.sql
psql -h $HOSTNAME -d $DB_NAME -U $USER -f sql/update_mostk_preferred.sql
