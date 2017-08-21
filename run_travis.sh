#!/usr/bin/env bash

set -e
set -x

if [[ $FRONTEND == "1" ]]; then
    rm -rf ~/.nvm
    curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.30.2/install.sh | bash
    source ~/.nvm/nvm.sh
    nvm install 6
    npm install -g npm

    ./setup.sh

    npm test
    exit 0
fi

if [[ $TOXENV == *"sqlite"* ]]; then
    echo "Nothing to install for sqlite"
    exit 0
elif [[ $TOXENV == *"mysql"* ]]; then
    export MYSQL_NAME=eregs
    export MYSQL_USER=travis
    export MYSQL_PW=travis
    export MYSQL_CMD=mysql
    export MYSQL_HOST=127.0.0.1
    export MYSQL_PORT=3307

    if [[ $TOXENV == *"mysql51"* ]]; then
        MYSQL_DOWNLOAD=mysql-5.1.45-linux-x86_64-glibc23.tar.gz
    elif [[ $TOXENV == *"mysql57"* ]]; then
        MYSQL_DOWNLOAD=mysql-5.7.18-linux-glibc2.5-x86_64.tar.gz
    fi

    export MYSQL_CMD=~/sandboxes/msb/use

    sudo apt-get install -y perl libaio1 libaio-dev
    curl -L https://cpanmin.us | sudo perl - App::cpanminus
    sudo cpanm MySQL::Sandbox

    wget -N -P mysql-archives http://downloads.mysql.com/archives/get/file/$MYSQL_DOWNLOAD

    mkdir ~/sandboxes
    sudo chown -R travis:travis ~/sandboxes

    make_sandbox "mysql-archives/$MYSQL_DOWNLOAD" -- -u $MYSQL_USER -p $MYSQL_PW -P $MYSQL_PORT -d msb --no_confirm

    $MYSQL_CMD -uroot -e "CREATE DATABASE IF NOT EXISTS $MYSQL_NAME;"
    $MYSQL_CMD -uroot -e "GRANT ALL PRIVILEGES ON *.* TO $MYSQL_USER@localhost"

    # Confirm version is correct.
    mysql -u$MYSQL_USER -p$MYSQL_PW -h $MYSQL_HOST -P $MYSQL_PORT -e "SELECT VERSION();"
fi

tox
