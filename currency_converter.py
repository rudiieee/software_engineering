import tkinter as tk
import tkinter.messagebox as messagebox
import pika
import uuid
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random


# This class was provided by my teammate Morgan Kandula as part of the communication contract
class RandomTextRPC():

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def request_text(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='text_gen',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body="please")
        self.connection.process_data_events(time_limit=None)
        return self.response


# The functions encrypt and decrypt were taken from:
# https://newbedev.com/how-to-encrypt-text-with-a-password-in-python
def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data


def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding


def generate_random_text():
    print("GENERATING RANDOM TEXT")
    example_client = RandomTextRPC()
    print(" [client.py] Requesting text")
    response = example_client.request_text()
    print(f" [client.py] Got {response}")
    gen_text_box.insert(0, response)


def copy_gen_text():
    print("COPY GENERATED TEXT")
    window.clipboard_clear()
    text = gen_text_box.get()
    window.clipboard_append(text)
    copy_message = messagebox.showinfo("confirmation", "Your text has been correctly copied!")
    window.update()


def clear_gen_text():
    print("DELETE GENERATED TEXT")
    answer = messagebox.askyesno(title='confirmation', message='Are you sure you want to clear the text?')
    if answer:
        gen_text_box.delete(0, 'end')


def encrypt_text():
    print("ENCRYPT TEXT")
    data = encrypt_text_box.get()
    data = data.encode('utf-8')
    password = password_text_box.get()
    password = password.encode('utf-8')
    encrypted = encrypt(password, data)
    decrypt_text_box.delete(0, 'end')
    decrypt_text_box.insert(0, encrypted)
    encrypt_text_box.delete(0, 'end')
    password_text_box.delete(0, 'end')


def decrypt_text():
    print("DECRYPT TEXT")
    data = encrypt_text_box.get()
    password = password_text_box.get()
    password = password.encode('utf-8')
    decrypted = decrypt(password, data)
    decrypt_text_box.delete(0, 'end')
    decrypt_text_box.insert(0, decrypted)
    encrypt_text_box.delete(0, 'end')
    password_text_box.delete(0, 'end')


def copy_encrypt_text():
    print("COPY ENCRYPT TEXT")
    window.clipboard_clear()
    text = decrypt_text_box.get()
    window.clipboard_append(text)
    copy_message = messagebox.showinfo("confirmation", "Your text has been correctly copied!")
    window.update()


def clear_encrypt_text():
    print("DELETE ENCRYPT TEXT")
    answer = messagebox.askyesno(title='confirmation', message='Are you sure you want to clear the text?')
    if answer:
        decrypt_text_box.delete(0, 'end')


def help_random_text():
    print("HELP RANDOM TEXT")
    help_message = messagebox.showinfo("confirmation", 'On this section you can click on the'
                                                       '"Generate Random Text" to automatically'
                                                       'generate a text on the box below.\n\n'
                                                       'You can also type some text there if you want.')
    window.update()


def help_encrypt():
    print("HELP RANDOM TEXT")
    help_message = messagebox.showinfo("confirmation", 'On this section you can enter some text '
                                                       'on box 1, or you can paste the text generated '
                                                       'on the section below. \n\nOn number 2 you can '
                                                       'add a password to encrypt your text. \n\nOn number '
                                                       '3 you will get the encripted text. \n\nThis also works '
                                                       'to decrypt, you paste the encrpted text on box 1 '
                                                       'and you will get the original text on box 3.')
    window.update()


def clear_all_text():
    print("DELETE ALL TEXT")
    answer = messagebox.askyesno(title='confirmation', message='Are you sure you want to start over and clear all text?')
    if answer:
        gen_text_box.delete(0, 'end')
        encrypt_text_box.delete(0, 'end')
        password_text_box.delete(0, 'end')
        decrypt_text_box.delete(0, 'end')


def set_window_sizes(window):
    window.geometry("1200x1500")
    window.columnconfigure(0, minsize=400)
    window.columnconfigure(1, minsize=400)
    window.columnconfigure(2, minsize=400)
    window.rowconfigure(3, minsize=30)
    window.rowconfigure(4, minsize=30)
    window.rowconfigure(5, minsize=30)
    window.rowconfigure(6, minsize=30)
    window.rowconfigure(7, minsize=30)
    window.rowconfigure(12, minsize=30)
    window.rowconfigure(13, minsize=30)
    window.rowconfigure(14, minsize=30)
    window.rowconfigure(15, minsize=30)
    window.rowconfigure(16, minsize=30)
    window.rowconfigure(22, minsize=30)
    window.rowconfigure(23, minsize=30)
    window.rowconfigure(24, minsize=30)
    window.rowconfigure(25, minsize=30)
    window.rowconfigure(26, minsize=30)


