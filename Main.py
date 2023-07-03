import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.filedialog import asksaveasfile
import json
from haralyzer import HarParser, HarPage

from openpyxl.workbook import Workbook

import pandas as pd
har_datas = []


# initalise the tkinter GUI
root = tk.Tk()

root.geometry("500x500") # set the root dimensions
root.pack_propagate(False) # tells the root to not let the widgets inside it determine its size.
# root.resizable(0, 0) # makes the root window fixed in size.

# Frame for TreeView
frame1 = tk.LabelFrame(root, text="Har Analyzer")
frame1.place(height=600, width=1350)

# Frame for open file dialog
file_frame = tk.LabelFrame(root, text="Open File")
file_frame.place(height=100, width=400, rely=0.85, relx=0)

# Buttons
button1 = tk.Button(file_frame, text="Browse A File", command=lambda: File_dialog())
button1.place(rely=0.65, relx=0.30)

button2 = tk.Button(file_frame, text="Load File", command=lambda: Load_Har_data())
button2.place(rely=0.65, relx=0.10)

button3 = tk.Button(file_frame, text="Export to Excel", command=lambda: export_to_excel())
button3.place(rely=0.65, relx=0.60)

# The file/file path text
label_file = ttk.Label(file_frame, text="No File Selected")
label_file.place(rely=0, relx=0)

style = ttk.Style()
style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11)) # Modify the font of the body
style.configure("mystyle.Treeview.Heading", font=('Calibri', 13,'bold')) # Modify the font of the headings

## Treeview Widget
tv1 = ttk.Treeview(frame1,style="mystyle.Treeview")
tv1.place(relheight=1, relwidth=1) # set the height and width of the widget to 100% of its container (frame1).

tv1.tag_configure('odd', background='#87CEEB')
tv1.tag_configure('even', background='#FFFFFF')

treescrolly = tk.Scrollbar(frame1, orient="vertical", command=tv1.yview) # command means update the yaxis view of the widget
treescrollx = tk.Scrollbar(frame1, orient="horizontal", command=tv1.xview) # command means update the xaxis view of the widget
tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set) # assign the scrollbars to the Treeview Widget
treescrollx.pack(side="bottom", fill="x") # make the scrollbar fill the x axis of the Treeview widget
treescrolly.pack(side="right", fill="y") # make the scrollbar fill the y axis of the Treeview widget


def File_dialog():
    """This Function will open the file explorer and assign the chosen file path to label_file"""
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select A File",
                                          filetype=(("Har files", ".har"),("All Files", ".*")))
    label_file["text"] = filename
    return None


def Load_Har_data():
    """If the file selected is valid this will load the file into the Treeview"""
    file_path = label_file["text"]
    # print(file_path)
    try:
        with open(file_path, 'r',encoding="utf8") as f:
            har_parser = HarParser(json.loads(f.read()))
            data = har_parser.har_data


    except ValueError:

        tk.messagebox.showerror("Information", "The file you have chosen is invalid")
        return None
    except FileNotFoundError:
        tk.messagebox.showerror("Information", f"No such file as {file_path}")
        return None    

    

    


    oncontenttime=data["pages"][0]["pageTimings"]["onContentLoad"]
    print("Page oncontenttime ="+str(int(oncontenttime)) +" ms")

    onload=data["pages"][0]["pageTimings"]["onLoad"]

    print("Page onLoad=" +str(onload) + " ms")



    for i in data["entries"]:
        for k in i:
            if k == "request":
                URLs= i[k]["url"]
                method=i[k]["method"]
                new_dict = {"Request Url":URLs,"Method ":method}

            elif k=="response":
                status=i[k]["status"] 
                new_dict.update({"Response Status":status})

            elif k=="time": 
                times=int(i[k]) 
                new_dict.update({"Total Time":str(times)+" ms"})


            elif k == "timings":
                new_dict.update(i[k])
                #print(new_dict)
                har_datas.append(new_dict)
            
     
        

            
            
    # print(har_datas)  
    global df
    df = pd.DataFrame(data=har_datas)
    df = df.astype({"blocked":'int',"dns":'int',"ssl":'int',"connect":'int',"send":'int',"wait":'int',"receive":'int',"_blocked_queueing":'int'})
    df = df.rename(columns={"blocked":"blocked (ms)","dns":"dns (ms)","ssl":"ssl (ms)","connect":"connect (ms)","send":"send (ms)","wait":"wait (ms)","receive":"receive (ms)","_blocked_queueing":"_blocked_queueing (ms)"}) 
  
    clear_data()
    l1 = list(df)
    r_set = df.to_numpy().tolist()
    tv1['height']=20 # Number of rows to display, default is 10
    tv1['show'] = 'headings' 
    # column identifiers 
    tv1["columns"] = l1
        # Defining headings, other option in tree
        # width of columns and alignment 
    tag_i = 1
   
    for i in l1:
        tv1.column(i, width = 70, anchor ='c')
        tv1.heading(i, text =i)

        ## Adding data to treeview 
    for dt in r_set:  
        v=[r for r in dt] # creating a list from each row 
        if tag_i % 2 == 0:
            tv1.insert("",'end',iid=v[0],values=v,tags = ('even',))
        else:
            tv1.insert("",'end',iid=v[0],values=v,tags = ('odd',)) # adding row
        tag_i = tag_i + 1


    

   
    return None



def clear_data():
    tv1.delete(*tv1.get_children())
    return None

def export_to_excel():
    files = (('All Files','*.*'),('CSV Files','*.csv'))
    file = asksaveasfile(filetypes=files, defaultextension = files)
    if file:
        df.to_csv(file,index=False)


root.mainloop()
