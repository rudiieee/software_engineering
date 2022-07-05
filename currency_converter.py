import tkinter

window = tkinter.Tk()
name = tkinter.label(window, text = "Name").grid(row=0, column=0)
e1 = tkinter.Entry(window).grid(row=0, column=1)
password = tkinter.label(window, text = "Password").grid(row=1, column=0)
e2 = tkinter.Entry(window).grid(row=1, column=1)