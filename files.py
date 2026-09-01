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
import numpy
import os
import sys
import csv
from style import *
import PIL.Image
import io
import base64

csv.register_dialect("excel-german",csv.excel,delimiter=";")

def export(array,name="",dialect="unix",encoding="utf-8"):
    try:os.remove(name)
    except FileNotFoundError:pass
    
    if dialect=="txt":
        with open(name,"x",encoding=encoding,newline='') as file:
            file.writelines(array)
            return

    with open(name,"x",encoding=encoding,newline='') as file:
        array = [x[1:] for x in array]
        writer = csv.writer(file, dialect=dialect)
        writer.writerows(array)

def re_index(my_data):
    my_data[:,0] = range(my_data.shape[0])
    return my_data

def index(my_data):
    if not my_data[0,0] == "Nr":
        my_data = numpy.insert(my_data,0,range(my_data.shape[0]),1)
        my_data[0,0] = "Nr"
        return my_data
    else:
        return re_index(my_data)

def import_csv(path,encoding="utf-8",dialect="unix",failsafe=[["Nr","Titel"],[1,"KEINE DATEN GELADEN"]],extract=None):
    if DEBUG: print(path)
    try:
        with open(path,"r",encoding=encoding,newline='') as file:
            reader = csv.reader(file, dialect=dialect)
            n = numpy.array(list(reader),dtype=numpy.dtypes.StringDType)
        if n.shape[0]<2 or n.shape[1]<2: return numpy.array(failsafe)
        if extract!=None: 
            n = n[:,extract]
        return n
    except FileNotFoundError:
        return numpy.array(failsafe)
    except ValueError as e:
        if DEBUG: print(e)
        return numpy.array(failsafe)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def file_exists(path): return os.path.isfile(path)

def from64(string):
    try:
        img = PIL.Image.open(io.BytesIO(base64.b64decode(string.encode('UTF-8'))))

        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    except (PIL.UnidentifiedImageError,OSError) as e:
        if DEBUG: print(e)
        return None

def to64(file_name):
    img = PIL.Image.open(file_name)
    
    img = img.resize((int(img.size[0]*512/img.size[1]), 512))
    bio = io.BytesIO()
    img.save(bio, 'webp', optimize = True, quality = 50)
    del img
    return base64.b64encode(bio.getvalue())

def resize_image(image, resize=None):
    if image==None: return None
    try:
        img = PIL.Image.open(io.BytesIO(base64.b64decode(image)))
    except Exception as e:
        data_bytes_io = io.BytesIO(image)
        img = PIL.Image.open(data_bytes_io)

    if resize:
        scale = min(resize[1]/img.size[1], resize[0]/img.size[0])
        try:
            img = img.resize((int(img.size[0]*scale), int(img.size[1]*scale)), resample=PIL.Image.LANCZOS)
        except ValueError: return None
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()
