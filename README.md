# eregs-2.0

This is the new version of eRegs.

To make it go, you'll need PostgreSQL. Create a user named `eregs` and give that user sufficient privileges to run
migrations (`alter user eregs superuser` should be fine for development). pip install the requirements and run the migrations.

You'll need some sample data, so check the `data` directory for the initial version of Reg C, or check out the entire 
`[regulations-xml][https://github.com/cfpb/regulations-xml]` repository. Load Reg C into the database by running

`./manage.py import_xml path/to/2011-31712.xml`

This should take no more than 10 seconds and will populate the database with the first version of Reg C. `./manage.py runserver` and
visit http://localhost:8000 to get the initial eRegs screen. Click on `Reg C` and it'll take you to the first section.

Right now the frontend does not really work, so you have to navigate to the URL you want manually. A node is uniquely identified
across all regulations by the combination of document number, effective date, and label, in that order. Since there's only one 
regulation currently available, you'll have to navigate to the specific node you're interested in by modifying the label. Refer to
the RegML file you're working from for labels.
