# Nima Vahdat 610397163
from suffixTree import SuffixTree
import PySimpleGUI as sg
import os.path

sg.theme('DarkBlue10')

def string_maker(string):
    flag = False
    final_string = ""
    for s in string:
        if s == ">":
            final_string += ">"
            flag = True
        if s == "\n":
            flag = False
        
        if not flag and s != "\n":
            final_string += s
            
    final_string = final_string[1:] + "$"
    return final_string

string_sec = [
    [sg.Text("Brows a file or inter string")],
    [sg.Text('File path\nfor main Strings:'), sg.InputText(enable_events=True, key="-FOLDER-"), sg.FileBrowse()],
    [sg.Text('\nOR')],
    [sg.Text('             Strings:'), sg.Multiline(enable_events=True, key="-FOLDER1-")],
    [sg.Button("Creat Tree", key = "Creat-Tree"), sg.Text(" "*30, key = "-create-")]
    ]
find_sec = [[sg.Text('File path\nfor results:\n'), sg.InputText(enable_events=True, key="-FOLDER2-"), sg.FolderBrowse()],
    [sg.Text('            K:'), sg.InputText(key="-PATTERN-")],
    [sg.Button("Find"), sg.Text(" "*30, key = "-FIND-")]
    ]

layout = [
    [
      sg.Column(string_sec),
      sg.VSeparator(),
      sg.Column(find_sec)
      ]
]

# Create the window
window = sg.Window("Longest Substring (PART 2)", layout)
# Create an event loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    elif event == "Creat-Tree":
        x = values["-FOLDER-"]
        if x == '':
            tree = SuffixTree(string_maker(values["-FOLDER1-"]))
        else:
            f = open(x, "r")
            string = f.read()
            tree = SuffixTree(string_maker(string))
        window['-create-'].Update('Created!')

    elif event == "Find":
        a = tree.find_k_sub(int(values["-PATTERN-"]))
        if values["-FOLDER2-"]:
            path_ = values["-FOLDER2-"] + "/result.txt"
        else:
            path_ = "result.txt"
        f2 = open(path_, 'w')
        final = "RESULT:\n" + str(a)
        f2.write(final)
        f2.close()
        window['-FIND-'].Update('Check the result.txt!')
window.close()