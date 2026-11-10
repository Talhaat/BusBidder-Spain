# File location for gui using customtkinter

import customtkinter as ctk

import datagen
import journey
import loader
import price
from gui.map_view import show_map

# Dark mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def run():
    data = datagen.generate_data()

    # Main window: sidebar on the left(burger menue)
    window = ctk.CTk()
    window.title("BusBidder Spain")
    window.geometry("900x600")

    sidebar = ctk.CTkFrame(window, width=160)
    sidebar.pack(side="left", fill="y")

    content = ctk.CTkFrame(window)
    content.pack(side="right", fill="both", expand=True)

    def clear_content():
        for widget in content.winfo_children():
            widget.destroy()

    def open_map():
        show_map(
            data["connections"], data["coordinates"], data["madrid_x"], data["madrid_y"],
            data["company_colors"], data["canvas_width"], data["canvas_height"]
        )
        loader.save_coords(data["coordinates"])

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

        ctk.CTkLabel(pickers_row, text="->", font=ctk.CTkFont(size=20)).pack(side="left", padx=5, pady=20)

        finish_column = ctk.CTkFrame(pickers_row, fg_color="transparent")
        finish_column.pack(side="left", padx=10)
        ctk.CTkLabel(finish_column, text="Finish").pack()
        finish_picker = ctk.CTkOptionMenu(finish_column, values=all_points)
        finish_picker.pack(pady=5)

        time_column = ctk.CTkFrame(pickers_row, fg_color="transparent")
        time_column.pack(side="left", padx=10)
        ctk.CTkLabel(time_column, text="Time").pack()
        time_picker = ctk.CTkOptionMenu(time_column, values=[f"{hour:02d}:00" for hour in range(24)])
        time_picker.set("08:00")
        time_picker.pack(pady=5)

        results_frame = ctk.CTkFrame(content)
        results_frame.pack(pady=10, fill="both", expand=True)

        def find_buses():
            for widget in results_frame.winfo_children():
                widget.destroy()

            start = start_picker.get()
            finish = finish_picker.get()
            travel_time = time_picker.get()

            options = price.get_route_options(
                start, finish, data["coordinates"],
                data["madrid_x"], data["madrid_y"], data["companies"], travel_time
            )
            options = journey.filter_by_time(options, travel_time)

            if options:
                for offer in options:
                    ctk.CTkLabel(results_frame, text=str(offer)).pack(anchor="w")
                return

            transfers = journey.get_transfer_options(
                start, finish, data["coordinates"],
                data["madrid_x"], data["madrid_y"], data["companies"], travel_time
            )
            transfers = journey.filter_by_time(transfers, travel_time)

            if not transfers:
                ctk.CTkLabel(results_frame, text="No bus on this route at this time").pack()
                return

            ctk.CTkLabel(results_frame, text="No direct bus - recommended transfers via Madrid:").pack(anchor="w")
            for offer in sorted(transfers, key=lambda offer: offer.price):
                ctk.CTkLabel(results_frame, text=str(offer)).pack(anchor="w")

        ctk.CTkButton(content, text="Find buses", command=find_buses).pack(pady=10)

    def show_companies_page():
        clear_content()

        for company in data["companies"]:
            ctk.CTkLabel(content, text=f"{company.name}: {company.profile.description} (Price range: {company.profile.min_price}-{company.profile.max_price} EUR)").pack(anchor="w", pady=5)

    # Sidebar buttons(burger menu)
    ctk.CTkButton(sidebar, text="Map", command=open_map).pack(pady=10, padx=10)
    ctk.CTkButton(sidebar, text="Bus Search", command=show_search_page).pack(pady=10, padx=10)
    ctk.CTkButton(sidebar, text="Bus Companies", command=show_companies_page).pack(pady=10, padx=10)

    window.mainloop()

if __name__ == "__main__":
    run()
