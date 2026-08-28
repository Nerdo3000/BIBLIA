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
try:
    import PySimpleGUI_Mod as sg
    import numpy
    import darkdetect
    import time

    import language as lang

    sg.theme_add_new("NOT_Dark",{"BACKGROUND": "#ffffff", "TEXT": "#000000", "INPUT": "#d3d3d3", "TEXT_INPUT": "#000000", "SCROLL": "#c2c2c2", "BUTTON": ("#FFFFFF", "#004F00"),
             "PROGRESS": sg.DEFAULT_PROGRESS_BAR_COMPUTE, "BORDER": 1, "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0})
    if darkdetect.isDark(): sg.theme("Dark")
    else: sg.theme("NOT_Dark")
    from os import remove
    import re
    import profiler

    sg.set_options(suppress_key_guessing=True,suppress_error_popups=True)

    GLOBAL_EMPTY_OVERRIDE = False
    GLOBAL_SEARCH = False
    GLOBAL_SAVE_FILE = ""
    from style import *

    def convert_date_front(string):
        if len(string) != 10:
            return "0000.00.00"
        j = string[-4:]
        m = string[3:5]
        d = string[0:2]
        return j + "." + m + "." + d

    def convert_date_back(string):
        if len(string) != 10:
            return "00.00.0000"
        j = string[0:4]
        m = string[5:7]
        d = string[8:10]
        return d + "." + m + "." + j

    def get_IDX():
        return convert_to_IDX(get_IDX_input())

    def convert_to_IDX(i):
        try:
            return int(table_data[i, 0])
        except ValueError:
            return 1

    def set_IDX(n):
        close_auto_box()
        if n < 1:
            n = 1
        if n > data_len():
            n = data_len()
        window["-IDX-"].update(n)
        try:
            window["TABLE"].update(select_rows=[n - 1])
            window.read(0)
        except sg.tkinter.TclError:
            pass

    def get_IDX_input():
        if window["-IDX-"].get()=="": return 1
        else: 
            try:
                return int(window["-IDX-"].get())
            except ValueError:
                return 1

    def data_len():
        return table_data.shape[0] - 1

    def lock_search(state):
        for key_name in Layouter.combo_elements_search:
            window[key_name].update(readonly=state)

        for key_name in Layouter.search_buttons[1:]:
            window[key_name].update(disabled=state)

    def lock_input(state):
        for key_name in Layouter.combo_elements:
            window[key_name].update(disabled=state)

        for key_name in Layouter.lock_complex:
            window[key_name].update(disabled=state)
            if state:
                window[key_name].Widget.config(bg=THIRD_COLOR(sg.theme()))
            else:
                window[key_name].Widget.config(bg=sg.theme_input_background_color())
            window[key_name + "ADD_ENTRY AUTO_COMBO ENTER"].update(disabled=state)
        lock_misc(state)

    def lock_misc(state):
        window["TABLE"].enable_cell_editing = not state
        window["-EINTRAG_LÖSCHEN-"].update(disabled=state)
        window["-ALLE_LÖSCHEN-"].update(disabled=state)

    def matches_parameter(string, parameter):
        try:
            if re.search(parameter, string, re.IGNORECASE * window["-BIGSMALL?-"].get()) == None:
                return False
        except re.PatternError:
            return False
        return True

    def remove_regex(string):
        return string.replace("?",r"\?").replace(".",r"\.").replace("+",r"\+").replace("*",r"\*").replace("(",r"\(").replace(")",r"\)").replace("[",r"\[").replace("]",r"\]").replace("\\\\","\\")

    def search():
        global table_data, GLOBAL_EMPTY_OVERRIDE, GLOBAL_SEARCH
        parameters = []
        values = []
        for i in range(1, len(Layouter.search_key_list)):
            if window[Layouter.search_key_list[i]].get() != "":
                parameters.append(i)
                values.append(window[Layouter.search_key_list[i]].get())
        table_data = []
        if DEBUG: print("Search parameters: "+str(len(parameters)))
        if len(parameters) == 0:
            GLOBAL_SEARCH = False
            window["-NEW-"].update(disabled=False)
            table_data = my_data
        else:
            GLOBAL_SEARCH = True
            window["-NEW-"].update(disabled=True)
            table_data.append(my_data[0])

            values = [x if (window["-REGEX?-"].get()) else remove_regex(str(x)) for x in values]

            for line in my_data[1:]:
                if window["-ALL_OR_ANY?-"].get():
                    truths = True
                    for i in range(len(parameters)):
                        if not matches_parameter(line[parameters[i]], values[i]):
                            truths = False
                            break
                else:
                    truths = False
                    for i in range(len(parameters)):
                        if matches_parameter(line[parameters[i]], values[i]):
                            truths = True
                            break
                if truths:
                    table_data.append(line)
        if len(table_data) == 1:
            if DEBUG: print("UH OH")
            n = numpy.empty_like(my_data[0])
            n[:] = numpy.nan
            table_data.append(n)
            table_data = numpy.array(table_data)
            window["LEN"].update("von 0")
            set_IDX(0)
            GLOBAL_EMPTY_OVERRIDE = True
            lock_input(True)
            window["-EDITABLE?-"].update(disabled=True, value=True)
            window["-IDX_L-"].update(disabled=True)
            window["-IDX_FRONT-"].update(disabled=True)
            window["-IDX_R-"].update(disabled=True)
            window["-IDX_BACK-"].update(disabled=True)
        else:
            GLOBAL_EMPTY_OVERRIDE = False
            window["-EDITABLE?-"].update(disabled=False)
            window["-IDX_L-"].update(disabled=False)
            window["-IDX_FRONT-"].update(disabled=False)
            window["-IDX_R-"].update(disabled=False)
            window["-IDX_BACK-"].update(disabled=False)
            table_data = numpy.array(table_data)
            window["LEN"].update("von " + str(data_len()))
            set_IDX(1)
        load_book(get_IDX())

    def convert_to_float_if_possible(a):
        try:
            return float(a)
        except ValueError:
            if a == "":
                return 0
            else:
                return 0

    def calc_analysis():
        list_sum = []
        list_mid = []
        list_com = []
        list_art = []
        list_min = []
        list_max = []
        for i in range(0,table_data.shape[1]):
            table_data_column = table_data[1:, i].tolist()
            if i in Layouter.treat_as_date:
                sorted_list = [convert_date_front(x) for x in (table_data_column)]
                sorted_list.sort()
                list_min.append(convert_date_back(sorted_list[0]))
                list_max.append(convert_date_back(sorted_list[-1]))
                list_mid.append(convert_date_back(sorted_list[data_len() // 2]))
            else:
                table_data_column.sort()
                sorted_list = table_data_column
                if i in Layouter.skip_math:
                    list_min.append("")
                    list_max.append("")
                    list_mid.append("")
                else:
                    list_min.append(min(sorted_list))
                    list_max.append(max(sorted_list))
                    sorted_list.sort(key=convert_to_float_if_possible)
                    list_mid.append(sorted_list[data_len() // 2])
            list_com.append(max(set(table_data_column), key=table_data_column.count))
            if i in Layouter.skip_math:
                list_sum.append("")
                list_art.append("")
                continue
            su = 0  # Sum
            for n in table_data_column:
                try:
                    su += float(n)
                except (TypeError, ValueError):
                    pass
            if su == 0:
                list_sum.append("")
                list_art.append("")
            else:
                list_sum.append(round(su, 2))
                list_art.append(round(su / data_len(), 2))
        if table_data.shape[1] - 1 != 0:
            l = []
            list_sum[0] = lang.ANALYSIS_SUM
            list_art[0] = lang.ANALYSIS_ARITH
            list_mid[0] = lang.ANALYSIS_MEDIAN
            list_min[0] = lang.ANALYSIS_MIN
            list_max[0] = lang.ANALYSIS_MAX
            list_com[0] = lang.ANALYSIS_MOD
            l.append(list_sum)
            l.append(list_art)
            l.append(list_mid)
            l.append(list_min)
            l.append(list_max)
            l.append(list_com)
            window["TABLE_STATS"].update(l)

    def load_book(idx):
        if GLOBAL_EMPTY_OVERRIDE:
            for key_name in Layouter.key_list[1:]:
                window[key_name].update(lang.NO_DATA_FOUND)
        else:
            try:
                for i in range(1, len(Layouter.key_list)):
                    window[Layouter.key_list[i]].update(str(my_data[idx, i]).replace("|", "\n"))
            except (IndexError, ValueError) as e:
                if DEBUG: print(e)

    def write_book_key(idx, key):
        global my_data
        my_data[idx, Layouter.key_list.index(key)] = str(window[key].get()).replace("\n", "|")

    def get_key(string):
        return string + str(layouter.key_counter)

    def simple_search_update():
        global prev_simple_search 
        prev_simple_search = window["-SIMPLE_SEARCH-"].get()
        if window["-SIMPLE_SEARCH-"].get() == "":
            lock_search(False)
            window["-ALL_OR_ANY?-"].update(True, disabled=False)
        else:
            lock_search(True)
            window["-ALL_OR_ANY?-"].update(False, disabled=True)
        sdfsdfsdf = window["-SIMPLE_SEARCH-"].get()
        for key_name in Layouter.key_list[1:]:
            window["SEARCH" + key_name].update(sdfsdfsdf)
        search()

    def clear_all_filters():
        for key_name in Layouter.key_list[1:]:
            window["SEARCH" + key_name].update("")
        window["-SIMPLE_SEARCH-"].update("")
        lock_search(False)
        window["-ALL_OR_ANY?-"].update(disabled=False)
        search()

    def update_hashes():
        global hash_val_STANDORT, hash_val_ANALYSE
        # hash_val_STANDORT = None
        hash_val_ANALYSE = None

    def menu_lock(state):
        global GLOBAL_EMPTY_OVERRIDE
        GLOBAL_EMPTY_OVERRIDE = state
        lock_search(state)
        window["-EDITABLE?-"].update(disabled=state, value=True)
        window["-IDX_L-"].update(disabled=state)
        window["-IDX_FRONT-"].update(disabled=state)
        window["-IDX_R-"].update(disabled=state)
        window["-IDX_BACK-"].update(disabled=state)
        window["-NEW-"].update(disabled=state)
        window["-CLEAR-"].update(disabled=state)
        window["-ALL_OR_ANY?-"].update(disabled=state)
        window["-REGEX?-"].update(disabled=state)
        window["-BIGSMALL?-"].update(disabled=state)
        window["-ALL_STANDORTE-"].update(disabled=state)
        window["-SIMPLE_SEARCH-"].update(disabled=state)
        window["!CLEAR-SIMPLE_SEARCH-"].update(disabled=state)
        window["-IDX-"].update(disabled=state)

    def close_auto_box():
        try:
            auto_window.close()
        except NameError:
            pass

    def dialog_open(filetypes,init_dir):
        if sg.running_mac():
            # Workaround for the "*.*" issue on Mac
            is_all = [(x, y) for (x, y) in filetypes if all(ch in "* ." for ch in y)]
            if not len(set(filetypes)) > 1 and (len(is_all) != 0 or filetypes == (("ALL Files", "*.* *"))):
                file_name = sg.tk.filedialog.askopenfilename(initialdir=init_dir)
            else:
                file_name = sg.tk.filedialog.askopenfilename(initialdir=init_dir, filetypes=filetypes)  # show the 'get file' dialog box
        else:
            file_name = sg.tk.filedialog.askopenfilename(filetypes=filetypes, initialdir=init_dir)  # show the 'get file' dialog box
        return file_name

    def dialog_save(filetypes,init_dir,default_extension,initialfile=None):
        # show the 'get file' dialog box
        if sg.running_mac():
            # Workaround for the "*.*" issue on Mac
            is_all = [(x, y) for (x, y) in filetypes if all(ch in '* .' for ch in y)]
            if not len(set(filetypes)) > 1 and (len(is_all) != 0 or filetypes == sg.FILE_TYPES_ALL_FILES):
                file_name = sg.tk.filedialog.asksaveasfilename(defaultextension=default_extension, initialdir=init_dir,initialfile=initialfile)
            else:
                file_name = sg.tk.filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=default_extension, initialdir=init_dir,initialfile=initialfile)
        else:
            file_name = sg.tk.filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=default_extension, initialdir=init_dir,initialfile=initialfile)
        return file_name

    def update_analysis():
        global hash_val_ANALYSE
        profiler.profiling_end("Before update analysis")
        if hash(table_data.tobytes()) != hash_val_ANALYSE:
            if DEBUG: print("Changed hash")
            window["TABLE"].update(select_rows=[get_IDX_input()-1])
            window["TABLE"].update(table_data[1:].tolist())
            hash_val_ANALYSE = hash(table_data.tobytes())
            calc_analysis()
        profiler.profiling_end("After update analysis")
    import files
    import layouter

    def new_main_window():
        global window, table_data, my_data, hash_val_ANALYSE, hash_val_STANDORT, Layouter, GLOBAL_EMPTY_OVERRIDE, GLOBAL_SEARCH, prev_selected_auto, prev_button, prev_simple_search
        GLOBAL_EMPTY_OVERRIDE = False
        GLOBAL_SEARCH = False
        my_data = files.index(my_data)
        table_data = my_data
        prev_selected_auto = prev_button = prev_simple_search = None

        Layouter = layouter.Layout(my_data, GLOBAL_SAVE_FILE)

        layout_left_column, layout_left_column_search, layout_right_column, layout_right_column_search = Layouter.make_layouts()

        layout_right_column_search_bottom = sg.Column(
            [
                [sg.Checkbox(lang.BIG_SMALL, default=True, key="-BIGSMALL?-", enable_events=True, tooltip=lang.TOOLTIP_BIG_SMALL)],
                [sg.Checkbox(lang.ALL_OR_ANY, default=True, key="-ALL_OR_ANY?-", enable_events=True, tooltip=lang.TOOLTIP_ALL_OR_ANY)],
                [sg.Checkbox(lang.REGEX_ACTIVE, default=False, key="-REGEX?-", enable_events=True, tooltip=lang.TOOLTIP_REGEX_ACTIVE)],
            ],
            vertical_alignment="bottom",
        )
        layout_right_column_search = sg.Column([[layout_right_column_search], [layout_right_column_search_bottom]], expand_y=True, pad=(50, 0), element_justification="left", expand_x=True)

        layout_right_column_bottom = sg.Column(
            [[sg.Button(lang.DELETE_SINGLE, key="-EINTRAG_LÖSCHEN-",tooltip=lang.TOOLTIP_DELETE_SINGLE)], [sg.Button(lang.DELETE_SELECTION, key="-ALLE_LÖSCHEN-",tooltip=lang.TOOLTIP_DELETE_SELECTION)]], vertical_alignment="bottom", expand_x=True
        )
        layout_right_column = sg.Column([[layout_right_column], [layout_right_column_bottom]], expand_y=True, pad=(50, 0), element_justification="left", expand_x=True)

        tab_buch = [
            [sg.Text(lang.TAB_ENTRIES, font=FONT_BOLD)],
            [sg.Column([[layout_left_column, sg.VerticalSeparator(), layout_right_column]], expand_y=True, expand_x=True, element_justification="center")],
        ]
        tab_suche = [
            [sg.Text(lang.TAB_SEARCH, font=FONT_BOLD), sg.Button(lang.CLEAR_SEARCH_FILTER, key="-CLEAR-",tooltip=lang.TOOLTIP_CLEAR_SEARCH_FILTER)],
            [sg.Column([[layout_left_column_search, sg.VerticalSeparator(), layout_right_column_search]], expand_y=True, expand_x=True, element_justification="center")],
        ]
        tab_analyse = [
            [sg.Text(lang.TAB_ANALYSIS, font=FONT_BOLD)],
            [
                sg.Column(
                    [
                        [
                            sg.Table(
                                my_data[1:].tolist(),
                                Layouter.col_names,
                                col_widths=Layouter.col_widths,
                                auto_size_columns=False,
                                vertical_scroll_only=False,
                                key="TABLE",
                                enable_cell_editing=True,
                                alternating_row_color=THIRD_COLOR(sg.theme()),
                                num_rows=10,
                                expand_y=True,
                                enable_events=True,
                                select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                cols_justification = Layouter.col_just,
                                tooltip=lang.TOOLTIP_TABLE
                            )
                        ],
                        [sg.Text(lang.ANALYSIS_HEAD, pad=((0, 0), (25, 0)))],
                        [
                            sg.Table(
                                [],
                                Layouter.col_names_alt,
                                auto_size_columns=False,
                                col_widths=Layouter.col_widths_alt,
                                vertical_scroll_only=False,
                                key="TABLE_STATS",
                                alternating_row_color=THIRD_COLOR(sg.theme()),
                                num_rows=6,
                                select_mode=sg.TABLE_SELECT_MODE_NONE,
                                expand_x=True,
                                expand_y=False,
                                cols_justification = Layouter.col_just,
                                tooltip=lang.TOOLTIP_ANALYSIS_HEAD
                            )
                        ],
                    ],
                    element_justification="center",
                    expand_y=True,
                    pad=((0, 0), (0, 40)),
                )
            ],
        ]
        tab_schrank = [[sg.Text(lang.TAB_LOCATION, font=FONT_BOLD), sg.Button(lang.BUTTON_ALL_LOCATIONS, key="-ALL_STANDORTE-",tooltip=lang.TOOLTIP_BUTTON_ALL_LOCATIONS)]]

        menu_layout = [
            [
                lang.MENU_FILE,
                [
                    lang.MENU_OPEN,
                    lang.MENU_IMPORT,
                    [lang.MENU_IMPORT_EXCEL, lang.MENU_IMPORT_EXCEL_GERMAN],
                    "---",
                    lang.MENU_SAVE_MAIN,
                    lang.MENU_SAVE_AS,
                    "---",
                    lang.MENU_EXPORT_ALL,
                    ["Excel CSV (International)::-EXPORT-ALL-excel_global-", 
                     "Excel CSV ("+lang.MENU_GERMAN+")::-EXPORT-ALL-excel_german-",
                     "Text::)::-EXPORT-ALL-txt-"],
                    lang.MENU_EXPORT_SELECT,
                    ["Excel CSV (International)::-EXPORT-SELECT-excel_global-", 
                     "Excel CSV ("+lang.MENU_GERMAN+")::-EXPORT-SELECT-excel_german-",
                     "Text::-EXPORT-SELECT-txt-"],
                    lang.MENU_EXPORT_SINGLE,
                    ["Excel CSV (International)::-EXPORT-SINGLE-excel_global-", 
                     "Excel CSV ("+lang.MENU_GERMAN+")::-EXPORT-SINGLE-excel_german-",
                     "Text::-EXPORT-SINGLE-txt-"],
                    "---",
                    lang.MENU_CLOSE,
                ],
            ],
            [lang.MENU_ABOUT, ["Copyright::COPY", "Regex::HILFE", lang.MENU_LIBS, ["NumPy::COPYRIGHT", "PySimpleGUI::COPYRIGHT", "darkdetect::COPYRIGHT"]]],
        ]

        # Define the window's contents
        layout = [
            [
                sg.Column([[sg.MenubarCustom(menu_layout)]], expand_x=False),
                sg.Text(lang.ENTRY_NUMBER_TEXT),
                sg.Input(size=(5, 1), justification="right", key="-IDX-", enable_events=True, tooltip=lang.TOOLTIP_IDX),
                sg.Text("", key="LEN"),
                sg.Button("⟪", key="-IDX_FRONT-", tooltip=lang.TOOLTIP_IDX_FRONT),
                sg.Button("⟨", key="-IDX_L-", tooltip=lang.TOOLTIP_IDX_L),
                sg.Button("⟩", key="-IDX_R-", tooltip=lang.TOOLTIP_IDX_R),
                sg.Button("⟫", key="-IDX_BACK-", tooltip=lang.TOOLTIP_IDX_BACK),
                sg.Button(lang.NEW_ENTRY, key="-NEW-", tooltip=lang.TOOLTIP_NEW_ENTRY),
                sg.Checkbox(lang.EDITABLE, default=True, enable_events=True, key="-EDITABLE?-", pad=(20, 0), tooltip=lang.TOOLTIP_EDITABLE),
                sg.Column(
                    [
                        [
                            sg.Text(lang.SIMPLE_SEARCH),
                            sg.Input(key="-SIMPLE_SEARCH-", enable_events=True, size=(5, 1), expand_x=True, tooltip=lang.TOOLTIP_SIMPLE_SEARCH),
                            sg.Button("X", key="!CLEAR-SIMPLE_SEARCH-", border_width=0, button_color=(OTHER_BUTTON(sg.theme()),sg.theme_background_color()), pad=0, auto_size_button=False, size=(1, 1),tooltip=lang.TOOLTIP_CLEAR_SIMPLE_SEARCH),
                        ]
                    ],
                    element_justification="right",
                    expand_x=True,
                    pad=(0, 0),
                ),
            ],
            [
                sg.TabGroup(
                    [[sg.Tab(lang.TAB_ENTRIES, tab_buch, key="-TAB-BUCH-"), sg.Tab(lang.TAB_SEARCH, tab_suche), sg.Tab(lang.TAB_ANALYSIS, tab_analyse, key="ANALYSE"), sg.Tab(lang.TAB_LOCATION, tab_schrank, visible=(Layouter.treat_as_pos!=None), key="STANDORTE")]],
                    expand_y=True,
                    enable_events=True,
                    key="-TAB-",
                )
            ],
        ]

        # Create the window
        window = sg.Window(
            lang.BIBLIA_APP_NAME,
            layout,
            font=FONT,
            resizable=False,
            enable_close_attempted_event=True,
            return_keyboard_events=False,
            size=(1600, 1000),
            icon=ICON,
            finalize=True,
        )
        hash_val_ANALYSE = None
        hash_val_STANDORT = None
        # Display and interact with the Window using an Event Loop
        lock_input(window["-EDITABLE?-"].get())
        lock_input(window["-EDITABLE?-"].get())
        window.read(0)
        window["TABLE"].disable_edit_for_cells([(i, 0) for i in range(len(my_data[:]))])
        window["-IDX-"].update("1")
        window["LEN"].update("von " + str(data_len()))
        load_book(1)
        profiler.profiling_start()
        calc_analysis()

        window.set_resizable(True, True)

        window.bind("<Control-KeyPress-space>", "KEY-UNLOCK")
        window.bind("<Control-KeyPress-Left>", "-IDX_L-")
        window.bind("<Control-KeyPress-Right>", "-IDX_R-")
        window.bind("<Control-KeyPress-Up>", "-IDX_BACK-")
        window.bind("<Control-KeyPress-Down>", "-IDX_FRONT-")
        window.bind("<Configure>", "LOOSE FOCUS")

        Layouter.bind_all(window)

        window["-EINTRAG_LÖSCHEN-"].block_focus()
        window["-ALLE_LÖSCHEN-"].block_focus()

        if numpy.array_equal(my_data, (numpy.array([["Nr", "Titel"], [1, "KEINE DATEN GELADEN"]]))):
            menu_lock(True)
        else:
            menu_lock(False)

    #####################################################################################################################
    #-------------------------------------------------------------------------------------------------------------------#
    #####################################################################################################################

    file_name = False
    loop_con = False
    filetypes = [("Comma-separated values", ".csv")]
    init_dir = files.resource_path("./")
    file_name = dialog_open(filetypes,init_dir)

    if file_name:
        GLOBAL_SAVE_FILE = file_name
        my_data = files.import_csv(GLOBAL_SAVE_FILE)
        new_main_window()
        loop_con = True

    if loop_con:
        new_data = my_data.tolist()
        if DEBUG: print(GLOBAL_SAVE_FILE)
        files.export(new_data, name=GLOBAL_SAVE_FILE + "__AUTOSAVE.csv")
        window.timer_start(30000,key="AUTOSAVE")

    while loop_con:
        window_event, event, values = sg.read_all_windows(timeout=1000,timeout_key = "TIMEOUT")
        if DEBUG and window_event != None: print("-----------------------------------------------------------------------------------------------------------------------")
        if DEBUG and window_event != None: print(window_event, event, values)
        profiler.profiling_start()
        if event == "AUTOSAVE":
            new_data = my_data.tolist()
            if DEBUG: print(GLOBAL_SAVE_FILE)
            files.export(new_data, name=GLOBAL_SAVE_FILE + "__AUTOSAVE.csv")
        
        if prev_simple_search != window["-SIMPLE_SEARCH-"].get():
            simple_search_update()

        if window_event == None:
            continue

        if event == "LOOSE FOCUS":
            close_auto_box()
            if window["-TAB-"].get() == "ANALYSE":
                search()
                update_analysis()
                    
            elif window["-TAB-"].get() == "STANDORTE":
                if Layouter.treat_as_pos != None:
                    if hash(my_data[1:, Layouter.treat_as_pos].data.tobytes()) != hash_val_STANDORT:
                        hash_val_STANDORT = hash(my_data[1:, Layouter.treat_as_pos].data.tobytes())
                        if layouter.key_counter != 0:
                            window[get_key("ALL_STANDORTE")].update(visible=False)
                        window.extend_layout(window["STANDORTE"], layouter.make_layout_standort(my_data[1:, Layouter.treat_as_pos].tolist()))

        elif event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == lang.MENU_CLOSE or event == None:
            layoutPOP = [
                [sg.Text(lang.BIBLIA_APP_SAVE_QUESTION, justification="center", auto_size_text=True,expand_x=True)],
                [sg.Button(lang.BIBLIA_APP_SAVE, key="-SAVE-"), sg.Button(lang.BIBLIA_APP_NOT_SAVE, key="-CLOSE-"), sg.Button(lang.BIBLIA_APP_NOT_CLOSE, key="-BACK-")],
            ]
            windowPOP = sg.Window(lang.BIBLIA_APP_CLOSE, layoutPOP, font=FONT, finalize=True, icon=ICON)
            eventPOP, valuesPOP = windowPOP.read()
            if eventPOP == "-SAVE-":
                new_data = my_data.tolist()
                files.export(new_data, name=GLOBAL_SAVE_FILE)
                try:
                    remove(GLOBAL_SAVE_FILE + "__AUTOSAVE.csv")
                except FileNotFoundError:
                    pass
                windowPOP.close()
                break
            if eventPOP == "-BACK-":
                windowPOP.close()
            if eventPOP == "-CLOSE-":
                windowPOP.close()
                break
        elif event == "KEY-UNLOCK" and not GLOBAL_EMPTY_OVERRIDE:
            window["-EDITABLE?-"].update(value=not window["-EDITABLE?-"].get())
            lock_input(window["-EDITABLE?-"].get())
            close_auto_box()
        elif event == lang.MENU_OPEN:
            filetypes = [("Comma-separated values", ".csv")]
            init_dir = files.resource_path("./")
            file_name = dialog_open(filetypes,init_dir)

            if file_name:
                GLOBAL_SAVE_FILE = file_name
                window.close()
                my_data = files.import_csv(GLOBAL_SAVE_FILE)
                new_main_window()

        elif event == lang.MENU_SAVE_MAIN:
            new_data = my_data.tolist()
            if files.file_exists(GLOBAL_SAVE_FILE):
                files.export(new_data, name=GLOBAL_SAVE_FILE)
        elif event == lang.MENU_SAVE_AS:
            filetypes = [("Comma-separated values", ".csv")]
            init_dir = files.resource_path("./")
            default_extension = ".csv"
            file_name = dialog_save(filetypes,init_dir,default_extension)
            
            if file_name:
                new_data = my_data.tolist()
                files.export(new_data, name=file_name)
        elif event==lang.MENU_IMPORT_EXCEL:
            filetypes = [("Comma-separated values", ".csv")]
            init_dir = files.resource_path("./")
            file_name = dialog_open(filetypes,init_dir)
            
            if file_name:
                GLOBAL_SAVE_FILE = file_name
                window.close()
                my_data = files.import_csv(GLOBAL_SAVE_FILE,"utf-8-sig","excel")
                new_main_window()
        elif event==lang.MENU_IMPORT_EXCEL_GERMAN:
            filetypes = [("Comma-separated values", ".csv")]
            init_dir = files.resource_path("./")
            file_name = dialog_open(filetypes,init_dir)
                    
            if file_name:
                GLOBAL_SAVE_FILE = file_name
                window.close()
                my_data = files.import_csv(GLOBAL_SAVE_FILE,"utf-8-sig","excel-german")
                for row_idx in range(my_data.shape[0]):
                    for col_idx in range(my_data.shape[1]):
                        if re.search(r"^\d+,\d+$",str(my_data[row_idx,col_idx])):
                            my_data[row_idx,col_idx] = str(my_data[row_idx,col_idx]).replace(",",".")
                new_main_window()
        elif re.search("::-EXPORT-",event):
            if re.search("-ALL-", event): 
                new_data = my_data
            elif re.search("-SELECT-", event): 
                new_data = table_data
            elif re.search("-SINGLE-", event): 
                new_data = my_data[[0,get_IDX()]]
            else: 
                new_data = my_data 

            new_data = new_data.tolist()

            if re.search("-excel_global-", event): 
                dialect = "excel"
                filetypes = [("Excel Comma-separated values", ".csv")]
                default_extension = ".csv"

            elif re.search("-excel_german-", event): 
                dialect = "excel-german"
                filetypes = [("Excel Comma-separated values", ".csv")]
                default_extension = ".csv"

                for row_idx in range(len(new_data)):
                    for col_idx in range(len(new_data[row_idx])):
                        if re.search(r"^\d+\.\d+$",str(new_data[row_idx][col_idx])):
                            new_data[row_idx][col_idx] = str(new_data[row_idx][col_idx]).replace(".",",")
            elif re.search("-txt-", event): 
                dialect = "txt"
                filetypes = [("Text", ".txt")]
                default_extension = ".txt"

                temp = []
                if DEBUG: print(new_data)
                for row in new_data[1:]:
                    for i in range(len(row)):
                        temp.append(str(new_data[0][i])+": "+str(row[i])+"\n")
                    temp.append("-----------------------------\n")
                temp.pop()
                new_data = temp
            else: continue

            default_name = GLOBAL_SAVE_FILE.split("/")[-1].removesuffix(".csv")+"_export"+default_extension
            init_dir = files.resource_path("./")
            file_name = dialog_save(filetypes,init_dir,default_extension,default_name)

            if file_name:  
                files.export(new_data, name=file_name,dialect=dialect,encoding="utf-8-sig")

        elif event == "-EDITABLE?-" and not GLOBAL_EMPTY_OVERRIDE:
            window["-EDITABLE?-"].set_focus()
            lock_input(window["-EDITABLE?-"].get())
        elif event == "-IDX-":
            if get_IDX_input()!=1:
                set_IDX(get_IDX_input())
                load_book(get_IDX())
        elif event == "TABLE" and not GLOBAL_EMPTY_OVERRIDE:
            try:
                set_IDX(values["TABLE"][0] + 1)
                load_book(get_IDX())
            except IndexError as e:
                if DEBUG: print(e)

        elif event[0] == "TABLE" and event[1] == "+EDITED+" and not GLOBAL_EMPTY_OVERRIDE:
            update_hashes()
            my_data[convert_to_IDX(event[2][0] + 1), event[2][1]] = window["TABLE"].Values[event[2][0]][event[2][1]]
            table_data[get_IDX(), event[2][1]] = window["TABLE"].Values[event[2][0]][event[2][1]]
            load_book(get_IDX())

        elif event in Layouter.key_list:
            write_book_key(get_IDX(), event)
            update_hashes()

        elif re.search(" AUTO_COMBO ", event):
            if not re.search("SEARCH",event) and window["-EDITABLE?-"].get(): close_auto_box(); continue
            key = event.replace(" AUTO_COMBO ", "")
            if re.search("KEY_PRESS",key):
                key_name = key.removesuffix("KEY_PRESS")

                if key_name!=prev_selected_auto: close_auto_box()
                prev_selected_auto = key_name
                
                if key_name in Layouter.combo_elements:
                    i = Layouter.key_list.index(key_name.removesuffix("ADD_ENTRY"))
                elif key_name in Layouter.combo_elements_search:
                    i = Layouter.search_key_list.index(key_name.removesuffix("ADD_ENTRY"))

                if key_name in Layouter.combo_elements_search or key_name in Layouter.combo_elements:
                    current = str(window[key_name].get()).lower()
                    new_list = my_data[1:, i].tolist()
                    set_list = []
                    new_list.pop(get_IDX() - 1)
                    for n in new_list:
                        for t in str(n).split("|"):
                            set_list.append(t)
                    set_list = list(set(set_list))
                    set_list.sort()
                    new_list = []
                
                    for val in set_list:
                        try:
                            if re.search(remove_regex(current), str(val).lower()):
                                new_list.append(val)
                        except re.PatternError:
                            if DEBUG: print(remove_regex(current))
                    if not str(window[key_name].get()) in new_list:
                        new_list.insert(0, str(window[key_name].get()))

                if key_name in Layouter.combo_elements:
                    write_book_key(get_IDX(),key_name.removesuffix("ADD_ENTRY"))
                elif key_name in Layouter.combo_elements_search:
                    search()
                try:
                    if auto_window.is_closed():
                        auto_window_layout = [[sg.Listbox(values=new_list, expand_x=True, expand_y=True, pad=0,key="AUTOBOX")]]
                        x = window[key_name].Widget.winfo_rootx()
                        y = window[key_name].Widget.winfo_rooty() + window[key_name].get_size()[1]
                        auto_window = sg.Window(
                            font=FONT, margins=(0, 0), layout=auto_window_layout, title="_", no_titlebar=True, keep_on_top=True, size=(window[key_name].get_size()[0], window[key_name].get_size()[1]*5), finalize=True, location=(x, y)
                        )
                        auto_window.bind("<Button-1>", key_name+" AUTO_COMBO ENTER")
                    else:
                        auto_window["AUTOBOX"].update(values=new_list)
                    auto_window["AUTOBOX"].metadata = -1
                except NameError:
                    auto_window_layout = [[sg.Listbox(values=new_list, expand_x=True, expand_y=True, pad=0,key="AUTOBOX")]]
                    x = window[key_name].Widget.winfo_rootx()
                    y = window[key_name].Widget.winfo_rooty() + window[key_name].get_size()[1]
                    auto_window = sg.Window(
                            font=FONT, margins=(0, 0), layout=auto_window_layout, title="_", no_titlebar=True, keep_on_top=True, size=(window[key_name].get_size()[0], window[key_name].get_size()[1]*5), finalize=True, location=(x, y)
                    )
                    auto_window.bind("<Button-1>", key_name+" AUTO_COMBO ENTER")
                    auto_window["AUTOBOX"].metadata = -1
                window[key_name].set_focus()
                
            elif re.search("ENTER",key):
                key_name = key.removesuffix("ENTER")
                try:
                    if str(auto_window["AUTOBOX"].get()) != "":
                        try: window[key_name].update(str(auto_window["AUTOBOX"].get()[0]))
                        except IndexError: pass
                except NameError:
                    pass
                close_auto_box()
                if re.search("ADD_ENTRY",key):
                    if str(window[key_name].get()) != "":
                        window[key_name.removesuffix("ADD_ENTRY")].update(append=True, value="\n" + str(window[key_name].get()))
                        window[key_name].update(value="")
                        window[key_name.removesuffix("ADD_ENTRY")].update(append=False, value=str(window[key_name.removesuffix("ADD_ENTRY")].get()).removeprefix("\n"))
                if key_name in Layouter.combo_elements:
                    write_book_key(get_IDX(),key_name.removesuffix("ADD_ENTRY"))
                elif key_name in Layouter.combo_elements_search:
                    search()
            elif re.search("UNFOCUS",key):
                key_name = key.removesuffix("UNFOCUS")
                try:
                    e,v = auto_window.read(10,timeout_key="TIMEOUT")
                    if DEBUG: print(e,v)
                    if e!="TIMEOUT" and e!=None:
                        if re.search("AUTO_COMBO ENTER",e):
                            key_name = e.removesuffix(" AUTO_COMBO ENTER")
                            if str(auto_window["AUTOBOX"].get()) != "":
                                try: window[key_name].update(str(auto_window["AUTOBOX"].get()[0]))
                                except IndexError: pass
                    if key_name in Layouter.combo_elements:
                        write_book_key(get_IDX(),key_name.removesuffix("ADD_ENTRY"))
                    elif key_name in Layouter.combo_elements_search:
                        search()
                    close_auto_box()
                except NameError: pass
            elif re.search(" SELECT_", event):
                if re.search(" SELECT_UP", event):
                    key_name = event.removesuffix(" SELECT_UP")
                    c = -1
                elif re.search(" SELECT_DOWN", event):
                    key_name = event.removesuffix(" SELECT_DOWN")
                    c = 1
                else:
                    continue
                try:
                    auto_window["AUTOBOX"].metadata += c
                    if auto_window["AUTOBOX"].metadata < 0:
                        auto_window["AUTOBOX"].metadata = 0
                    if auto_window["AUTOBOX"].metadata > len(auto_window["AUTOBOX"].Values) - 1:
                        auto_window["AUTOBOX"].metadata = len(auto_window["AUTOBOX"].Values) - 1
                    
                    auto_window["AUTOBOX"].update(set_to_index=auto_window["AUTOBOX"].metadata, scroll_to_index=auto_window["AUTOBOX"].metadata)
                    if DEBUG: print(auto_window["AUTOBOX"].metadata, len(auto_window["AUTOBOX"].Values) - 1)
                except NameError:
                    pass


        elif event == "-NEW-" and not GLOBAL_SEARCH:
            lock_input(False)
            window[Layouter.key_list[1]].set_focus()
            window["-EDITABLE?-"].update(value=False)
            my_data = numpy.append(my_data, numpy.zeros(shape=[1, my_data.shape[1]], dtype=str), 0)
            my_data[-1, 0] = len(my_data[:]) - 1
            table_data = my_data
            set_IDX(data_len())
            load_book(get_IDX())
            window["LEN"].update("von " + str(data_len()))
            window["-TAB-BUCH-"].select()

        elif event == "-IDX_FRONT-" and not GLOBAL_EMPTY_OVERRIDE:
            set_IDX(1)
            load_book(get_IDX())
        elif event == "-IDX_L-" and not GLOBAL_EMPTY_OVERRIDE :
            set_IDX(get_IDX_input() - 1)
            load_book(get_IDX())
        elif event == "-IDX_R-" and not GLOBAL_EMPTY_OVERRIDE:
            set_IDX(get_IDX_input() + 1)
            load_book(get_IDX())
        elif event == "-IDX_BACK-" and not GLOBAL_EMPTY_OVERRIDE:
            set_IDX(data_len())
            load_book(get_IDX())

        elif event == "-CLEAR-":
            if prev_button != None: window[prev_button].update(disabled=False)
            clear_all_filters()

        elif event == "-TAB-":
            if values["-TAB-"] == "ANALYSE":
                update_analysis()

            elif values["-TAB-"] == "STANDORTE":
                if Layouter.treat_as_pos != None:
                    if hash(my_data[1:, Layouter.treat_as_pos].data.tobytes()) != hash_val_STANDORT:
                        hash_val_STANDORT = hash(my_data[1:, Layouter.treat_as_pos].data.tobytes())
                        if layouter.key_counter != 0:
                            window[get_key("ALL_STANDORTE")].update(visible=False)
                        window.extend_layout(window["STANDORTE"], layouter.make_layout_standort(my_data[1:, Layouter.treat_as_pos].tolist()))

        elif re.search("GETSTANDORT", event):
            if prev_button != None: window[prev_button].update(disabled=False)
            button_name = str(event).removeprefix("GETSTANDORT---")
            if DEBUG: print("Last:" + button_name[: int(button_name.rindex("-")) + 1])
            button_name = button_name[: int(button_name.rindex("-")) + 1].removesuffix("---")
            window["SEARCH-STANDORT-"].update(button_name)
            search()
            prev_button = event
            window[event].update(disabled=True)
        elif event == "-ALL_STANDORTE-":
            if prev_button != None: window[prev_button].update(disabled=False)
            prev_button = None
            window["SEARCH-STANDORT-"].update("")
            search()
        elif event == "-BIGSMALL?-":
            search()
        elif event == "-ALL_OR_ANY?-":
            search()
        elif event == "-REGEX?-":
            search()

        elif event == "Copyright::COPY":
            f = open(files.resource_path("./LICENSE"), encoding="utf-8")
            sgfxd = f.readlines()
            text = "".join(sgfxd)
            layoutINFO = [[sg.Multiline(text, justification="center", auto_size_text=True, size=(50, 20), disabled=True)]]
            windowINFO = sg.Window(lang.BIBLIA_APP_INFO, layoutINFO, font=FONT, finalize=True, icon=ICON)
            windowINFO.read()
            windowINFO.close()
        elif event == "darkdetect::COPYRIGHT":
            f = open(files.resource_path("./copyright/copyright_darkdetect"), encoding="utf-8")
            sgfxd = f.readlines()
            text = "".join(sgfxd)
            layoutINFO = [[sg.Multiline(text, justification="center", auto_size_text=True, size=(50, 20), disabled=True)]]
            windowINFO = sg.Window(lang.BIBLIA_APP_INFO, layoutINFO, font=FONT, finalize=True, icon=ICON)
            windowINFO.read()
            windowINFO.close()
        elif event == "PySimpleGUI::COPYRIGHT":
            f = open(files.resource_path("./copyright/copyright_pysimplegui"), encoding="utf-8")
            sgfxd = f.readlines()
            text = "".join(sgfxd)
            layoutINFO = [[sg.Multiline(text, justification="center", auto_size_text=True, size=(50, 20), disabled=True)]]
            windowINFO = sg.Window(lang.BIBLIA_APP_INFO, layoutINFO, font=FONT, finalize=True, icon=ICON)
            windowINFO.read()
            windowINFO.close()
        elif event == "NumPy::COPYRIGHT":
            f = open(files.resource_path("./copyright/copyright_numpy"), encoding="utf-8")
            sgfxd = f.readlines()
            text = "".join(sgfxd)
            layoutINFO = [[sg.Multiline(text, justification="center", auto_size_text=True, size=(50, 20), disabled=True)]]
            windowINFO = sg.Window(lang.BIBLIA_APP_INFO, layoutINFO, font=FONT, finalize=True, icon=ICON)
            windowINFO.read()
            windowINFO.close()
        elif event == "Regex::HILFE":
            f = open(files.resource_path(lang.BIBLIA_APP_REGEX_FILE_NAME), encoding="utf-8")
            sgfxd = f.readlines()
            text = "".join(sgfxd)
            layoutINFO = [[sg.Multiline(text, justification="left", auto_size_text=True, size=(50, 20), disabled=True)]]
            windowINFO = sg.Window(lang.BIBLIA_APP_REGEX_HEADER, layoutINFO, font=FONT, finalize=True, icon=ICON)
            windowINFO.read()
            windowINFO.close()

        elif re.search("!CLEAR", event):
            if prev_button != None: window[prev_button].update(disabled=False)
            name = event.removeprefix("!CLEAR")
            window[name].update("")
            if event == "!CLEAR-SIMPLE_SEARCH-":
                simple_search_update()
            elif re.search("SEARCH", name):
                search()

        elif event == "-EINTRAG_LÖSCHEN-":
            layoutCaution = [
                [sg.Text(lang.BIBLIA_APP_YOU_WANNA_REALY_DELETE, justification="center", auto_size_text=True)],
                [sg.Column([[sg.Button(lang.BIBLIA_APP_DELETE, key="-DELETE-"), sg.Button(lang.BIBLIA_APP_CANCEL, key="-CLOSE-")]], element_justification="center", expand_x=True)],
            ]
            windowCaution = sg.Window(lang.BIBLIA_APP_CONFIRM_DELETE, layoutCaution, font=FONT, finalize=True, icon=ICON)
            eventC, ValuesC = windowCaution.read()
            if eventC == "-DELETE-":
                my_data = numpy.delete(my_data, get_IDX(), 0)
                my_data = files.re_index(my_data)
                search()
                windowCaution.close()
            if eventC == "-CLOSE-":
                windowCaution.close()

        elif event == "-ALLE_LÖSCHEN-":
            layoutCaution = [
                [
                    sg.Text(
                        lang.BIBLIA_APP_YOU_WANNA_REALY_DELETE_ALL,
                        justification="center",
                        auto_size_text=True,
                    )
                ],
                [sg.Column([[sg.Button(lang.BIBLIA_APP_DELETE, key="-DELETE-"), sg.Button(lang.BIBLIA_APP_CANCEL, key="-CLOSE-")]], element_justification="center", expand_x=True)],
            ]
            windowCaution = sg.Window(lang.BIBLIA_APP_CONFIRM_DELETE, layoutCaution, font=FONT, finalize=True, icon=ICON)
            eventC, ValuesC = windowCaution.read()
            if eventC == "-DELETE-":
                list_of_books = table_data[1:, 1].tolist()
                layoutCaution2 = [
                    [sg.Text(lang.BIBLIA_APP_YOU_WANNA_REALY_DELETE_ALL_FR, justification="center", auto_size_text=True, expand_x=True)],
                    [sg.Listbox(list_of_books, justification="center", auto_size_text=True, select_mode=sg.SELECT_MODE_BROWSE, size=(60, 10))],
                    [sg.Column([[sg.Button(lang.BIBLIA_APP_DELETE, key="-DELETE_FR-"), sg.Button(lang.BIBLIA_APP_CANCEL, key="-CLOSE_FR-")]], element_justification="center", expand_x=True)],
                ]
                windowCaution2 = sg.Window(lang.BIBLIA_APP_CONFIRM_DELETE, layoutCaution2, font=FONT, finalize=True, icon=ICON)
                eventC2, ValuesC2 = windowCaution2.read()
                if eventC2 == "-DELETE_FR-":
                    for element in reversed(table_data[1:, 0].tolist()):
                        my_data = numpy.delete(my_data, int(element), 0)
                    windowCaution2.close()
                    windowCaution.close()
                    my_data = files.re_index(my_data)
                    clear_all_filters()
                if eventC2 == "-CLOSE_FR-":
                    windowCaution2.close()
                    windowCaution.close()
            if eventC == "-CLOSE-":
                windowCaution.close()

        profiler.profiling_end()
    # Finish up by removing from the screen
    try:
        window.close()
    except NameError:
        pass
except ZeroDivisionError as e:  # Exception as e:
    if DEBUG: print(e)
    input()
