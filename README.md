This guide explains how to use the code written here to analyze other editorial boards. The first step is to download python and pip. Run `pip install -r requirements.txt` to install the dependencies. There are a few local update to the Scholarly library. Copy them into the downloaded Scholarly code in ...\Python\Python3x\Lib\site-packages. We're ready to get up and running.

For the program to work as is, we need to store the data for each journal in a separate folder, all contained in a large container folder. Within the folder for a given journal, we need a seed file called names.txt. The file stores an array of information in JSON format, as follows:

```
[
    {
        "name": "John Smith",
        "institution": "Example University",
        "any other information you care about": ...,
        ...
    },
    ...
]
```

The only required attributes are the name and institution, which are both used when searching Google Scholar. Other attributes could include journal section, gender, underrepresented minority status, nationality, or anything else. Once we have a names.txt file, we are ready to compile papers. To do so, copy super\_scraper.py into the journal's folder, and run it.

The script may run for an hour or longer, depending on many authors are in the names.txt file. The script will attempt to resolve ambiguous cases (such as two "John Smith" user profiles appearing on Google Scholar), but it may fail occasionally. Therefore, it may be beneficial to scroll through the final papers.txt file to ensure that the papers assigned to each author appear reasonable within their field. For example, while gathering papers on an economics journal, an author with many medical publications may be a sign that the script chose incorrectly when resolving an ambiguity. In this case, manually delete the author's section in papers.txt, look into which user profile is correct, and then add the author's name to blacklist.txt (as explained in the next paragraph).

It may also be the case that certain authors have private profiles on Google Scholar. When this happens, the script will create a file called blacklist.txt. It is your choice whether to ignore these authors or get a little technical to find their papers anyway. Assuming you want to find their papers, read on. Otherwise, skip the next paragraph.

Delete blacklist.txt; we are going to find their papers now. Once the script finishes gathering papers for all other authors, change line 38 of super\_scraper.py by removing the comment "# ". This will set the Scholarly library to request manual HTML input. Run super\_scraper.py again. The program will now prompt you with a Google Scholar URL. It needs the HTML of the page. Go to the URL and go into Inspect Element in the developer tools. Copy the HTML out of what's labelled as the "body" tag (or get everything). The terminal only accepts inputs that are so large, so we need to split the paste into multiple chunks of 10000 characters. Run silly\_splitter.py to do this (so named because it's silly that we need to do this anyway!). It will create a file called silly\_splitter.txt. Paste the HTML into this file, then return to silly\_splitter.py. When you press enter, it will copy the first chunk of 10000 characters to your clipboard. Return to the terminal running super\_scraper.py, paste, and press enter. Go back to silly\_splitter and press enter for the next 10000 characters. Go back to super\_scraper and paste. Repeat this until you have pasted the entire HTML contents, which usually takes six chunks of 10000 characters. Press enter one more time in super\_scraper.py to tell it the HTML input is over, then go to the new URL it gives you and repeat the entire process. For a given author, you may need to do so between two and ten times. Remember to always paste the new HTML into silly\_splitter.txt so you don't copy old HTML into super\_scraper.py.

Now we have all the papers from the authors in names.txt. Copy in the file called cleanup.py and run it. This may take ten minutes or so to run. It will sanitize the papers.txt and names.txt files, and it will create a new file called coauthors.txt. This file has the information we need for our graph. (To manually check coauthors, run sanity.py.)

To generate a graph, copy the file called graph.py into the large container folder (i.e., the one with folders for each journal). Note that this script expects the names.txt file for each individual journal to contain attributes called 'URM', meaning underrepresented minority (value is true or false); 'female' (value is 'male' or 'female'); and 'section' (value is editorial board section). The Editor-in-Chief should have their section attribute as 'Editor-in-Chief' to get properly counted. Feel free to change around line 68 of graph.py to include node properties from new attributes you put in names.txt. In addition to a graph, this script will generate a MatPlotLib histogram of the degrees of the editors, with the bar containing the Editor-in-Chief highlighted.

At this point, we have done everything possible for one journal. The remainder of the guide explains how to organize multiple journals. There are six files for this purpose.

The first is accumulator.py, which creates a file called all\_papers.txt in the container folder. When super\_scraper.py searches for papers for an author in a given journal, it first checks whether we already have information on that author in all\_papers.txt. If so, it uses that stored information to save time. This is useful when the same author serves as a member of multiple editorial boards.

The second is gather\_names.py. If there is a folder called "all", then running gather\_names.py will combine the names.txt files from all other journals into one. Then running super\_scraper.py (after running accumulator.py) will quickly generate a papers.txt file, and cleanup.py will sanitize everything and generate a coauthors.txt file. The "all" folder is useful for finding average statistics across all journals.

The third is combine.py, which is more general than gather\_names.py. Running it in the container folder lets you pick which journals to combine. It will create a folder called "COMBO JOURNAL1 + JOURNAL2 + ..." with a combined names.txt file, and it will autogenerate a papers.txt file. Running cleanup.py within the new combo folder finishes the process.

The fourth is institutions.py, which when run in the container folder lets you pick journals to view institution data. It will create a histogram of the top 15 institutions from the chosen journal. You can change this number in the code if desired.

The fifth is analyze.py, which when run in the container folder generates a file called stats.txt. The script expects each names.txt file to have section, URM, and gender attributes, although you can edit the code to generate whatever statistics interest you.

The sixth and final is graph.py, which we have already seen briefly. Running it in the container folder lets you generate interactive graphs for a chosen journal. This script also expects the names.txt files to have section, URM, and gender attributes, although again you can change around line 68 to fit the script to your purposes.

That's all! Please freely edit the code locally to suit your needs.
