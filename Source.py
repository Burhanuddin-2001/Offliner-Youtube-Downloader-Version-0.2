# Importing required modules
import tkinter
import threading
import customtkinter  # use mainly to make UI nicer over the tkinter module
from os import getcwd, path, makedirs  # to get path of current directory
from pytube import YouTube

# download function


def downloadVideo():
    try:

        # grab the Youtube link
        ytLink = link.get()

        # create a Youtube video object
        ytObject = YouTube(
            ytLink, on_progress_callback=Updating_progress_bar)

        # reset title to show the video title
        title.configure(text=ytObject.title, text_color="white")
        finish_label.configure(text="")

        # Create a video stream object of highest quality
        video = ytObject.streams.get_highest_resolution()

        # Finally download that video to this folder
        folder_path = getcwd() #Get the path of current working directory/folder
        output_path = folder_path+"\Download" #create a download folder in current directory
        if path.isdir(output_path):
            video.download(output_path)
        else:
            makedirs(output_path)
            video.download(output_path)

    except Exception as e:
        print(f"The error occurs is:\n{e}")  # for terminal
        finish_label.configure(text="Download Error", text_color="red")

    else:
        finish_label.configure(text="Download Complete!",
                               text_color="white")  # for app UI
        url_var.set("")


def startDownload():
    progress_Percentage.pack()
    progress_bar.pack()
    threading.Thread(target=downloadVideo).start()

# Progress bar updation function
def Updating_progress_bar(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = (bytes_downloaded/total_size)*100
    percent = str(int(percentage_of_completion))

    # update progress percentage
    progress_Percentage.configure(text=percent+"%")
    progress_Percentage.update_idletasks()

    # update progress bar
    progress_bar.set(percentage_of_completion/100)
    progress_bar.update_idletasks()


# System settings
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

# Our app frame
app = customtkinter.CTk()
app.geometry("480x320") #setting a custom app window size 
app.title("Youtube Downloader")

# Adding UI elements
title = customtkinter.CTkLabel(
    app, text="Insert the Youtube Link", font=("Tekton Pro Cond", 20))
title.pack(padx=10, pady=10)

# Link input
# use to create a text variable to store to the input link provided by the user
url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_var)
link.pack(pady=10)

# Finished label
finish_label = customtkinter.CTkLabel(app, text="")
finish_label.pack(pady=10)

# Download Button
download = customtkinter.CTkButton(
    app, text="Download", command=startDownload, width=200, height=40)
download.pack(padx=15, pady=15)

# Progress Percentage
progress_Percentage = customtkinter.CTkLabel(app, text="0%")
# Move to bottom of window
progress_Percentage.pack(side=tkinter.BOTTOM, pady=10)
progress_Percentage.pack_forget()

# ProgressBar
progress_bar = customtkinter.CTkProgressBar(app, width=400)
progress_bar.set(0)
progress_bar.pack(side=tkinter.BOTTOM, padx=40)  # Move to bottom of window
progress_bar.pack_forget()

# Run app
app.mainloop()
