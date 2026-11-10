# Map view - window, drawing and hover highlighting for the bus route map

import tkinter as tk
import customtkinter as ctk

from routes import minimum_spanning_tree

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

normal_width = 2
weak_width = 1
highlight_width = 5
weak_color = "#555555"


#Function to open a window showing Madrid, destinations and bus routes, with hover highlighting
# Input is connections dict, coordinates dict, Madrid's x and y, company colours dict, canvas size.
# Return is none, opens the window and blocks until it is closed.
def show_map(connections, coordinates, madrid_x, madrid_y, company_colors, canvas_width, canvas_height):
    window = ctk.CTk()
    window.title("BusBidder Spain - Route Map")

    canvas_background = "#242424"
    canvas = tk.Canvas(window, width=canvas_width, height=canvas_height, bg=canvas_background, highlightthickness=0)
    canvas.pack(padx=10, pady=10)


    for company, served_destinations in connections.items():
        color = company_colors.get(company, "white")
        points = {"Madrid": (madrid_x, madrid_y)}
        for destination in served_destinations:
            points[destination] = coordinates[destination]

        edges = minimum_spanning_tree(points)
        for name1, name2 in edges:
            x1, y1 = points[name1]
            x2, y2 = points[name2]
            canvas.create_line(
                x1, y1, x2, y2, fill=color, width=normal_width,
                tags=(company, "touch-" + name1, "touch-" + name2)
            )

    #Function to highlight one company's route and weaken every other route
    # Input is the company name to highlight, return is none.
    def highlight_route(company_to_highlight):
        for company in connections:
            if company == company_to_highlight:
                canvas.itemconfig(company, fill=company_colors.get(company, "white"), width=highlight_width)
                canvas.tag_raise(company)
            else:
                canvas.itemconfig(company, fill=weak_color, width=weak_width)

    #Function to highlight every line directly touching one station, weaken the rest
    # Input is the station name to highlight, return is none.
    def highlight_station(station_name):
        touching = set(canvas.find_withtag("touch-" + station_name))
        for company in connections:
            for item in canvas.find_withtag(company):
                if item in touching:
                    canvas.itemconfig(item, width=highlight_width)
                    canvas.tag_raise(item)
                else:
                    canvas.itemconfig(item, fill=weak_color, width=weak_width)

    #Function to put every route back to its normal look
    # Input is none, return is none.
    def reset_routes(event=None):
        for company in connections:
            canvas.itemconfig(company, fill=company_colors.get(company, "white"), width=normal_width)

    for company in connections:
        canvas.tag_bind(company, "<Enter>", lambda event, c=company: highlight_route(c))
        canvas.tag_bind(company, "<Leave>", reset_routes)

    #Draw Madrid itself, tagged so hovering it also highlights its direct connections
    canvas.create_oval(madrid_x - 7, madrid_y - 7, madrid_x + 7, madrid_y + 7, fill="white", tags=("Madrid",))
    canvas.create_text(madrid_x, madrid_y - 12, text="Madrid", fill="white", tags=("Madrid",))
    canvas.tag_bind("Madrid", "<Enter>", lambda event: highlight_station("Madrid"))
    canvas.tag_bind("Madrid", "<Leave>", reset_routes)

    #Draw each destination on top of the lines, tagged the same way
    for destination, (x, y) in coordinates.items():
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#4da6ff", tags=(destination,))
        canvas.create_text(x, y - 10, text=destination, fill="white", tags=(destination,))
        canvas.tag_bind(destination, "<Enter>", lambda event, d=destination: highlight_station(d))
        canvas.tag_bind(destination, "<Leave>", reset_routes)

    #Draw the legend in the top right corner: one coloured line plus name per company
    legend_x = canvas_width - 220
    legend_y = 20
    row_height = 25
    canvas.create_rectangle(
        legend_x - 10, legend_y - 10, canvas_width - 20, legend_y + 30 + len(connections) * row_height,
        fill=canvas_background, outline=weak_color
    )
    canvas.create_text(legend_x, legend_y + 5, text="Companies", fill="white", anchor="w")
    for index, company in enumerate(connections):
        y = legend_y + 35 + index * row_height
        canvas.create_line(legend_x, y, legend_x + 30, y, fill=company_colors.get(company, "white"), width=4)
        canvas.create_text(legend_x + 40, y, text=company, fill="white", anchor="w")

    window.mainloop()
