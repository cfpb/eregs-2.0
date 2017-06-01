#!/bin/sh

set -e

# Initialize project directories

init(){
    NODE_DIR=node_modules
    echo 'npm components directory:', $NODE_DIR
}

# Clean project deps
clean(){
    if [ -d $NODE_DIR ]; then
      echo 'Removing project dependency directories...'
      rm -rf $NODE_DIR
    fi
    echo 'Project dependencies have been removed.'
}

# Install deps
install(){
    echo 'Installing project dependencies...'
    npm install
    npm install -g grunt-cli
}

# Build
build(){
    echo 'Building project...'
    npm run build
}

init
clean
install
build
