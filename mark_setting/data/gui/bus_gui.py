# Bus GUI - the main app window, with a sidebar menu for Map and Bus Search

import customtkinter as ctk

import datagen
import loader
import price
from gui.map_view import show_map

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


#Function to run the whole application
# Input is none, return is none, opens the main window and blocks until closed.
def run():
    data = datagen.generate_data()

    window = ctk.CTk()
    window.title("BusBidder Spain")
    window.geometry("900x600")

    sidebar = ctk.CTkFrame(window, width=160)
    sidebar.pack(side="left", fill="y")

    content = ctk.CTkFrame(window)
    content.pack(side="right", fill="both", expand=True)

    #Function to clear whatever is currently shown in the content area
    # Input is none, return is none.
    def clear_content():
        for widget in content.winfo_children():
            widget.destroy()

    #Function to open the map in its own window
    # Input is none, return is none.
    def open_map():
        show_map(
            data["connections"], data["coordinates"], data["madrid_x"], data["madrid_y"],
            data["company_colors"], data["canvas_width"], data["canvas_height"]
        )
        loader.save_coordinates(data["coordinates"])

    #Function to show the bus search page: pick a start and finish, see companies and prices
    # Input is none, return is none.
    def show_search_page():
        clear_content()

        all_points = ["Madrid"] + data["destinations"]

        pickers_row = ctk.CTkFrame(content, fg_color="transparent")
        pickers_row.pack(pady=10)

        start_column = ctk.CTkFrame(pickers_row, fg_color="transparent")
        start_column.pack(side="left", padx=10)
        ctk.CTkLabel(start_column, text="Start").pack()
        start_picker = ctk.CTkOptionMenu(start_column, values=all_points)
        start_picker.set("Madrid")
        start_picker.pack(pady=5)

        ctk.CTkLabel(pickers_row, text="→", font=ctk.CTkFont(size=20)).pack(side="left", padx=5, pady=20)

        finish_column = ctk.CTkFrame(pickers_row, fg_color="transparent")
        finish_column.pack(side="left", padx=10)
        ctk.CTkLabel(finish_column, text="Finish").pack()
        finish_picker = ctk.CTkOptionMenu(finish_column, values=all_points)
        finish_picker.pack(pady=5)

        results_frame = ctk.CTkFrame(content)
        results_frame.pack(pady=10, fill="both", expand=True)

        #Function to look up and display bus options for the picked start and finish
        # Input is none, return is none.
        def find_buses():
            for widget in results_frame.winfo_children():
                widget.destroy()

            start = start_picker.get()
            finish = finish_picker.get()
            options = price.get_route_options(
                start, finish, data["connections"], data["coordinates"],
                data["madrid_x"], data["madrid_y"], data["companies"]
            )

            if not options:
                ctk.CTkLabel(results_frame, text="No companies serve this route").pack()
                return

            for company_name, option_price in options:
                ctk.CTkLabel(results_frame, text=f"{company_name}: {option_price} EUR").pack(anchor="w")

        ctk.CTkButton(content, text="Find buses", command=find_buses).pack(pady=10)

    ctk.CTkButton(sidebar, text="Map", command=open_map).pack(pady=10, padx=10)
    ctk.CTkButton(sidebar, text="Bus Search", command=show_search_page).pack(pady=10, padx=10)

    window.mainloop()


if __name__ == "__main__":
    run()
