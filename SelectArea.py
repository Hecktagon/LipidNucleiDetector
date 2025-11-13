import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw


"""
Allows user to select multiple areas within an image using left click and drag,
and deselect areas using right click. Returns a list of coordinates for the selected areas.
"""
class ImageCoordinateSelector:
    def __init__(self, root, image_path=None):
        self.root = root
        self.root.title("Press X When Area is Selected")
        self.image_path = image_path
        self.image = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.all_coords = []
        self.selection_rectangle = None
        self.all_rectangles = []
        self.resize_ratio = 1

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # LEFT CLICK
        self.canvas.bind("<ButtonPress-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_click_release)
        # RIGHT CLICK
        self.canvas.bind("<ButtonPress-3>", self.on_right_click)
        # CLOSE
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.load_image()

    def load_image(self):
        if self.image_path is None:
            file_path = filedialog.askopenfilename()
            self.image_path = file_path
        else:
            file_path = self.image_path
        if file_path:
            self.image = Image.open(file_path)
            self.render_image()

    def render_image(self):
        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Get the original image dimensions
        original_width, original_height = self.image.size

        # Calculate the resizing ratio
        width_ratio = (screen_width / original_width) * 0.75
        height_ratio = (screen_height / original_height) * 0.75
        self.resize_ratio = min(width_ratio, height_ratio)

        # New dimensions for the image
        new_width = int(original_width * self.resize_ratio)
        new_height = int(original_height * self.resize_ratio)
        size = (new_width, new_height)

        # Resize the image
        self.image = self.image.resize(size)
        self.tk_image = ImageTk.PhotoImage(self.image)

        # Set canvas dimensions to match the resized image
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def scale_coords(self, coords):
        return [round(x/self.resize_ratio) for x in coords]

    def on_left_click(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.selection_rectangle = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        self.canvas.coords(self.selection_rectangle, self.start_x, self.start_y, event.x, event.y)

    def on_left_click_release(self, event):
        self.end_x = event.x
        self.end_y = event.y
        self.all_coords.append(self.scale_coords([self.start_x, self.start_y, self.end_x, self.end_y]))
        self.all_rectangles.append(self.selection_rectangle)
        # print(f"Start coords: ({self.start_x}, {self.start_y})\nEnd coords: ({self.end_x}, {self.end_y})")

    def on_right_click(self, event):
        if len(self.all_rectangles) > 0:
            self.canvas.delete(self.all_rectangles.pop())
            self.all_coords.pop()

    def on_close(self):
        self.save_canvas_as_image()
        self.root.destroy()

    def save_canvas_as_image(self):
        output_file = f"SelectedAreaImages\\{self.image_path.split("/")[-1].split("\\")[-1]}_selected_areas.png"
        output_dir = 'SelectedAreaImages'
        os.makedirs(output_dir, exist_ok=True)  # Creates selected areas directory if it doesn't exist

        # Create a new image with the same size as canvas, and draw the image on it.
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image = self.image
        draw = ImageDraw.Draw(image)

        # Get all the items on the canvas and draw them onto the image
        for item in self.canvas.find_all():
            coords = self.canvas.coords(item)
            if self.canvas.type(item) == "rectangle":
                draw.rectangle(coords, outline="red")  # Change as needed based on your drawing

        # Save the image
        image.save(output_file, 'PNG')
        print(f"Canvas saved as {output_file}")



# arranges coordinates of rectangle corners so that the first pair is the top left corner
def order_coords(coords):
    if coords[0] > coords[2]:
        coords[0], coords[2] = coords[2], coords[0]
    if coords[1] > coords[3]:
        coords[1], coords[3] = coords[3], coords[1]


"""
Allows the user to select multiple areas, then returns the coordinates 
for the corners of those areas in a 2D list.
"""
def select_areas(image_path = None):
    root = tk.Tk()
    area_selector = ImageCoordinateSelector(root, image_path)
    root.mainloop()
    coords = area_selector.all_coords
    for coord in coords:
        order_coords(coord)
    return coords


if __name__ == "__main__":
    print(select_areas())