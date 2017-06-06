# eRegs 2.0

This is the documentation for the new version of [eRegs](https://www.consumerfinance.gov/eregulations), the interface for reading the Bureau's regulatory documents. This document describes how to deploy eRegs, add and update content, and troubleshoot.

## Getting eRegs

eRegs can be checked out from the Github repository:

	git clone https://github.com/cfpb/eregs-2.0
	cd eregs-2.0
	pip install -r requirements.txt

The other thing you'll need is the `eregsip` repository, which contains some static content for branding. If you are inside the CFPB developer VPN, you know where you can find this repository, and if you're not, you'll have to go without. You can run the project without this repository, but some static assets will be missing.

## Installing the prerequisites

In addition to installing the various required Python modules, you will need to install and configure a MySQL database and an ElasticSearch instance. If you are developing on a Mac, you may be able to install both of these via `homebrew` like so:

	brew install mysql
	brew install elasticsearch23

Note that you will need ElasticSearch 2.3, not one of the later versions, which do not work correctly with Haystack, the search interface between Django and a search backend. If you are not able to install ElasticSearch 2.3, it might have been removed from Homebrew, in which case you will have to download the binary yourself. You can get the ElasticSearch 2.3 binar [here](https://www.elastic.co/downloads/past-releases/elasticsearch-2-3-0).

Once you have MySQL installed, you'll need to configure it to match the `settings.py` file. This means creating the two databases, creating the appropriate users, and granting those users privileges on the databases. First, create two databases named `eregs` and `test_eregs`. Then, create the user `eregs` authenticated by the password `eregs`. Finally, grant the `eregs` user privileges by logging into MySQL as root (`mysql -u root`) and running the following commands:

	grant all privileges on eregs.* to 'eregs'@'localhost' identified by eregs
	grant all privileges on eregs.* to 'test_eregs'@'localhost' identified by eregs
	
Once that's done, you should run `./manage.py migrate` to create the database and the model tables. You should also make sure that ElasticSearch is running.

## Loading data

In order to load data, you'll need to grab the repository that contains the RegML files. Wherever you want to have this data, do:

	git clone https://github.com/cfpb/regulations-xml

This repository has the following structure:

	images                     # images that are embedded in the regulations
	notice/                    # change notices for each regulation
		1003/                  # reg C
			2012-31311.xml
			...                # etc.
		1005/                  # reg E
			2012-01728.xml
			...                # etc.
		...                    # etc.
	regulation/                # compiled regulations
		1003/                  # reg C
			2011-31712.xml     # initial version of the regulation
			2012-31311.xml     # result of applying first notice
			...                # etc.
		...                    # etc.

If you run `./manage.py runserver` and go to `localhost:8000`, you'll see that there is no content in eRegs. To load some content, run the following management command:

	./manage.py import_xml /path/to/regulations-xml/regulation/1003/2011-31712.xml

This will import the initial version of Regulation C into eRegs. If you refresh your view, you will now see Regulation C on the landing page. You should be able to navigate the regulation interface in the same way that you navigate the current production eRegs interface.

In order to get search to work, you'll need to build the index:

	./manage.py rebuild_index

This will build the ElasticSearch index for eRegs. In the future, you can update the index by running `./manage.py update_index`. You should now be able to search the eRegs regulatory text in the normal manner.

## Loading diffs

Diffs are a special form of content that indicate the difference between two versions of a regulation. It is important to note that diffs are _not_ symmetric; in other words, if _X_ and _Y_ are versions of a single regulation, `diff(X, Y) != diff(Y, X)`. Therefore, right now, if you want to display bidirectional differences in regulatory content, you need to generate diffs in both directions. There's a command to do that:

	./manage.py import_diff /path/to/regulations-xml/regulation/regnumber/version1.xml /path/to/regulations-xml/regulation/regnumber/version2.xml
	./manage.py import_diff /path/to/regulations-xml/regulation/regnumber/version2.xml /path/to/regulations-xml/regulation/regnumber/version1.xml

Here, `regnumber` is the part number of the regulation (e.g. 1003) and `version1` and `version2` are the document numbers of the respective versions. Make sure that `regnumber` is the same in both cases; you can of course generate a diff between two different part numbers, but that diff would make no sense. In the future, there will be a single management command that will generate the bidirectional diffs for you, but for the moment, you have to run it twice with the arguments swapped, as above, to have differences in both directions.
