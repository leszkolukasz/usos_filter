# USOS filter (for University of Warsaw)
![license](https://img.shields.io/github/license/leszkolukasz/usos_filter.svg)
![status](https://img.shields.io/badge/status-finished-green)

Do you find USOS subject selection to be tedious and lacking basic filter settings? Well, this script will solve all your problems. USOS filter facilitates usage of custom filtering option like showing only subject with specific ECTS score, or subject taught at specific venue.

## Installation

To use the scipt you need to install all required dependencies using the following code:
```
pip install -r requirements.txt
```

Project was tested with python 3.10 and I don't guarantee that it will work with newer python releases.

## Usage

To use the scipt you will need to directly edit main.py file. At the bottom of the file create new instance of USOSFilter class. With this instance you can add new filter options, and print all found subject.

USOSFilter class has the following constructor parameters:
* url - URL to the list of subject you want to filter from (e.g. 'https://rejestracja.usos.uw.edu.pl/catalogue.php?rg=0000-2021-OG-UN')
* expired - set this to True if you want to see groups with no seats left (default: False)
* verbose - set this to True if you want to see information about currently searched URL (positional only, default: False)

#### Examples:
```
filter = UsosFilter('https://rejestracja.usos.uw.edu.pl/catalogue.php?rg=0000-2021-OG-UN')
filter = UsosFilter('https://rejestracja.usos.uw.edu.pl/catalogue.php?rg=0000-2021-OG-UN', True)
filter = UsosFilter('https://rejestracja.usos.uw.edu.pl/catalogue.php?rg=0000-2021-OG-UN', True, verbose=True)
```

Now that you have instance you need to add custom filters. To do that create a function (lambda allowed) that takes dictionary object as argument, and returns True or False, and then add it to the instance using add_condition method. Dictionary is an object that keeps information about a single subject group. Its keys correspond to information like name of the subject, ECTS score, venue, gruop size etc. (all available keys are shown later). Using this dictionary create you own filter that returns True if you want to show subject with corresponding data or False otherwise. (See examples for more clarification)

#### Examples:
```
filter = UsosFilter('https://rejestracja.usos.uw.edu.pl/catalogue.php?rg=0000-2021-OG-UN')
filter.add_condition(lambda x: int(x['ects']) >= 4) # Show groups with ECTS score >= 4
filter.add_condition(lambda x: int(x['span']) >= 30) # Show groups that take at least 30 hours total
filter.add_condition(lambda x: x['lecturer'] == 'xyz' # Show all groups run by person xyz
filter.add_condition(lambda x: x['language'] == 'polski' # Show groups being taught in polish language
```

#### All dictionary keys:
* 'term' (str) - term when the subject is happening e.g. 'semestr zimowy 2021/22'
* 'language' (str) - language in which the subject is taugth e.g. 'polski'
* 'id' (str) - code of the subject e.g. '3221-FBA-KLB-OG'
* 'cost' (float) - cost of the subject in żetony e.g. 15.0
* 'span' (float) - total span of the subject in hours e.g. 30.0
* 'seats' (tuple(float, float)) - seats taken vs all available seats e.g. (10., 15.)
* 'name' (str) - name of the subject e.g. 'kalejdoskop literatury białoruskiej'
* 'lecturer' (list(str)) - name of the lecturer (may be more than one) e.g. ['dr Jan Kowalski']
* 'ects' (float) - ects score e.g. 4.0
* 'time' (list(tuple(str, datetime.time, datetime.time))) - time when the subject is happening; subsequent elements of the tuple are: name of the weekday, starting time, finishing time e.g. ['czwartek'. datetime.time('10:00'), datetime.time('11:30')]
* 'type' (str) - type of the subject e.g. 'ćwiczenia'
* 'url' - (str) url to the subject page in USOS e.g. 'https://rejestracja.usos.uw.edu.pl/course.php?rg=0000-2021-OG-UN&group=0000-OG&subject=3221-FBA-KLB-OG&cdyd=2021Z&full=0&course_id=464876&gr_no=1'
* 'venue' (str) - place where the subject is happening e.g. 'Gmach Audytoryjny, Warszawa, ul. Krakowskie Przedmieście 26/28'

Some subjects lack specific data or have this data in strange format. It these cases values for this data were replaced with 'unknown' or -1, but I could have ommited some cases. If your filter throws exception because of strange data format script will mute the exception, and proceed as if it never happened.

String are in lowercase except for lecturers, id, url and venue.

Finally, to show the results run show() method:
```
filter.show()
```

It may take up to a few minutes, depending on the size of the list and your internet connection. Scipt will recursively iterate over any found sublist, and will print all found groups.

## Notice

This script was tested only for University for Warsaw, therefore, I don't know if it works for other universities as well.
