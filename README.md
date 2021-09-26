# USOS filter (for University of Warsaw)

Do you find USOS subject selection to be tedious and lacking basic filter settings? Well, this script will solve all your problems. USOS filter facilitates usage of custom filtering option like showing only subject with specific ECTS score, or subject taught at specific venue.

## Installation

To use the scipt you need to install all required dependencies using the following code:
```
pip install -r requirements.txt
```

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
filter.add_condition(lambda x: int(x['Punkty ECTS']) >= 4) # Show groups with ECTS score >= 4
filter.add_condition(lambda x: int(x['Liczba godzin']) >= 30) # Show groups that take at least 30 hours total
filter.add_condition(lambda x: x['Prowadzący'] == 'XYZ' # Show all groups run by person XYZ
filter.add_condition(lambda x: x['Język wykładowy'] == 'polski' # Show groups being taught in polish language
```

#### All dictionary keys:
* 'Cykl dydaktyczny' - e.g. 'Semestr zimowy 2021/22'
* 'Język wykładowy' - e.g. 'polski'
* 'Kod przedmiotu' - e.g. '3221-FBA-KLB-OG'
* 'Koszt' - e.g. '15 żetonów typu OG'
* 'Liczba godzin' - e.g. '15'
* 'Liczba miejsc (zarejestrowani/limit)' - e.g. '0/15'
* 'Nazwa przedmiotu' - e.g. 'Kalejdoskop literatury białoruskiej'
* 'Prowadzący' - e.g. 'dr Jan Kowalski'
* 'Punkty ECTS' - e.g. '4'
* 'Termin' - e.g. 'Czwartek  15:00-16:30'
* 'Typ zajęć' - e.g. 'Ćwiczenia'
* 'url' - e.g. 'https://rejestracja.usos.uw.edu.pl/course.php?rg=0000-2021-OG-UN&group=0000-OG&subject=3221-FBA-KLB-OG&cdyd=2021Z&full=0&course_id=464876&gr_no=1'

All keys and values are stored as strings, thus, sometimes you need to cast data to different types. Whenever you need to do this, please, try to make it as general as possible. Some values have many formats e.g. 'Punkty ECTS' can be equal to '3.5'. Because of that its better to cast to float, rather than int. If at any point casting fails, or your filter throws exception because of strange data format script will mute the exception, and proceed as if it never happened.

Finally, to show the results run show() method:
```
filter.show()
```

It may take up to a few minutes, depending on the size of the list and your internet connection. Scipt will recursively iterate over any found sublist, and will print all found groups.

## Notice

This script was tested only for University for Warsaw, therefore, I don't know if it works for other universities as well.
