# Data generation for project

# Libraries
import random
import csv
import tkinter as tk

#Placing destination on map


canvas_width = 600
canvas_height = 400


with open("destination.csv") as file:
    reader = csv.DictReader(file)
    destinations = [row["destination"] for row in reader]

coordinates = {}


for destination in destinations:
    x = random.randint(0, canvas_width)
    y = random.randint(0, canvas_height)
    coordinates[destination] = (x, y)

# Show the map in a window
window = tk.Tk()
canvas = tk.Canvas(window, width=canvas_width, height=canvas_height)
canvas.pack()

for destination, (x, y) in coordinates.items():
    canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="blue")
    canvas.create_text(x, y - 10, text=destination)

window.mainloop()