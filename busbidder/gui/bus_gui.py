# File location for gui using customtkinter

import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk

import datagen
import journey
import loader
from gui.map_view import show_map
from timing import to_time_text, to_duration_text

# Dark mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def run():
    data = datagen.generate_data()

    # Main window: sidebar on the left(burger menue)
    window = ctk.CTk()
    window.title("BusBidder Spain")
    window.geometry("900x600")

    # Plain tk labels use Tk's default font: make it the same as customtkinter's (Roboto 13)
    # Setting it once here is much faster than giving every label its own font
    tkfont.nametofont("TkDefaultFont").configure(family="Roboto", size=-13)

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

        # Preferred departure, not used yet: the ranking will use it
        time_column = ctk.CTkFrame(pickers_row, fg_color="transparent")
        time_column.pack(side="left", padx=10)
        ctk.CTkLabel(time_column, text="Preferred time").pack()
        time_picker = ctk.CTkOptionMenu(time_column, values=[f"{hour:02d}:00" for hour in range(24)])
        time_picker.set("08:00")
        time_picker.pack(pady=5)

        # Filters under the pickers: luggage and minimum rating
        filters_row = ctk.CTkFrame(content, fg_color="transparent")
        filters_row.pack(pady=5)

        # Luggage: when ticked, only show buses that take luggage
        luggage_box = ctk.CTkCheckBox(filters_row, text="I need luggage")
        luggage_box.pack(side="left", padx=10)

        # Minimum rating: hide companies rated lower, 0 = no limit
        ctk.CTkLabel(filters_row, text="Minimum rating").pack(side="left", padx=(20, 5))
        rating_picker = ctk.CTkOptionMenu(filters_row, values=["0", "1", "2", "3", "4", "5"], width=70)
        rating_picker.set("0")
        rating_picker.pack(side="left")

        results_frame = ctk.CTkScrollableFrame(content)
        results_frame.pack(pady=10, fill="both", expand=True)

        # Offers as a table: bold header row, then one row per offer
        def show_table(offers, first_row, with_wait):
            headers = ["Company", "Rating", "Price", "Departs", "Arrives", "Seats"]
            if with_wait:
                headers = ["Company", "Rating", "Price", "Departs", "Arrives", "Wait in Madrid", "Seats"]
            # Plain tk labels: much faster than CTkLabel when there are hundreds of cells
            # Same colours as the customtkinter dark theme, the font is set once in run()
            table_bg = "gray20"
            text_color = "#DCE4EE"
            bold = ctk.CTkFont(weight="bold")
            for col in range(len(headers)):
                tk.Label(results_frame, text=headers[col], font=bold, bg=table_bg, fg=text_color, pady=5).grid(row=first_row, column=col, padx=10, sticky="w")

            row = first_row + 1
            for offer in offers:
                # Transfers show both companies and ratings, like SolRuta -> CostaLink, 3.8 / 4.2
                names = []
                ratings = []
                for company in offer.companies:
                    names.append(company.name)
                    ratings.append(str(company.profile.rating))

                values = [" -> ".join(names), " / ".join(ratings), f"{offer.price} EUR", to_time_text(offer.departure), to_time_text(offer.arrival)]
                if with_wait:
                    values.append(to_duration_text(offer.wait))
                values.append(offer.seats)

                for col in range(len(values)):
                    tk.Label(results_frame, text=str(values[col]), bg=table_bg, fg=text_color, pady=5).grid(row=row, column=col, padx=10, sticky="w")
                row += 1

        def find_buses():
            for widget in results_frame.winfo_children():
                widget.destroy()

            start = start_picker.get()
            finish = finish_picker.get()
            min_rating = int(rating_picker.get())

            options = journey.get_direct_offers(data["offers"], start, finish)
            if luggage_box.get() == 1:
                options = journey.luggage_allowed(options)
            options = journey.rating_allowed(options, min_rating)

            if options:
                show_table(options, 0, False)
                return

            transfers = journey.get_transfer_options(data["offers"], start, finish)
            if luggage_box.get() == 1:
                transfers = journey.luggage_allowed(transfers)
            transfers = journey.rating_allowed(transfers, min_rating)

            # results_frame uses grid for the table, so the messages use grid too (never mix with pack)
            if not transfers:
                ctk.CTkLabel(results_frame, text="No bus on this route").grid(row=0, column=0, padx=10, sticky="w")
                return

            ctk.CTkLabel(results_frame, text="No direct bus - recommended transfers via Madrid:").grid(row=0, column=0, columnspan=7, padx=10, pady=(0, 5), sticky="w")
            show_table(sorted(transfers, key=lambda offer: offer.price), 1, True)

        ctk.CTkButton(content, text="Find buses", command=find_buses).pack(pady=10)

    def show_companies_page():
        clear_content()

        # One button per company, the info for the clicked company shows below
        buttons_row = ctk.CTkFrame(content, fg_color="transparent")
        buttons_row.pack(pady=10)

        info_frame = ctk.CTkFrame(content)
        info_frame.pack(pady=10, fill="both", expand=True)

        def show_company(company):
            for widget in info_frame.winfo_children():
                widget.destroy()

            ctk.CTkLabel(info_frame, text=company.name, font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=10, pady=10)
            ctk.CTkLabel(info_frame, text=f"{company.profile.description} (Price range: {company.profile.min_price}-{company.profile.max_price} EUR)").pack(anchor="w", padx=10, pady=5)
            ctk.CTkLabel(info_frame, text=f"Customer rating: {company.profile.rating} / 5").pack(anchor="w", padx=10, pady=5)
            ctk.CTkLabel(info_frame, text="Route: Madrid, " + ", ".join(company.destinations), wraplength=650, justify="left").pack(anchor="w", padx=10, pady=5)
            # The timetable is in minutes, show it as clock times
            times = []
            for time in company.profile.departure_times():
                times.append(to_time_text(time))
            ctk.CTkLabel(info_frame, text="Timetable: " + ", ".join(times), wraplength=650, justify="left").pack(anchor="w", padx=10, pady=5)

        for company in data["companies"]:
            ctk.CTkButton(buttons_row, text=company.name, width=120, command=lambda c=company: show_company(c)).pack(side="left", padx=5)

    # Sidebar buttons(burger menu)
    ctk.CTkButton(sidebar, text="Map", command=open_map).pack(pady=10, padx=10)
    ctk.CTkButton(sidebar, text="Bus Search", command=show_search_page).pack(pady=10, padx=10)
    ctk.CTkButton(sidebar, text="Bus Companies", command=show_companies_page).pack(pady=10, padx=10)

    window.mainloop()

if __name__ == "__main__":
    run()
