# eregs-2.0 [![Build Status](https://travis-ci.org/cfpb/eregs-2.0.svg?branch=master)](https://travis-ci.org/cfpb/eregs-2.0)

This is the new version of eRegs.

## Installation

To make it go, you'll need MySQL. Create a user named `eregs` and give that user sufficient privileges to run
migrations (`alter user eregs superuser` should be fine for development). pip install the requirements and run the migrations.

You'll need some sample data, so check the `data` directory for the initial version of Reg C, or check out the entire
[regulations-xml](https://github.com/cfpb/regulations-xml) repository. Load Reg C into the database by running

`./manage.py import_xml path/to/2011-31712.xml`

This should take no more than 10 seconds and will populate the database with the first version of Reg C. `./manage.py runserver` and
visit http://localhost:8000 to get the initial eRegs screen. Click on `Reg C` and it'll take you to the first section.

## Working on the front-end

1. Install [Node.js](http://nodejs.org) v4 or greater.
1. `./setup.sh` will install dependencies and build the project.

After the initial set-up:

- `npm run build` - Bundle and minify all front-end assets.
- `npm run watch` - Bundle Less and JS files whenever they're changed.
- `npm test` - Run JS unit tests and lint source files.

## Open source licensing info

1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)
