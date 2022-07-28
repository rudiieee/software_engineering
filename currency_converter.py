import tkinter as tk
import tkinter.messagebox as messagebox


def copy_get_text():
    print("COPY")
    window.clipboard_clear()
    text = gen_text_box.get()
    window.clipboard_append(text)
    copy_message = messagebox.showinfo("confirmation", "Your text has been correctly copied!")
    window.update()
    return True


def clear_get_text():
    print("DELETE")
    answer = messagebox.askyesno(title='confirmation', message='Are you sure you want to clear the text?')
    if answer:
        gen_text_box.delete(0, 'end')
    return True


# window sizes config
window = tk.Tk()
# root = tix.Tk()
window.title('Encrypt / Decrypt Program')
window.geometry("800x1500")
window.columnconfigure(0,minsize=200)
window.columnconfigure(1,minsize=200)
window.columnconfigure(2,minsize=200)
window.rowconfigure(3,minsize=50)
window.rowconfigure(4,minsize=50)
window.rowconfigure(5,minsize=50)
window.rowconfigure(6,minsize=50)
window.rowconfigure(7,minsize=50)

# Text Generator
title = tk.Label(window, text = "Random Text Generator", font=("Arial", 25))
title.grid(row=0, column=0, sticky = 'nsew', padx=10, pady=10)
gen_text_1 = tk.Label(window, text = "1. Click the button on the right to generate text: ")
gen_text_1.grid(row=1, column=0, sticky = 'w', padx=10, pady=10)
gen_text_2 = tk.Label(window, text = "2. Generated Text: (You can type your own text if you want)")
gen_text_2.grid(row=2, column=0, sticky = 'w', padx=10, pady=10)
gen_text_box = tk.Entry(window, font=("arial", 24))
gen_text_box.grid(row=3, column=0, rowspan=5, columnspan=3, sticky = 'nsew', padx=10, pady=10)

gen_text_copy = tk.Button(window, text='Copy', command=copy_get_text)
gen_text_copy.grid(row=8, column=0, padx=10, pady=10)
gen_text_clear = tk.Button(window, text='Clear', command=clear_get_text)
gen_text_clear.grid(row=8, column=1, padx=10, pady=10)
gen_text_copy_label = tk.Label(window, text='', bd=1,)
gen_text_copy_label.grid(row=9, column=0, padx=10, pady=10)
gen_text_clear_label = tk.Label(window, text='', bd=1,)
gen_text_clear_label.grid(row=9, column=1, padx=10, pady=10)


def on_enter_copy(e):
    gen_text_copy.config(fg= "red", bg='Red')
    gen_text_copy_label.config(text='By clicking on this button you will be\n'
                                     'copying the text inside the above box')


def on_leave_copy(e):
    gen_text_copy.config(fg= 'black')
    gen_text_copy_label.config(text='')


def on_enter_clear(e):
    gen_text_clear.config(fg= "red", bg='Red')
    gen_text_clear_label.config(text='By clicking on this button\n'
                                     'you will CLEAR all\n'
                                     'the text inside\n'
                                     'the above box')


def on_leave_clear(e):
    gen_text_clear.config(fg= 'black')
    gen_text_clear_label.config(text='')


gen_text_copy.bind('<Enter>', on_enter_copy)
gen_text_copy.bind('<Leave>', on_leave_copy)
gen_text_clear.bind('<Enter>', on_enter_clear)
gen_text_clear.bind('<Leave>', on_leave_clear)

window.mainloop()
