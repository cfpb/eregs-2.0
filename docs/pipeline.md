# End-to-end pipeline for content deployment

The following is a set of instructions for how to go from a document located on the [Federal Register](http://www.federalregister.gov) website to eRegs content.

## Versioning regulations

Regulations are promulgated via notices published by the Federal Register. Every regulation or modification thereof is contained in a specific document number. Document numbers are typically formed by the pattern `<year>-<order-of-publication>`, where `<order-of-publication>` represents the number of the document published that year, i.e. the first document published in 2011 would have the document number 2011-1. Another example: the first notice that originates Regulation C is `2011-31712`.

Regulations also take effect on particular dates. A single document might contain multiple effective dates, and multiple documents may take effect on the same effective date. The combination of document number and effective date are unique, however, so together they serve to identify a particular version of the regulation. Notices other than the one that originates the regulation will contain modifications to the previous version of the regulation, so the task at hand is to compile the text into an original starting point, plus a series of changes that define the regulation at each step.

## Parsing the original document

The documents that exist on the Federal Register's website are in "XML", where the scare quotes indicate that the markup is not semantic, as it is meant to be transpiled into a PDF suitable for printing. What we do is we take that XML and we turn it into a semantic document in which different parts of the regulation are clearly delineated. We also decouple the semantics of the document from its presentation.

In order to make this happen, we rely on a tool called `regulations-parser`, which can be found [on Github](https://github.com/cfpb/regulations-parser). This tool will fetch the source files, including change notices, from the Federal Register and compiles them into a series of XML files which represent the regulation at every stage of its existence.

The usage of `regulations-parser` is described in the README on Github. For the purposes of this walkthrough, we'll assume that you've got the source files to work with. To compile a source file into RegML, run

	python build_from.py fr-notices/articles/xml/201/131/725.xml 12 2011-31712 15 1693

The only really important parameter here is the document number. The other parameters can be left constant (they correspond to the title of the regulation, which is always 12, and the issuing authority, which is actually irrelevant). If all goes well, the parser will figure out which document numbers form the version chain, parse the original document, then fetch and parse the subsequent notices, and finally output the whole thing in XML that validates with the RegML schema. If all does not go well, you might want to read [the documentation](https://regulation-parser.readthedocs.io/en/latest/) for `regulation-parser`. The RegML files thus generated will be located whatever the `settings.OUTPUT_DIR` variable is set to. 

## The RegML schema

The above procedure only needs to be done once. The point of the RegML schema is to make it so that you don't have to keep running the regulations parser over and over again; the parser is quite finicky and slow and often makes mistakes, and fixing the source that leads to the mistakes is difficult. In order to see the effects, you have to then rerun the whole parser again, which can take hours for large regulations with many notices. With RegML, you instead end up with separate versions of the regulation that can be fixed independently of each other; moreover, changes propagate downstream, so fixing version _n_ and fixing the notice that transforms _n_ into _n + 1_, automatically ensures that version _n + 1_ will also be correct. More details about the schema can be found [here](regml) and by reading [the code](https://github.com/cfpb/regulations-schema) and [the documentation](http://cfpb.github.io/regulations-schema/).

## Compiling regulations

Now you have a series of regulation files organized in the following fashion:

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
	diff/                      # diff files
		1003/
	

Here, as indicated, the file `regulation/2011-31311.xml` is the result of applying the file `notice/2012-31311.xml` to the original notice `regulation/2011-31712.xml`. How is this done?

You'll be pleased to learn that there's a tool for that. It's called `regulations-xml-parser` and like everything, you can get it [on Github](https://github.com/cfpb/regulations-xml-parser). Despite the unfortunate similarity in names, `regulations-xml-parser` is not so much a parser as a tool for transforming and verifying RegML. The full set of abilities of `regulations-xml-parser` is beyond the scope of this document, but the thing that matters the most to us here is that the tool can take a regulation and apply notices to it in successive fashion to generate every version of the regulation. The easiest way to do this is with the `apply-through` command, like so:

	python regml.py apply-through <title-number> <regulation-number>

The title number is always going to be 12, because that is the title number of the authorizing legislation. The regulation number is 1001 for Regulation A, 1002 for Regulation B, and so on, down to Regulation Z being number 1026. Beyond Regulation Z, letters are doubled up and the numbering continues in sequence, so that Regulation DD is 1030, for example.

When you execute the above command, you'll see the original notice and the notices that apply to it. You can choose up to which notice to apply, but if you just hit `Enter` you can apply all of them. Assuming everything goes well, the tool will generate a series of regulations that live in the `regulation/<regulation-number>` directory from above. Those regulation files are the final form which will be inserted into the database as per the instructions in [Loading Data](/#loading-data).

## Generating diffs

Another thing that the `regulations-xml-parser` does is generate the diffs for the regulation. A diff, as the name suggests, shows the difference between two versions of the same regulation; in all respects, a diff is just a RegML file and is inserted into the database in the same way. To generate diffs, run:

	python regml.py generate-diffs <regulation-number>

This will produce two XML files for every pair of regulation versions. Since the diffing is not symmetric, the order of diffs matters. The files will be located in the `diff/<regulation-number>` directory in the tree displayed above. Keep in mind that `generate-diffs` should be run after running `apply-through`, since it relies solely on the generated regulation files, not the notices.

## Editing regulations

The edit-update-data load loop is the key functionality offered by RegML and the improved eRegs backend. The basic logic goes like this: if you find a mistake in the way that some regulation is displayed, the first step is to identify at which point the mistake is introduced into the pipeline. For example, if a regulation has 10 versions, and you see a mistake in version 10, it might have been introduced in version 4. Usually the most straightforward way of finding where the mistake occurs is to simply work backwards until you find where the mistake is. Once you have found the the mistake, you need to fix it in the XML. That means editing the appropriate notice file to fix whatever the problem might be. Once the problem is fixed, run `apply-through` as above to generate the regulation files, and then run `generate-diffs` to generate diffs between all the versions of the regulation. Eventually, there will be an option to `generate-diffs` that will allow you to generate diffs only between the specified versions and every other version, but for now `generate-diffs` will just use every existing regulation version.

## Deployment to production

Right now, any deployment that happens has to be done manually, i.e. all of these commands have to be run by an actual person. In the future, it should be possible to automate this by hooking up a Jenkins job to the `regulations-xml` repository, so that committing a new notice automatically triggers the compilation, diffing, and data uploading steps.
