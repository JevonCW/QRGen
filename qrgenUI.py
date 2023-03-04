import tkinter as tk
import qrcode
import re
import os
import string
from PIL import ImageTk, Image
from pyzbar.pyzbar import decode

URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # scheme
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class QRGeneratorApp:
    def __init__(self, master):

        # create a list to store the links
        self.links = []

        self.master = master
        master.title("QR Generator")
        master.resizable(False,False)
        
        # create a frame to hold the buttons
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        self.button_add = tk.Button(button_frame, text="Add Link", font=("Helvetica", 10), command=self.add_link, bg="#0077CC", fg="white")
        self.button_generate = tk.Button(button_frame, text="Generate", font=("Helvetica", 10), command=self.generate_qr_codes, bg="#0077CC", fg="white")
        self.button_clear = tk.Button(button_frame, text="Clear Links", font=("Helvetica", 10), command=self.clear_links, bg="red", fg="white")

        # pack the buttons inside the button_frame
        self.button_clear.pack(side=tk.LEFT, padx=10)
        self.button_add.pack(side=tk.LEFT)
        self.button_generate.pack(side=tk.LEFT, padx=10)

        # create a frame for the user input
        input_frame = tk.Frame(root)
        input_frame.pack(expand=True, fill='both')

        # create widgets for the input form
        self.entry_link = tk.Entry(input_frame, width=30, font=("Helvetica", 10), justify='center')
        self.link_label = tk.Label(input_frame, text="Link", font=("Helvetica", 10))
        self.entry_link.bind("<KeyPress>", lambda event: 
                             self.add_link() if event.keycode == 13 else None)


        self.entry_name = tk.Entry(input_frame, width=30, font=("Helvetica", 10), justify='center')
        self.name_label = tk.Label(input_frame, text="File Name (optional)", font=("Helvetica", 10))
        self.entry_name.bind("<KeyPress>", lambda event: 
                             self.add_link() if event.keycode == 13 else None)

        # pack the widgets
        self.link_label.pack(pady=1)
        self.entry_link.pack(pady=5)
        self.name_label.pack(pady=1)
        self.entry_name.pack(pady=5)

        # create a frame for the link display
        self.frame_links = tk.Frame(master, pady=10)
        #limit horizontal size of frame
        self.frame_links.pack(side=tk.BOTTOM, pady=10, fill=tk.BOTH)

    def add_link(self):
        # get the link and name from the input fields
        link = self.entry_link.get().strip()
        name = self.entry_name.get().strip()

        # validate the link
        if not link.startswith("http://") and not link.startswith("https://"):
            link = "http://" + link
        if not re.match(URL_REGEX, link):
            self.error_popup("Invalid URL")
            return

        if name.strip() == '':
                name = link

        # add the link to the list and clear the input fields
        self.links.append((link, name))
        self.entry_link.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)

        # display the links in the frame
        for widget in self.frame_links.winfo_children():
            widget.destroy()
        for i, (link, name) in enumerate(self.links):
            if name == link and len(name) > 40 or len(name) > 40:
                shortname = name[:40] + "..."
                label = tk.Label(self.frame_links, text=f"{shortname}")
            elif len(name) <= 40:
                label = tk.Label(self.frame_links, text=f"{name}")
            label.grid(row=i, column=0, sticky="w")

    def clear_links(self):
        self.links = []
        self.frame_links.destroy()
        self.frame_links = tk.Frame(self.master, pady=10)
        self.frame_links.pack(side=tk.BOTTOM, pady=10, fill=tk.BOTH)


    def error_popup(self, errormsg, files=None):
        popup = tk.Toplevel()
        popup.title("Error")
        popup.geometry("300x100")
        popup.overrideredirect(True)  # remove window decorations
        popup.iconbitmap('qrgen.ico')

        # change background color and font
        popup.configure(background='#F6CECE')
        label = tk.Label(popup, text=errormsg, font=('Helvetica', 14, 'bold'), fg='#800000', bg='#F6CECE')
        label.pack(side="top", fill="x", pady=10)

        # list file names with error message if files parameter is not None
        if files is not None:
            file_list = "\n".join(files)
            files_label = tk.Label(popup, text=f"Failed files:\n{file_list}", font=('Helvetica', 12), fg='#800000', bg='#F6CECE')
            files_label.pack(side="top", fill="x", pady=5)

        # change button color and font
        button = tk.Button(popup, text="OK", command=popup.destroy, font=('Helvetica', 12, 'bold'), bg='#800000', fg='white')
        button.pack()

        # Calculate the position of the popup relative to the main window
        x = root.winfo_rootx() + (root.winfo_width() - popup.winfo_width()) // 2
        y = root.winfo_rooty() + (root.winfo_height() - popup.winfo_height()) // 2
        popup.geometry("+{}+{}".format(x, y))

        popup.mainloop()

    def success_popup(self):
        popup = tk.Toplevel()
        popup.title("Success")
        popup.geometry("325x100")
        popup.overrideredirect(True)  # remove window decorations
        popup.iconbitmap('qrgen.ico')

        # change background color and font
        popup.configure(background='#77dd77')
        label = tk.Label(popup, text="QR Code(s) Successfully Created", font=('Helvetica', 14, 'bold'), fg='white', bg='#007f00')
        label.pack(side="top", fill="x", pady=10)

        # change button color and font
        button = tk.Button(popup, text="OK", command=popup.destroy, font=('Helvetica', 12, 'bold'), bg='#007f00', fg='white')
        button.pack()

        # Calculate the position of the popup relative to the main window
        x = root.winfo_rootx() + (root.winfo_width() - popup.winfo_width()) // 2
        y = root.winfo_rooty() + (root.winfo_height() - popup.winfo_height()) // 2
        popup.geometry("+{}+{}".format(x, y))

        self.clear_links()
        popup.mainloop()

    def generate_qr_codes(self):
        # generate a QR code for each link and save it as a PNG file
        for i, (link, name) in enumerate(self.links):            
            # generate the QR code
            version = None
            box_size = 20
            border = 1
            while version is None:
                try:
                    qr = qrcode.QRCode(version=version, box_size=box_size, border=border)
                    qr.add_data(link)
                    qr.make(fit=True)
                    version = qr.version
                except ValueError:
                    # if the QR code library raises a ValueError, increase the box size and try again
                    box_size += 5
                    if box_size > 100:
                        # if the box size gets too large, exit the loop and raise an error
                        break

            if version is None:
                self.error_popup(self, "Failed to generate QR code for " + name + ".")

            # define the output directory
            output_directory = 'qrcodes/'

            # save the QR code as a PNG file
            valid_chars = '-_.() %s%s' % (string.ascii_letters, string.digits)
            filename = f'{output_directory}/qr_{re.sub(r"[^%s]" % valid_chars, "", name.strip())[:40]}.png'
            img = qr.make_image(fill_color='black', back_color='white')
            img.save(filename)
        
        failed_tests = []
        for file in os.listdir('qrcodes'):
            print(file)
            if file.endswith('.png'):
                result = self.qrtest(file)
                if not result[1]:
                    failed_tests.append(result[0])
        if len(failed_tests) == 0:
            self.success_popup()
        else:
            self.error_popup(failed_tests)

    def qrtest(self, file):
        """
        Test a generated QR code and return the result.
        Args:
            file (str): Path to the image file containing the QR code.
        Returns:
            Tuple[str, bool]: A tuple containing the file name and a boolean indicating whether the test passed or failed.
        """
        try:
            # Decode the QR code in the image file and extract the link
            img = Image.open(f'qrcodes/{file}')
            link = decode(img)[0].data.decode('utf-8')
            # Check if the decoded link matches the expected link
            if link.strip() == '':
                return (file, False)
            else:
                return (file, True)
        except Exception:
            # Return a failed result if decoding fails
            return (file, False)

root = tk.Tk()
app = QRGeneratorApp(root)
root.mainloop()
