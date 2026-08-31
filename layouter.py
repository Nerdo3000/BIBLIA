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
import PySimpleGUI_Mod as sg
import re
from style import *
import files
import numpy
import language as lang

key_counter = 0

def convert_text_bool(string):
    if string.lower()=="true": return True
    elif string.lower()=="false": return False
    else: return None

class Layout:
    def __init__(self, table_header, GLOBAL_SAVE_FILE):
        table_header = table_header[0].tolist()

        self.meta_data_raw = files.import_csv(GLOBAL_SAVE_FILE.removesuffix(".csv")+".meta.csv",failsafe=[])
        try:
            if not self.meta_data_raw[0,0] == "Nr":
                self.meta_data_raw = numpy.insert(self.meta_data_raw,0,["Nr","none","true","Nr","0","9","","r"],1)
        except IndexError:
            pass
        if DEBUG: print(self.meta_data_raw.shape)
        if self.meta_data_raw.shape != (8, len(table_header)):
            if self.meta_data_raw.shape[0]==8:
                new_data = numpy.full((8,len(table_header)),"",object)
                if self.meta_data_raw.shape[1]>len(table_header):
                    if DEBUG: print(new_data.shape)
                    if DEBUG: print(self.meta_data_raw[:,:len(table_header)].shape)
                    new_data[:,:] = self.meta_data_raw[:,:len(table_header)]
                else:
                    col_idx = self.meta_data_raw.shape[1]
                    new_data[:,:col_idx] = self.meta_data_raw[:,:col_idx]
                    for i in range(len(table_header)-self.meta_data_raw.shape[1]):
                        col_idx = len(table_header)-1-i
                        name = table_header[col_idx]
                        new_data[:,col_idx] = [name,"medium","true",name,name,10,10,""]
                    if DEBUG: print(new_data)
                self.meta_data_raw = new_data
            else:
                self.meta_data_raw = numpy.full((8,len(table_header)),"",object)
                self.meta_data_raw[1].fill("medium")
                self.meta_data_raw[1,0] = "none"
                self.meta_data_raw[2].fill("true")
                self.meta_data_raw[3,:] = table_header
                self.meta_data_raw[4].fill(10)
                self.meta_data_raw[4,0] = 0
                self.meta_data_raw[5].fill(10)
                self.meta_data_raw[5,0] = 9
                self.meta_data_raw[7].fill("r")
        
        self.meta_data_raw[0,:] = table_header

        self.meta_data_dict = {val: idx for idx, val in enumerate(self.meta_data_raw[0].tolist())}  

        self.key_list = []
        self.search_key_list = []
        
        self.display_length = []
        self.skip_math = []

        self.lock_complex = []

        self.col_widths = []
        self.col_widths_alt = []
        self.col_names = []
        self.col_names_alt = []
        self.col_just = []

        self.search_buttons = []

        self.combo_elements = []
        self.images = []
        self.search_normal = []

        self.combo_elements_search = []

        self.treat_as_date = []
        self.treat_as_pos = None

        for key in table_header:
            key_name = re.sub("[^0-9a-zA-Z]", "",key)
            key_name = "-"+key_name.lower()+"-"
            self.key_list.append(key_name)
            self.search_key_list.append("SEARCH"+key_name)
            self.search_buttons.append("!CLEARSEARCH"+key_name)

            idx = self.meta_data_dict[key]

            displ = self.meta_data_raw[1,idx]
            self.display_length.append(str(displ))
            if displ=="long": 
                self.lock_complex.append(key_name)
                self.combo_elements.append(key_name+"ADD_ENTRY")
                self.combo_elements_search.append("SEARCH"+key_name)
            elif displ=="none": pass
            elif displ=="big":
                self.lock_complex.append(key_name)
            elif displ=="medium":
                self.combo_elements.append(key_name)
                self.combo_elements_search.append("SEARCH"+key_name)
            elif displ=="short":
                self.combo_elements.append(key_name)
                self.combo_elements_search.append("SEARCH"+key_name)
            elif displ=="image":
                self.images.append(key_name)

            if convert_text_bool(self.meta_data_raw[2,idx]):
                self.skip_math.append(idx)

            self.col_names.append(str(self.meta_data_raw[3,idx]))
            self.col_widths.append(int(self.meta_data_raw[4,idx]))
            self.col_widths_alt.append(int(self.meta_data_raw[5,idx]))
            if str(self.meta_data_raw[6,idx])=="pos":
                self.treat_as_pos = idx
            elif str(self.meta_data_raw[6,idx])=="date":
                self.treat_as_date.append(idx)
            self.col_just.append(self.meta_data_raw[7,idx])

        self.col_names_alt = self.col_names
        self.col_names_alt[0] = lang.ANALYSIS_ANALYSIS

    def make_layouts(self):
        layout_left_column = []
        layout_right_column = []
        layout_left_column_search = []
        layout_right_column_search = []
        layout_right_column_r = []
        layout_right_column_l = []
        layout_right_column_r_search = []
        layout_right_column_l_search = []
        layout_right_column_center = []

        for head in self.meta_data_raw[0].tolist():
            key_idx=self.meta_data_dict[head]
            head_name = head+":"
            if self.display_length[key_idx]=="none": continue
            elif self.display_length[key_idx]=="long":
                layout_left_column.append([sg.Text(head_name,justification="center",expand_x=True,pad=(0,15))])
                layout_left_column.append([sg.Multiline(size=(40,3),expand_x=True,right_click_menu=make_right_click_menu(self.key_list[key_idx]),expand_y=True,key=self.key_list[key_idx],enable_events=True,pad=(0,0))])
                layout_left_column.append([sg.Column([[sg.Input(key=self.key_list[key_idx]+"ADD_ENTRY",right_click_menu=make_right_click_menu(self.key_list[key_idx]+"ADD_ENTRY"),use_readonly_for_disable=True,disabled_readonly_background_color=THIRD_COLOR(sg.theme()),metadata=0,expand_x=True,enable_events=True,expand_y=True,pad=0),sg.Button(lang.LAYOUTER_ADD_ENTRY,pad=0,key=self.key_list[key_idx]+"ADD_ENTRY AUTO_COMBO ENTER")]],expand_x=True,expand_y=False,pad=(0,(0,15)))])

                #layout_left_column_search.append([sg.Text(head_name,justification="center",expand_x=True,pad=(0,25))])
                #layout_left_column_search.append([sg.Multiline(size=(40,4),expand_x=True,expand_y=True,key=self.search_key_list[key_idx],enable_events=True,pad=(0,10),tooltip=lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING0+head+lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING2),sg.Button("X",key="!CLEAR"+self.search_key_list[key_idx],border_width=0,button_color=(OTHER_BUTTON(sg.theme()),sg.theme_background_color()),pad=0,auto_size_button=False,size=(1,1),tooltip=lang.LAYOUTER_CLEAR)])
                layout_left_column_search.append([sg.Column([[sg.Text(head_name,size=(20,1)),sg.Input(key=self.search_key_list[key_idx],right_click_menu=make_right_click_menu(self.search_key_list[key_idx]),disabled_readonly_background_color=THIRD_COLOR(sg.theme()),use_readonly_for_disable=True,size=(30,1),expand_x=True,enable_events=True,tooltip=lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING0+head+lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING2),sg.Button("X",key="!CLEAR"+self.search_key_list[key_idx],border_width=0,button_color=(OTHER_BUTTON(sg.theme()),sg.theme_background_color()),pad=0,auto_size_button=False,size=(1,1),tooltip=lang.LAYOUTER_CLEAR)]],expand_x=True,pad=(0,10))])
            elif self.display_length[key_idx]=="big":
                layout_left_column.append([sg.Text(head_name,justification="center",expand_x=True,pad=(0,15))])
                layout_left_column.append([sg.Multiline(size=(40,3),right_click_menu=make_right_click_menu(self.key_list[key_idx]),expand_x=True,expand_y=True,key=self.key_list[key_idx],enable_events=True,pad=(0,0))])

                layout_left_column_search.append([sg.Column([[sg.Text(head_name,size=(20,1)),sg.Input(key=self.search_key_list[key_idx],right_click_menu=make_right_click_menu(self.search_key_list[key_idx]),disabled_readonly_background_color=THIRD_COLOR(sg.theme()),use_readonly_for_disable=True,size=(30,1),expand_x=True,enable_events=True,tooltip=lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING0+head+lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING2),sg.Button("X",key="!CLEAR"+self.search_key_list[key_idx],border_width=0,button_color=(OTHER_BUTTON(sg.theme()),sg.theme_background_color()),pad=0,auto_size_button=False,size=(1,1),tooltip=lang.LAYOUTER_CLEAR)]],expand_x=True,pad=(0,10))])
            elif self.display_length[key_idx]=="medium":
                layout_left_column.append([sg.Column([[sg.Text(head_name,size=(20,1)),sg.Input([],right_click_menu=make_right_click_menu(self.key_list[key_idx]),key=self.key_list[key_idx],disabled_readonly_background_color=THIRD_COLOR(sg.theme()),use_readonly_for_disable=True,metadata=0,size=(30,1),expand_x=True,enable_events=True)]],expand_x=True,pad=(0,10))])
                layout_left_column_search.append([sg.Column([[sg.Text(head_name,size=(20,1)),sg.Input(key=self.search_key_list[key_idx],right_click_menu=make_right_click_menu(self.search_key_list[key_idx]),disabled_readonly_background_color=THIRD_COLOR(sg.theme()),use_readonly_for_disable=True,size=(30,1),expand_x=True,enable_events=True,tooltip=lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING0+head+lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING2),sg.Button("X",key="!CLEAR"+self.search_key_list[key_idx],border_width=0,button_color=(OTHER_BUTTON(sg.theme()),sg.theme_background_color()),pad=0,auto_size_button=False,size=(1,1),tooltip=lang.LAYOUTER_CLEAR)]],expand_x=True,pad=(0,10))])
                
            elif self.display_length[key_idx]=="short":
                layout_right_column_l.append([sg.Text(head_name,size=(15,1),pad=(0,10))])
                layout_right_column_l_search.append([sg.Text(head_name,size=(15,1),pad=(0,10))])

                layout_right_column_r.append([sg.Input([],key=self.key_list[key_idx],right_click_menu=make_right_click_menu(self.key_list[key_idx]),use_readonly_for_disable=True,disabled_readonly_background_color=THIRD_COLOR(sg.theme()),metadata=0,enable_events=True,size=(10,1),pad=(0,10),expand_x=True)])
                layout_right_column_r_search.append([sg.Input(key=self.search_key_list[key_idx],right_click_menu=make_right_click_menu(self.search_key_list[key_idx]),use_readonly_for_disable=True,disabled_readonly_background_color=THIRD_COLOR(sg.theme()),size=(10,1),pad=(0,10),enable_events=True,expand_x=True,tooltip=lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING0+head+lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING2),sg.Button("X",key="!CLEAR"+self.search_key_list[key_idx],border_width=0,button_color=(OTHER_BUTTON(sg.theme()),sg.theme_background_color()),pad=0,auto_size_button=False,size=(1,1),tooltip=lang.LAYOUTER_CLEAR)])
            elif self.display_length[key_idx]=="image":
                layout_right_column_center.append([
                    sg.Frame(
                        head_name,
                        [
                            [sg.Image(expand_x=True,key=self.key_list[key_idx],expand_y=True,data=ICON,subsample=1,pad=0)],
                            [sg.Column([[sg.Button(lang.ADD_IMAGE, key=self.key_list[key_idx]+" ADD IMAGE"),sg.Button(lang.CLEAR_IMAGE, key=self.key_list[key_idx]+" CLEAR IMAGE")]],expand_x=True,vertical_alignment="bottom",element_justification="center")]
                        ],
                        expand_x=True,title_location=sg.TITLE_LOCATION_TOP,border_width=7,relief=sg.RELIEF_RIDGE,pad=5,size=(50, 50),expand_y=True)])

                layout_right_column_l_search.append([sg.Text(head_name,size=(15,1),pad=(0,10))])
                layout_right_column_r_search.append([sg.Input(key=self.search_key_list[key_idx],right_click_menu=make_right_click_menu(self.search_key_list[key_idx]),use_readonly_for_disable=True,disabled_readonly_background_color=THIRD_COLOR(sg.theme()),size=(10,1),pad=(0,10),enable_events=True,expand_x=True,tooltip=lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING0+head+lang.LAYOUTER_TOOLTIP_SEARCH_SUBSTRING2),sg.Button("X",key="!CLEAR"+self.search_key_list[key_idx],border_width=0,button_color=(OTHER_BUTTON(sg.theme()),sg.theme_background_color()),pad=0,auto_size_button=False,size=(1,1),tooltip=lang.LAYOUTER_CLEAR)])

        layout_right_column = sg.Column([[
                sg.Column(layout_right_column_l,expand_x=True),  
                sg.Column(layout_right_column_r,expand_x=True)],[sg.Column(layout_right_column_center,expand_x=True,expand_y=True)]],expand_y=True,pad=(0,0),element_justification="left",expand_x=True)
        layout_right_column_search = sg.Column([[
                            sg.Column(layout_right_column_l_search,expand_x=True),  
                            sg.Column(layout_right_column_r_search,expand_x=True)]],expand_y=True,pad=(0,0),element_justification="left",expand_x=True)

        layout_left_column = sg.Column(layout_left_column,expand_y=True,pad=(50,0),element_justification="left",expand_x=True)
        layout_left_column_search = sg.Column(layout_left_column_search,expand_y=True,pad=(50,0),element_justification="left",expand_x=True)

        self.layout_left_column = layout_left_column

        return layout_left_column, layout_left_column_search, layout_right_column, layout_right_column_search

    def bind_all(self, window):
        for key in self.combo_elements:
            window[key].bind("<Key>", " AUTO_COMBO KEY_PRESS")
            window[key].bind("<Button-1>", " AUTO_COMBO KEY_PRESS")
            window[key].bind("<FocusOut>", " AUTO_COMBO UNFOCUS")
            window[key].bind("<Key-Down>"," AUTO_COMBO SELECT_DOWN")
            window[key].bind("<Key-Return>"," AUTO_COMBO ENTER")
            window[key].bind("<Key-Up>"," AUTO_COMBO SELECT_UP")
        for key in self.combo_elements_search:
            window[key].bind("<Key>", " AUTO_COMBO KEY_PRESS")
            window[key].bind("<Button-1>", " AUTO_COMBO KEY_PRESS")
            window[key].bind("<FocusOut>", " AUTO_COMBO UNFOCUS")
            window[key].bind("<Key-Down>"," AUTO_COMBO SELECT_DOWN")
            window[key].bind("<Key-Return>"," AUTO_COMBO ENTER")
            window[key].bind("<Key-Up>"," AUTO_COMBO SELECT_UP")

