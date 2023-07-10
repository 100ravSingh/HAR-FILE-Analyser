#!/usr/bin/env python
# coding: utf-8

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.filedialog import asksaveasfile
import seaborn as sns
import json
from haralyzer import HarParser, HarPage

from openpyxl.workbook import Workbook

import pandas as pd
import matplotlib.pyplot as plt

har_datas = []


# initalise the tkinter GUI
root = tk.Tk()

root.geometry("500x500") # set the root dimensions
root.title('HAR Analyzer')
root.pack_propagate(False) # tells the root to not let the widgets inside it determine its size.
# root.resizable(0, 0) # makes the root window fixed in size.

# Frame for TreeView
frame1 = tk.LabelFrame(root, text="Har Analyzer - Components Table")
frame1.place(height=600, width=1300)

# Frame for open file dialog
file_frame = tk.LabelFrame(root, text="File Operations")
file_frame.place(height=100, width=700, rely=0.85, relx=0)

label_1 = ttk.Label(root, text="Output Section ",font = ('courier', 10, 'bold'))
label_1.place(height=100, width=600, rely=0.85, relx=0.60)

# Buttons
button1 = tk.Button(file_frame, text="Browse A File", command=lambda: File_dialog())
button1.place(rely=0.65, relx=0.05)

button2 = tk.Button(file_frame, text="Load File", command=lambda: Load_Har_data())
button2.place(rely=0.65, relx=0.20)

button3 = tk.Button(file_frame, text="Export File", command=lambda: export_to_excel())
button3.place(rely=0.65, relx=0.45)

button4 = tk.Button(file_frame, text="Graph", command=lambda: graph())
button4.place(rely=0.65, relx=0.75)

button5 = tk.Button(file_frame, text="Time Graph", command=lambda: graph2())
button5.place(rely=0.65, relx=0.32)


Box1 = tk.Entry(file_frame,highlightthickness=2,justify = 'center',font = ('courier', 10, 'bold'))
Box1.place(rely=0.30,relx=0.65)

label_2 = ttk.Label(file_frame, text="Enter row number here",font = ('courier', 10, 'bold'))
label_2.place(rely=0, relx=0.65)

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
    onload=data["pages"][0]["pageTimings"]["onLoad"]
    
    label_1.config(text="Page oncontenttime = "+str(int(oncontenttime)) +" ms \n" + "Page onLoad = " +str(onload) + " ms" )



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
    df.insert(0,"Serial No.",range(1,len(df)+1)) 
    df['Total Time'] = df['Total Time'].str.replace(r'\D', '', regex=True).astype(int)
    df = df.astype({"Total Time":'int',"blocked":'int',"dns":'int',"ssl":'int',"connect":'int',"send":'int',"wait":'int',"receive":'int',"_blocked_queueing":'int'})
    df = df.rename(columns={"Total Time":"Total Time (ms)","blocked":"blocked (ms)","dns":"dns (ms)","ssl":"ssl (ms)","connect":"connect (ms)","send":"send (ms)","wait":"wait (ms)","receive":"receive (ms)","_blocked_queueing":"blocked_queueing (ms)"}) 
    df=df.replace(-1,"None")
    clear_data()
    
    r_set = df.to_numpy().tolist()
    
    tag_i = 1
   
    tv1["column"] = list(df.columns)
    tv1["show"] = "headings"
    for i in tv1["columns"]:
        tv1.heading(i, text=i) # let the column heading = column name
        #if(i==1):
        tv1.column(i,stretch=False,anchor ='c')
        #else:
           # tv1.column(i, anchor ='c')

        ## Adding data to treeview 
    for dt in r_set:  
        v=[r for r in dt] # creating a list from each row 
        if tag_i % 2 == 0:
            tv1.insert("",'end',values=v,tags = ('even',))
        else:
            tv1.insert("",'end',values=v,tags = ('odd',)) # adding row
        tag_i = tag_i + 1


    

   
    return None



def clear_data():
    tv1.delete(*tv1.get_children())
    return None

def graph2():
    
    TT = df[df['Total Time (ms)'] != 0]
    ######## for line graph#############
    #XX = TT['Total Time (ms)']
    #YY = TT['Serial No.']
    #plt.plot(XX, YY, 'o-g')
    ###############################
    SF= pd.DataFrame(TT, columns=['Serial No.','Total Time (ms)'])
    
    plots = sns.barplot(x="Serial No.", y="Total Time (ms)", data=SF)
    # plots = sns.barplot(x="Total Time (ms)", y="Serial No.", data=SF)
 
    # Iterating over the bars one-by-one
    for bar in plots.patches:
        plots.annotate(format(bar.get_height(), '0'),
                   (bar.get_x() + bar.get_width() / 2,
                    bar.get_height()), ha='center', va='center',
                   size=5, xytext=(0, 8),
                   textcoords='offset points')

        plt.xticks(rotation=90)           

                   
    
    # set axis titles
    plt.xlabel("URL Serial Number")
    plt.ylabel("Total Time in ms")
    # set chart title
    plt.title("Total Time Chart")
    plt.tight_layout()
    plt.show()

def graph():
    
    #DF = df.drop(df.columns[[1, 2, 3]], axis=1)
    DF = df.drop(df.columns[[0, 2, 3, 4]], axis=1)
    DF[["blocked (ms)","dns (ms)","ssl (ms)","connect (ms)","send (ms)","wait (ms)","receive (ms)","blocked_queueing (ms)"]] = DF[["blocked (ms)","dns (ms)","ssl (ms)","connect (ms)","send (ms)","wait (ms)","receive (ms)","blocked_queueing (ms)"]].replace("None", 0) 
    #DF = DF[DF.iloc[:, 1:].ne(0).any(axis=1)].reset_index(drop=True)
    

    for i, (idx, row) in enumerate(DF.set_index('Request Url').iterrows()):
        if (i+1) == int(Box1.get()):
            row = row[row.gt(row.sum() * .001)]
            IDX = idx
            plt.pie(row,autopct='%1.1f%%')            
            plt.legend(labels=row.index,loc="center right",bbox_to_anchor=(1,0.5), bbox_transform=plt.gcf().transFigure)
            plt.subplots_adjust(left=0.0, bottom=0.1, right=0.80)
            plt.title(str(IDX) + "   " + " [Total Time : " + str(df["Total Time (ms)"][i]) + " ms ]")
            plt.show()
        
    
    
    
    
def export_to_excel():
    # files = (('All Files','.'),('CSV Files','*.csv'))
    # file = asksaveasfile(filetypes=files, defaultextension = files)
    # if file:
    #     df.to_csv(file,index=False)

    try:
        
        save_path = filedialog.asksaveasfilename(defaultextension='.xlsx',filetypes=(("Excel files", "*.xlsx"),("All files", ".") ))
    
        if save_path:

            # Export DataFrame to Excel
            df.to_excel(save_path, index=False)
            print('Data exported successfully.')



    except FileNotFoundError:
        tk.messagebox.showerror("Information", "Please upload the file first")
        return None          


root.mainloop()
