# BIBLIA
BIBLIA is an application I made for cataloguing and sorting my books, but it can essentially read any data provided in CSV form with the unix dialect. It can somewhat supports excel dialect, as well as the german ";" delimiter. 

It features a regex search system, autocompletion, some analysis, a position system (when you want to know where you books are (the syntax for which is "B##H#_". B for book, # are numbers, H for height (in you shelf) and at the end you can put a char for denoting the room you shelf is in. An example would be B01H3L)) and is generally quite lightweight. Just load in a CSV. You can also provide a .meta.csv file, with the same name as you CSV, which contains style information and things like that (I will provide an example). The App switches automatically between Englisch and German, as well as light and dark mode, based on system settings.


The app is built using PySimpleGUI 6, which intern uses tkinter, so you can basically run it anywhere. I have tested it on Linux Ubuntu 24, Windows 10 and 11, Python 3.13.3 and 3.14.6, but I see no reason it shouldn't work in other versions. 

If you want to run it, the dependencies are:
- numpy
- PySimpleGUI
- darkdetect

```
pip install numpy
pip install PySimpleGUI
pip install darkdetect
```
If you clone this repository, be sure to "cd" to it, as it wont work otherwise. If you run the .exe or Linux App, you don´t have to worry about that :)



Its probably not going to be maintained, but I don't know what should break. If something breaks, make an Issue, I'll probably respond to it.

PS: Don't look at the code, it's horrific.