def bind_buttons():
    gen_text_copy.bind('<Enter>', on_enter_gen_text_copy)
    gen_text_copy.bind('<Leave>', on_leave_gen_text_copy)
    gen_text_clear.bind('<Enter>', on_enter_gen_text_clear)
    gen_text_clear.bind('<Leave>', on_leave_gen_text_clear)

    encrypting.bind('<Enter>', on_enter_encrypt)
    encrypting.bind('<Leave>', on_leave_encrypt)
    decrypting.bind('<Enter>', on_enter_decrypt)
    decrypting.bind('<Leave>', on_leave_decrypt)

    encrypt_text_copy.bind('<Enter>', on_enter_encrypt_text_copy)
    encrypt_text_copy.bind('<Leave>', on_leave_encrypt_text_copy)
    encrypt_text_clear.bind('<Enter>', on_enter_encrypt_text_clear)
    encrypt_text_clear.bind('<Leave>', on_leave_encrypt_text_clear)

    clear_all.bind('<Enter>', on_enter_clear_all)
    clear_all.bind('<Leave>', on_leave_clear_all)


def on_enter_gen_text_copy(e):
    gen_text_copy.config(fg= "red", bg='Red')
    gen_text_copy_label.config(text='This will copy the text from the box above')


def on_leave_gen_text_copy(e):
    gen_text_copy.config(fg= 'black')
    gen_text_copy_label.config(text='')


def on_enter_gen_text_clear(e):
    gen_text_clear.config(fg= "red", bg='Red')
    gen_text_clear_label.config(text='This will clear all text above')


def on_leave_gen_text_clear(e):
    gen_text_clear.config(fg= 'black')
    gen_text_clear_label.config(text='')


def on_enter_encrypt(e):
    encrypting.config(fg= "red", bg='Red')
    encrypting_label.config(text='This will encrypt text on box 1 with the password on box 2')


def on_leave_encrypt(e):
    encrypting.config(fg= 'black')
    encrypting_label.config(text='')


def on_enter_decrypt(e):
    decrypting.config(fg= "red", bg='Red')
    decrypting_label.config(text='This will decrypt text on box 1 with the password on box 2')


def on_leave_decrypt(e):
    decrypting.config(fg= 'black')
    decrypting_label.config(text='')


def on_enter_encrypt_text_copy(e):
    encrypt_text_copy.config(fg= "red", bg='Red')
    encrypt_text_copy_label.config(text='This will copy the text from the box above')


def on_leave_encrypt_text_copy(e):
    encrypt_text_copy.config(fg= 'black')
    encrypt_text_copy_label.config(text='')


def on_enter_encrypt_text_clear(e):
    encrypt_text_clear.config(fg= "red", bg='Red')
    encrypt_text_clear_label.config(text='This will clear all text above')


def on_leave_encrypt_text_clear(e):
    encrypt_text_clear.config(fg= 'black')
    encrypt_text_clear_label.config(text='')


def on_enter_clear_all(e):
    clear_all.config(fg= "red", bg='Red')
    clear_all_label.config(text='This will delete all text in all the boxes above')


def on_leave_clear_all(e):
    clear_all.config(fg= 'black')
    clear_all_label.config(text='')


# window sizes config
window = tk.Tk()
# root = tix.Tk()
window.title('Encrypt / Decrypt Program')
set_window_sizes(window)

# Text Generator
title1 = tk.Label(window, text = "Random Text Generator", font=("Arial", 25))
title1.grid(row=0, column=1, sticky = 'nsew', padx=15, pady=(20, 10))
help_random_text = tk.Button(window, text='?', command=help_random_text)
help_random_text.grid(row=0, column=2, padx=15, pady=1)
gen_text_1 = tk.Label(window, text = "1. Click the button on the right to generate text: ")
gen_text_1.grid(row=1, column=0, sticky='w', padx=15, pady=1)
gen_text_copy = tk.Button(window, text='Generate Random Text', command=generate_random_text)
gen_text_copy.grid(row=1, column=2, padx=15, pady=1)
gen_text_2 = tk.Label(window, text = "2. Generated Text: (You can type your own text if you want)")
gen_text_2.grid(row=2, column=0, sticky='w', padx=15, pady=1)
gen_text_box = tk.Entry(window, font=("arial", 24))
gen_text_box.grid(row=3, column=0, rowspan=5, columnspan=3, sticky = 'nsew', padx=15, pady=1)

