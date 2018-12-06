# CS121 Project 3
# Created by Ye Yuan
# Contributors: Diyue Gu, Jian Li
# Team# : 53

import sys
import Engine
import tkinter
import webbrowser

BIG_FONT = ('Helvetica', 20)
SMALL_FONT=('Helvetica', 15)
CELL_WIDTH = 65
LINE_COLOR="white"
CANVAS_COLOR="pink"

class GUI:
    def __init__(self):
        self.engine=Engine.IcsSearchEngine()
        self.engine.connect_to_redis()
        self.window = tkinter.Tk()
        self.window.title("ICS Search Engine!")

        self.label1 = tkinter.Label(
            master=self.window, text="Welcome to the ICS Search Engine!",
            font=BIG_FONT)
        self.label1.grid(
            row=0, column=0, padx=10, pady=10, sticky=tkinter.S)

        self.label2 = tkinter.Label(
            master=self.window, text="Before we start the game, please make sure the index file is ready.",
            font=('Helvetica', 15))
        self.label2.grid(
            row=1, column=0, padx=10, pady=10, sticky=tkinter.S)

        self.start_button = tkinter.Button(
            master=self.window, text="start",
            font=BIG_FONT,
            command=self.start)
        self.start_button.grid(
            row=2, column=0, padx=10, pady=10, sticky=tkinter.S)

        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.window.rowconfigure(2, weight=1)
        self.window.columnconfigure(0, weight=1)

    def start(self):
        # self.start_button.grid_forget()
        # self.label1.grid_forget()
        # self.label2.grid_forget()

        self.window.destroy()

        self.window=tkinter.Tk()
        self.window.title("ICS Search Engine!")

        self.l_query = tkinter.Label(
            master=self.window, text="Please Enter your query:",
            font=('Helvetica', 20))
        self.l_query.grid(
            row=0, column=0, padx=10, pady=5, sticky=tkinter.S + tkinter.W)

        self.e_row = tkinter.Entry(master=self.window, width=33, font=BIG_FONT)
        self.e_row.insert(0, "Query can contain one or multiple token(s):")
        self.e_row.bind("<FocusIn>",
                        lambda x: self._on_entry_click(self.e_row, 'Query can contain one or multiple token(s):'))
        self.e_row.grid(row=1, column=0, padx=10, sticky=tkinter.S + tkinter.W)


        self.Search=tkinter.Button(
            master=self.window,text= "Search!",
            font=BIG_FONT,
            command=self._display)
        self.Search.grid(
            row = 2, column=0, padx= 50, pady=10, sticky= tkinter.S)

    def _on_entry_click(self,entry:tkinter.Entry, line:str):
        #delete the default content of the entry
        if entry.get()==line:
            entry.delete(0,"end")

    def _display(self):
        self.query = self.e_row.get()
        results = self.engine.run(self.query)
        print(results)
        self.window.destroy()

        self.window = tkinter.Tk()
        self.window.title("Results:")
        counter = 0
        for i in results:
            counter+=1
            w = tkinter.Label(master=self.window, text=i, borderwidth=1, relief="groove",width=60,
            font=('Helvetica', 20))
            if results[i] == '1':
                w.configure(background='pink')
            w.bind("<Button-1>", self.callback)

            w.pack()
        self.back_button = tkinter.Button(
            master=self.window, text="Back",
            font=BIG_FONT,
            command=self.start)
        self.back_button.pack()

    def callback(self,event):
        url='http://'+event.widget.cget("text")
        webbrowser.open(url)


    def run(self):
        #run the main window
        self.window.mainloop()

def main():
    ins = Engine.IcsSearchEngine()
    gui = GUI()
    gui.run()

if __name__ == '__main__':
    main()