def make_right_click_menu(key_name):
    #sg.clipboard_get
    return ["", [lang.MENU_RIGHT_CLICK_CUT+"::"+key_name, lang.MENU_RIGHT_CLICK_COPY+"::"+key_name, lang.MENU_RIGHT_CLICK_PASTE+"::"+key_name, lang.BIBLIA_APP_CANCEL]]

def make_layout_standort(pos_strip):
    global key_counter
    different_pos = set(pos_strip)
    different_pos_l = list(set([n[0:3] if (re.search(r"B\d\d\w\d\w",n) or re.search(r"B\d\d\w\d\d\w",n)) else None for n in different_pos]))
    try: different_pos_l.remove(None)
    except ValueError: pass
    different_pos_l.sort()
    different_pos = list(different_pos)
    different_pos.sort(reverse=True)
    list_of_b = []
    key_counter += 1

    b_list = []
    else_list = []

    for pos in different_pos:
        if re.search(r"B\d+\w\d+\w",pos):
            b_list.append(pos)
        else:
            else_list.append(pos)

    r_list = list(set([n[5] for n in b_list]))
    r_list.sort()

    if DEBUG: print(r_list)

    if DEBUG: print(different_pos_l)

    
    sort_matrix = numpy.frompyfunc(lambda x:[],1,1)(numpy.zeros((len(r_list),len(different_pos_l))))  

    for pos in b_list:
        y = r_list.index(pos[5])
        x = different_pos_l.index(pos[0:3])
        sort_matrix[y,x].append(pos)

    sort_matrix = numpy.rot90(sort_matrix,3)

    if DEBUG:print(sort_matrix)
    
    add_pad = 0
    for row in sort_matrix[:]:
        for i in range(len(row)):
            if row[i]!=[]:
                s_list = []
                s_list.append([sg.Button(str(row[i][0][0:3]),key="GETSTANDORT---"+str(row[i][0][0:3])+"---"+str(key_counter),pad=0,font=FONT_BIG,expand_y=False,tooltip=lang.LAYOUTER_TOOLTIP_POS_SUBSTRING0+different_pos_l[i]+lang.LAYOUTER_TOOLTIP_POS_SUBSTRING2)])
                for s_pos in row[i]:
                    s_list.append([sg.Button(s_pos,key="GETSTANDORT---"+s_pos+"---"+str(key_counter),pad=0,font=FONT_BIG,expand_y=True,tooltip=lang.LAYOUTER_TOOLTIP_POS_SUBSTRING0+s_pos+lang.LAYOUTER_TOOLTIP_POS_SUBSTRING2)])
                list_of_b.append(sg.Column(s_list,vertical_alignment="top",pad=((25+add_pad,25),50),expand_y=True,element_justification="center"))
                add_pad = 0

                if DEBUG: print(different_pos_l[i],row[i])
        add_pad = 75

    list_of_non_b = [sg.Sizer(0,FONT_BIG[1]*10)]
    else_list.reverse()
    for pos in else_list:
        list_of_non_b.append(sg.Column([[sg.Button(pos,key="GETSTANDORT---"+pos+"---"+str(key_counter),pad=(25,50),font=FONT_BIG,auto_size_button=True,expand_y=True,tooltip=lang.LAYOUTER_TOOLTIP_POS_SUBSTRING0+pos+lang.LAYOUTER_TOOLTIP_POS_SUBSTRING2)]],vertical_alignment="top",element_justification="center",expand_y=True))

    s = [[sg.pin(sg.Column([list_of_non_b,list_of_b],key="ALL_STANDORTE"+str(key_counter),expand_x=True,expand_y=True,vertical_alignment="t",pad=0,scrollable=True),expand_x=False,expand_y=False,vertical_alignment="t")]]
    return s