gen_text_copy = tk.Button(window, text='Copy', command=copy_gen_text)
gen_text_copy.grid(row=8, column=0, padx=15, pady=1)
gen_text_clear = tk.Button(window, text='Clear', command=clear_gen_text)
gen_text_clear.grid(row=8, column=1, padx=1, pady=1)
gen_text_copy_label = tk.Label(window, text='', bd=1,)
gen_text_copy_label.grid(row=9, column=0, padx=15, pady=1)
gen_text_clear_label = tk.Label(window, text='', bd=1,)
gen_text_clear_label.grid(row=9, column=1, padx=1, pady=1)

# Encrypt / Decrypt
title2 = tk.Label(window, text = "Encrypt / Decrypt with Password", font=("Arial", 25))
title2.grid(row=10, column=1, sticky = 'nsew', padx=15, pady=1)
help_encrypt_decrypt = tk.Button(window, text='?', command=help_encrypt)
help_encrypt_decrypt.grid(row=10, column=2, padx=15, pady=1)
encrypt_text_1 = tk.Label(window, text = "1. Enter text to Encrypt / Decrypt: ")
encrypt_text_1.grid(row=11, column=0, sticky='w', padx=15, pady=1)
encrypt_text_box = tk.Entry(window, font=("arial", 24))
encrypt_text_box.grid(row=12, column=0, rowspan=5, columnspan=3, sticky = 'nsew', padx=15, pady=1)
encrypt_text_2 = tk.Label(window, text = "2. Enter password for Encryption / Decryption: ")
encrypt_text_2.grid(row=17, column=0, sticky='w', padx=15, pady=1)
password_text_box = tk.Entry(window, font=("arial", 24))
password_text_box.grid(row=18, column=0, columnspan=3, sticky = 'nsew', padx=15, pady=1)

encrypting = tk.Button(window, text='Encrypt', command=encrypt_text)
encrypting.grid(row=19, column=0, padx=15, pady=1)
decrypting = tk.Button(window, text='Decrypt', command=decrypt_text)
decrypting.grid(row=19, column=1, padx=1, pady=1)
encrypting_label = tk.Label(window, text='', bd=1,)
encrypting_label.grid(row=20, column=0, padx=15, pady=1)
decrypting_label = tk.Label(window, text='', bd=1,)
decrypting_label.grid(row=20, column=1, padx=1, pady=1)

encrypt_text_3 = tk.Label(window, text = "3. Output text from Encryption / Decryption: ")
encrypt_text_3.grid(row=21, column=0, sticky='w', padx=15, pady=1)
decrypt_text_box = tk.Entry(window, font=("arial", 24))
decrypt_text_box.grid(row=22, column=0, rowspan=5, columnspan=3, sticky = 'nsew', padx=15, pady=1)

encrypt_text_copy = tk.Button(window, text='Copy', command=copy_encrypt_text)
encrypt_text_copy.grid(row=28, column=0, padx=15, pady=1)
encrypt_text_clear = tk.Button(window, text='Clear', command=clear_encrypt_text)
encrypt_text_clear.grid(row=28, column=1, padx=1, pady=1)
encrypt_text_copy_label = tk.Label(window, text='', bd=1,)
encrypt_text_copy_label.grid(row=29, column=0, padx=15, pady=1)
encrypt_text_clear_label = tk.Label(window, text='', bd=1,)
encrypt_text_clear_label.grid(row=29, column=1, padx=1, pady=1)

clear_all = tk.Button(window, text='Start Over', command=clear_all_text)
clear_all.grid(row=30, column=1, sticky='w', padx=1, pady=1)
clear_all_label = tk.Label(window, text='', bd=1,)
clear_all_label.grid(row=31, column=1, sticky='w', padx=1, pady=1)
bind_buttons()

window.mainloop()
