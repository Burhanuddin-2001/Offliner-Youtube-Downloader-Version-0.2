import logging
from threading import Thread
from pathlib import Path
from shutil import rmtree

import tkinter
import customtkinter
from moviepy.editor import AudioFileClip, VideoFileClip
from proglog import ProgressBarLogger
from pytube import YouTube
from pytube.exceptions import PytubeError
from psutil import cpu_count
from os import listdir

# Configure logging
logging.basicConfig(level=logging.INFO)
log_logger = logging.getLogger(__name__)


class MyBarLogger(ProgressBarLogger):
    def __init__(self, progress_bar, progress_percent):
        super().__init__()
        self.progress_bar = progress_bar
        self.progress_percent = progress_percent

    def bars_callback(self, bar, attr, value, old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        self.progress_bar.set(percentage/100)
        self.progress_bar.update_idletasks()
        self.progress_percent.configure(text=f"{percentage:.0f}%")
        self.progress_percent.update_idletasks()


def mixer(video_path, audio_path, output_path, progress_bar, progress_percent):
    log_logger = logging.getLogger(__name__)
    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        video = video.set_audio(audio)
        logger = MyBarLogger(progress_bar, progress_percent)
        video.write_videofile(output_path, threads=cpu_count(
            logical=False), logger=logger)
        default = Path.cwd()
        rmtree(default / "video")
        rmtree(default / "audio")
    except Exception as e:
        log_logger.error(f"An error occurred during mixing: {e}")
        progress_percent.configure(text=f"Error: {str(e)}")

# GUI section
class DownloaderApp:
    def __init__(self):
        self.app = customtkinter.CTk()
        self.app.geometry("450x380")
        self.app.title("Offliner")
        self.setup_main_window()

    def setup_main_window(self):
        self.title = customtkinter.CTkLabel(
            self.app, text="Insert Your Youtube Link here!:)", font=("Tekton Pro Cond",  20))
        self.title.pack(padx=10, pady=30)

        self.url_var = tkinter.StringVar()
        link = customtkinter.CTkEntry(
            self.app, width=350, height=40, textvariable=self.url_var)
        link.pack(pady=10)

        download_button = customtkinter.CTkButton(
            self.app, text="Download", width=200, height=40, command=self.download_function, corner_radius=5)
        download_button.pack(padx=15, pady=15)

        self.finish_label = customtkinter.CTkLabel(self.app, text="")
        self.finish_label.pack(pady=10)

        self.progress_bar = customtkinter.CTkProgressBar(self.app, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(side=tkinter.BOTTOM, padx=20, pady=20)

        self.progress_percent = customtkinter.CTkLabel(self.app, text="0%")
        self.progress_percent.pack(side=tkinter.BOTTOM)

    def on_progress(self, stream, chunks, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - int(bytes_remaining)
        percentage = (bytes_downloaded / total_size) * 100
        self.progress_bar.set(percentage/100)
        self.progress_bar.update_idletasks()
        self.progress_percent.configure(text=f"{percentage:.0f}%")
        self.progress_percent.update_idletasks()
        if percentage == 100:
            self.finish_label.configure(text="Downloading Finished!")

    def setup_download_window(self):
        self.app.withdraw()
        self.download_window = customtkinter.CTkToplevel(self.app)
        self.download_window.geometry("450x380")
        self.download_window.title("Download Window")
        self.download_window.lift()

        DQ_new_lable = customtkinter.CTkLabel(
            self.download_window, text="Choose Download Quality For The Video.", font=("Tekton Pro Cond",  32), wraplength=300)
        DQ_new_lable.pack(padx=30, pady=30)
        progressive = [f"{keys} Fast" for keys in self.return_list[0]]
        non_progressive = [f"{keys} Slow" for keys in self.return_list[1]]
        progressive.extend(non_progressive)

        self.combobox = customtkinter.CTkOptionMenu(master=self.download_window, values=[values for values in progressive], anchor="center", font=(
            "Tekton Pro Cond",  20), dropdown_font=("Tekton Pro Cond",  18), width=300, height=30, corner_radius=5, dynamic_resizing=True)
        self.combobox.pack(padx=50, pady=10)

        Selection_button = customtkinter.CTkButton(master=self.download_window, text="Download", font=(
            "Tekton Pro Cond",  20), corner_radius=5, width=200, height=20, command=lambda: self.download_main_selected_stream())
        Selection_button.pack(padx=50, pady=15)

        self.download_window.bind("<Destroy>", self.close_main_window)

    # Pytube section
    def download_function(self):
        try:
            self.ytObject = YouTube(
                self.url_var.get(), on_progress_callback=self.on_progress)
            available_streams = self.ytObject.streams
            self.title.configure(text=self.ytObject.title)
            pro_dict = dict()
            non_pro_video_dict = dict()
            audio_dict = dict()
            for stream in available_streams:
                if stream.is_progressive:
                    pro_dict[stream.resolution] = stream.itag
                elif stream.type == "audio":
                    audio_dict[stream.abr] = stream.itag
                else:
                    non_pro_video_dict[stream.resolution] = stream.itag

            max_stream_audio = float("-inf")
            temp_audio = []
            for stream in audio_dict:
                temp = int(stream[:stream.index("k")])
                if temp > max_stream_audio:
                    max_stream_audio = temp
                    temp_audio = [stream, audio_dict[stream]]
            self.audio = temp_audio[1]
            self.return_list = [pro_dict, non_pro_video_dict, temp_audio]
            self.setup_download_window()
        except PytubeError as e:
            log_logger.error(f"An error occurred during downloading: {e}")
            self.progress_percent.configure(text=f"Error: {str(e)}")

    def download_main_selected_stream(self):
        self.download_window.withdraw()
        self.app.deiconify()
        selected = self.combobox.get()[:self.combobox.get().index(" ")]
        download_thread = Thread(
            target=self.download_video, args=(selected,))  # Create a new thread
        download_thread.start()

    def download_video(self, selected):
        output_path = Path.home() / "Downloads" / "Youtube Videos"
        self.finish_label.configure(text="Downloading.......")
        if selected in self.return_list[0]:
            file = self.ytObject.streams.get_by_itag(
                self.return_list[0][selected])
            file.download(output_path)
        else:
            file = self.ytObject.streams.get_by_itag(
                self.return_list[1][selected])
            default = Path.cwd()
            video_file_path = default / "video"
            audio_file_path = default / "audio"
            file.download(video_file_path)
            file2 = self.ytObject.streams.get_by_itag(self.audio)
            file2.download(audio_file_path)

            def select_single_file(dir_path):
                files = listdir(dir_path)
                if len(files) == 1:
                    return files[0]
                else:
                    return None

            dir_path = video_file_path
            label = select_single_file(dir_path)
            vd_path = str(video_file_path / label)
            ad_path = str(audio_file_path /
                          select_single_file(audio_file_path))
            label = f"{label[:label.rfind('.')]}.mp4"
            self.finish_label.configure(text="Processing The Video.......")
            mixer(vd_path, ad_path, str(output_path / label),
                  self.progress_bar, self.progress_percent)
            self.finish_label.configure(text="Finished!:)")

    def close_main_window(self,event):
        self.app.quit()


if __name__ == "__main__":
    app = DownloaderApp()
    app.app.mainloop()
