import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time
import sys
from pathlib import Path
from tkinter import filedialog

MIN_PYTHON_VERSION = (3, 11)

current_version = sys.version_info[:2]

if current_version < MIN_PYTHON_VERSION:
    raise ValueError(
        f"Внимание! Строго рекомендуется использовать python версии {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} или выше\n"
        "в связи с переработанной функцией time.sleep() в этой версии.\n"
        "Работа с python более старой версии приведет к неверной частоте кадров видео."
    )


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.window_width = round(self.root.winfo_screenwidth() * 0.842)
        self.window_height = round(self.root.winfo_screenheight() * 0.861)
        self.root.geometry(f"{self.window_width}x{self.window_height}")

        x = (self.screen_width - self.window_width) // 2
        y = (round(0.87 * self.screen_height) - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

        self.player = VideoPlayer(self)

        self.video_label = tk.Label(
            self.root,
            width=round(self.window_width * 0.854),
            height=round(self.window_height * 0.800),
        )
        self.video_label.pack()

        self.pause_button = tk.Button(
            self.root,
            width=round(self.window_width * 0.016),
            height=round(self.window_height * 0.0025),
            text="Pause",
            command=self.player.toggle_pause,
        )
        self.pause_button.config(font=("Courier", 13))
        self.pause_button.pack()

        self.scale = tk.Scale(
            self.root,
            from_=0,
            to=int(self.player.duration),
            orient=tk.HORIZONTAL,
            length=round(self.window_width * 0.375),
            command=self.on_scale_change,
        )
        self.scale.config(font=("Courier", 11))
        self.scale.pack()

        self.duration_label = tk.Label(
            self.root, text=f"Duration: {round(self.player.duration)} seconds"
        )
        self.duration_label.config(font=("Courier", 13))
        self.duration_label.pack(side="right", padx=round(self.window_width * 0.313))

        self.programmatic_scale_change = False

    def on_scale_change(self, seconds_number):
        if not self.programmatic_scale_change:
            self.player.jump_to_frame(float(seconds_number))


class VideoPlayer:
    def __init__(self, win):
        self.win = win
        self.vid = cv2.VideoCapture(str(self.get_video_path()))
        self.paused = False
        self.stop = False
        self.sleep_time = 0

        if win.screen_width > 1400:
            self.fps_label_k1 = 0.00625
            self.fps_label_k2 = 0.05555
        else:
            self.fps_label_k1 = 0.25
            self.fps_label_k2 = 0.25

        self.frame_rate = self.vid.get(cv2.CAP_PROP_FPS)
        self.frame_count = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.duration = self.frame_count / self.frame_rate
        self.current_frame = 0

        if self.frame_rate == 0:
            self.frame_rate = 25
            self.frame_time = 1 / self.frame_rate
        else:
            self.frame_time = 1 / self.frame_rate

    def get_video_path(self):
        video_path = None
        list_args = sys.argv
        if len(list_args) > 1:
            video_path = Path(list_args[1])

        if video_path is None:
            video_path = Path(
                filedialog.askopenfilename(
                    title="Select video", filetypes=[("Video", ".mp4 .avi")]
                )
            )

        if video_path == Path('.'):
            sys.exit()

        return video_path

    def update_frame(self):
        if not self.paused:
            ret, frame = self.vid.read()
            if ret:
                fps_text = "FPS: {:.2f}".format(self.frame_rate)
                cv2.putText(
                    frame, fps_text, (round(win.window_width*self.fps_label_k1), round(win.window_height*self.fps_label_k2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
                )
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                try:
                    self.imgtk = ImageTk.PhotoImage(image=img)
                except RuntimeError:
                    sys.exit()
                self.win.video_label.config(image=self.imgtk)
                self.win.root.update()
                self.current_frame += 1
            else:
                self.win.video_label.config(image=self.imgtk)
                self.win.root.update()
        elif self.stop:
            self.win.video_label.config(image=self.imgtk)
            self.win.root.update()
            self.stop = False
        else:
            time.sleep(0.02)
            self.win.root.update()

    def toggle_pause(self):
        self.stop = True
        if self.paused:
            self.win.pause_button.config(text='Pause')
        else:
            self.win.pause_button.config(text='Play')
        self.paused = not self.paused

    def jump_to_frame(self, seconds_number):
        self.current_frame = seconds_number * self.frame_rate
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

        ret, frame = self.vid.read()
        if ret:
            fps_text = "FPS: {:.2f}".format(self.frame_rate)
            cv2.putText(
                frame, fps_text, (round(win.window_width*self.fps_label_k1), round(win.window_height*self.fps_label_k2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            try:
                self.imgtk = ImageTk.PhotoImage(image=img)
            except RuntimeError:
                sys.exit()
            self.win.video_label.config(image=self.imgtk)
            self.win.root.update()
        else:
            self.win.video_label.config(image=self.imgtk)
            self.win.root.update()

    def play(self):
        while True:
            cur_time1 = time.perf_counter()
            self.update_frame()
            current_time = self.current_frame / self.frame_rate
            self.win.programmatic_scale_change = False
            if current_time.is_integer():
                try:
                    self.win.scale.set(current_time)
                except tk.TclError:
                    sys.exit()
                if not self.paused:
                    self.win.programmatic_scale_change = True
            delta = time.perf_counter() - cur_time1
            self.sleep_time = self.frame_time - delta
            if self.sleep_time > 0:
                time.sleep(self.sleep_time)


win = MainWindow()
win.player.play()
win.root.mainloop()