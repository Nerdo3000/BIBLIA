"""
"BIBLIA - Book Index, Bibliography, & Literary Information Archive" / "BIBLIA - Buch-Index, Bibliografie, & Literarisches Informations-Archiv" version 1.0
Copyright (C) 2026  Nerdo3000

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import datetime
from style import *
start_time = None


def profiling_start():
    global start_time
    start_time = datetime.datetime.now()

def profiling_end(string=""):
    if DEBUG: print("Time Delta at "+string+": "+str(datetime.datetime.now()-start_time))