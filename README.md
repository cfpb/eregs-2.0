# :warning: THIS REPO IS DEPRECATED (12/3/2018) :warning:
Please migrate to using [cfgov-refresh](https://github.com/cfpb/cfgov-refresh).

# eregs-2.0

[![Build Status](https://travis-ci.org/cfpb/eregs-2.0.svg?branch=master)](https://travis-ci.org/cfpb/eregs-2.0)
[![Coverage Status](https://coveralls.io/repos/github/cfpb/eregs-2.0/badge.svg?branch=master)](https://coveralls.io/github/cfpb/eregs-2.0?branch=master)

Work in progress. This is an updated back-end for [consumerfinance.gov/eregulations](https://www.consumerfinance.gov/eregulations/).

[Documentation](https://cfpb.github.io/eregs-2.0/)

## Development Quick-start

Create a MySQL database named `eregs` with a priviledged user named `eregs`, password `eregs`, then:

```
mkvirtualenv eregs
workon eregs
pip install -r requirements.txt
./manage.py import_xml data/2011-31712.xml
./setup.sh
./manage.py runserver
```


## Detailed installation

The installation instructions will guide you through cloning the repo, setting up the database, importing an initial regulation, and building the front-end. Additional instructions can be found in the project's [documentation](https://cfpb.github.io/eregs-2.0/)

### Dependencies

- Python >= 2.6
- Node >= 4
- MySQL
- ElasticSearch 2.3

MySQL and ElasticSearch can be installed using `homebrew`:

```
brew install mysql
brew install elasticsearch23
```

### Initial setup

Clone the repository, create a Python virtualenv, and install the project's dependencies.

```
git clone https://github.com/cfpb/eregs-2.0
cd eregs-2.0
mkvirtualenv eregs
workon eregs
pip install -r requirements.txt
```

### Database setup (for development)

Login to MySQL and create a database named `eregs`  with an `eregs` superuser.

```
mysql
mysql> CREATE DATABASE IF NOT EXISTS eregs;
mysql> CREATE USER 'eregs'@'localhost' IDENTIFIED BY 'eregs';
mysql> GRANT ALL PRIVILEGES ON eregs.* TO 'eregs'@'localhost';
mysql> GRANT ALL PRIVILEGES ON test_eregs.* TO 'eregs'@'localhost';
mysql> FLUSH PRIVILEGES;
```


### Import a regulation

The application requires [RegML-compliant xml](https://github.com/cfpb/regulations-xml) data. To simplify development, sample data has been provided. To load the sample data into the database run:

```
./manage.py import_xml data/2011-31712.xml
```

This will populate the database with the first version of CFPB's regulation C C.

### Build the front-end

1. Install [Node.js](http://nodejs.org) v4 or greater.
1. `./setup.sh` will install dependencies and build the project.

For front-end development, after the initial set-up:

- `npm run build` - Bundle and minify all front-end assets.
- `npm run watch` - Bundle Less and JS files whenever they're changed.
- `npm test` - Run JS unit tests and lint source files.

### Run the application

To run the application, run `./manage.py runserver` and
visit http://localhost:8000 to get the initial eRegulations screen.

## Open source licensing info

1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)
