'''"""
This project will be complicated, with multiple working parts.
I'll make a prototype first, proof of concept which will be minimally functional to prove the idea works.
The idea: A tool which will reveal satellites in photos taken of the sky.

I want to see whats invisible but def in the sky when I look up, so I'll code a tool to do that.

It will be a windowed app which will have a prompt to open a photo for analysis.
When selected, the photo will be processed for information neccecary to do the calcs.
If information is missing, the user will be prompted to enter it during this time.
Once all the info is determined, that input info will be used to narrow down the search for satellites.
And then thats the analysis which will then occur heavily,
And then the photo will be displayed with calculated probable hits for satellites,
and the ~x,y coords charted on the image.

Now, how will the calcs work?
Metadata contains a lot of vital info specifically
Location and time. Other stuff like camera settings can be ignored for this prototype.
Using the exact time of when the photo was taken, we can use the location history of all satellites in orbit to
where they all were in the sky at that exact time. Next, we can use the exact long/lat of the photo to determine 
the approximate region the photo was taken in. Using this info, we can determine which satellites may have been
visible in the sky then. This is purely using location math, not visual analysis. 
The next step would be to filter out the satellites which are definetly NOT in the captured region of the sky,
thats hard. One way is using absolute compass direction and somehow figuring out how angled upwards the camera
was while taking the photo, but I don't think thats possible. So, I could maybe use multiple steps to cull and crop
out culled satellites... maybe theres more info in the metadata and location info that could be pulled to
figure out the angle of the camera?

"""

# first things first, lets open the app window and prompt the user to open a photo

import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import time
from PIL.ExifTags import TAGS, GPSTAGS

def convert_to_decimal(coord):
    return coord.numerator / coord.denominator

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Watch The Skies")
        self.img = None

        # button to open image with size and pos set
        self.btn = tk.Button(self.root, text="Open Image", command=self.prompt_file_img)
        self.btn.pack()

        # righthand sidebar to display info
        self.info = tk.Frame(self.root, bg="white")
        self.info.pack(side="right", fill="none", expand=False)
        self.info.configure(width=400)  # Set minimum width of the sidebar to 200 pixels

        # sidebar title
        self.info_title = tk.Label(self.info, text="Image Info", bg="white")
        self.info_title.pack()

        # sidebar has 2 columns of info, left is labels right is values
        self.info_labels = tk.Frame(self.info, bg="white")
        self.info_labels.pack(side="left", fill="both", expand=True)
        self.info_values = tk.Frame(self.info, bg="white")
        self.info_values.pack(side="right", fill="both", expand=True)

        # in left column, name of infos longitude, latitude, date, time, altitude
        self.info_label_long = tk.Label(
            self.info_labels, text="Longitude:", bg="white", wraplength=200
        )
        self.info_label_long.pack(anchor="w")
        self.info_label_lat = tk.Label(
            self.info_labels, text="Latitude:", bg="white", wraplength=200
        )
        self.info_label_lat.pack(anchor="w")
        self.info_label_date = tk.Label(
            self.info_labels, text="Date:", bg="white", wraplength=200
        )
        self.info_label_date.pack(anchor="w")
        self.info_label_time = tk.Label(
            self.info_labels, text="Time:", bg="white", wraplength=200
        )
        self.info_label_time.pack(anchor="w")
        self.info_label_alt = tk.Label(
            self.info_labels, text="Altitude:", bg="white", wraplength=200
        )
        self.info_label_alt.pack(anchor="w")

        # in right column, values of infos longitude, latitude, date, time, altitude
        self.info_value_long = tk.Label(
            self.info_values, text=" ", bg="white", wraplength=200
        )
        self.info_value_long.pack(anchor="w")
        self.info_value_lat = tk.Label(
            self.info_values, text=" ", bg="white", wraplength=200
        )
        self.info_value_lat.pack(anchor="w")
        self.info_value_date = tk.Label(
            self.info_values, text=" ", bg="white", wraplength=200
        )
        self.info_value_date.pack(anchor="w")
        self.info_value_time = tk.Label(
            self.info_values, text=" ", bg="white", wraplength=200
        )
        self.info_value_time.pack(anchor="w")
        self.info_value_alt = tk.Label(
            self.info_values, text=" ", bg="white", wraplength=200
        )
        self.info_value_alt.pack(anchor="w")

        self.canvas = tk.Canvas(
            self.root, width=600, height=400
        )  # Set the initial size of the canvas
        self.canvas.pack(
            fill="both", expand=True
        )  # Fill the entire window with the canvas
        self.canvas.pack()



    def open_img(self):
        if not self.img_path:
            return
        img = Image.open(self.img_path)
        img = img.resize(
            (self.canvas.winfo_width(), self.canvas.winfo_height())
        )  # Scale the image to fit the canvas size
        self.img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)

        exif_data = self.get_exif_data(self.img_path)
        lat_lon = self.get_lat_lon(exif_data)
        
        if lat_lon:
            lat = convert_to_decimal(lat_lon[0])
            lon = convert_to_decimal(lat_lon[1])
            
            print("Latitude:", lat)
            print("Longitude:", lon)
            # put the lat and lon in the info sidebar
            self.info_value_lat.config(text=lat)
            self.info_value_long.config(text=lon)
            
        else:
            print("No GPS metadata found.")

    def get_exif_data(self, image_path):
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            if exif_data is not None:
                exif_data_decoded = {
                    TAGS.get(tag, tag): value for tag, value in exif_data.items()
                }
                if "GPSInfo" in exif_data_decoded:
                    gps_info = {}
                    for tag, value in exif_data_decoded["GPSInfo"].items():
                        tag_name = GPSTAGS.get(tag, tag)
                        gps_info[tag_name] = value
                    return gps_info
                else:
                    return None
            else:
                return None
        except Exception as e:
            print("Error:", e)
            return None

    def get_lat_lon(self, exif_data):
        if exif_data is not None:
            lat = exif_data.get("GPSLatitude")
            lon = exif_data.get("GPSLongitude")
            if lat and lon:
                lat_ref = exif_data.get("GPSLatitudeRef", "N")
                lon_ref = exif_data.get("GPSLongitudeRef", "W")
                lat_val = lat[0] + lat[1] / 60 + lat[2] / 3600
                lon_val = lon[0] + lon[1] / 60 + lon[2] / 3600
                if lat_ref == "S":
                    lat_val = -lat_val
                if lon_ref == "E":
                    lon_val = -lon_val
                return lat_val, lon_val
            else:
                return None
        else:
            return None

    def prompt_file_img(self):
        self.img_path = filedialog.askopenfilename()
        self.open_img()

    def dev_open_img(self, img_path):
        self.img_path = img_path
        self.open_img()


root = tk.Tk()
app = App(root)
app.dev_open_img(
    "C:/Users/aiden/OneDrive/Pictures/Screenshots/iCloud Photos from Aiden Okrent/IMG_8653.JPG")
root.mainloop()
'''