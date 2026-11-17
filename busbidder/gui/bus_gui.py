# File location for gui using customtkinter

import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk

import datagen
import journey
import loader
import ranking
from gui.map_view import show_map
from timing import to_minutes, to_time_text, to_duration_text

# Dark mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def run():
    data = datagen.generate_data()

    # Main window: sidebar on the left(burger menue)
    window = ctk.CTk()
    window.title("BusBidder Spain")
    # Big enough for the filters, the preferences and the ranked table with its score columns
    window.geometry("1600x950")

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

        # Preferred departure: a soft preference, the ranking scores buses closer to it higher
        time_column = ctk.CTkFrame(pickers_row, fg_color="transparent")
        time_column.pack(side="left", padx=10)
        ctk.CTkLabel(time_column, text="Preferred time").pack()
        time_picker = ctk.CTkOptionMenu(time_column, values=[f"{hour:02d}:00" for hour in range(24)])
        time_picker.set("08:00")
        time_picker.pack(pady=5)

        # Must have: hard rules, offers that break one are removed
        # (soft preferences are further down, they only change the order)
        ctk.CTkLabel(content, text="Must have", font=ctk.CTkFont(weight="bold")).pack()

        # Grid: checkboxes on the left, dropdowns on the right (one long row did not fit the window)
        filters_frame = ctk.CTkFrame(content, fg_color="transparent")
        filters_frame.pack(pady=5)

        # Luggage: when ticked, only show buses that take luggage
        luggage_box = ctk.CTkCheckBox(filters_frame, text="I need luggage")
        luggage_box.grid(row=0, column=0, padx=10, pady=3, sticky="w")

        # Ticket flexibility: the ticket can be changed or refunded after buying (not changing bus)
        change_box = ctk.CTkCheckBox(filters_frame, text="Changeable ticket")
        change_box.grid(row=1, column=0, padx=10, pady=3, sticky="w")

        refund_box = ctk.CTkCheckBox(filters_frame, text="Refundable ticket")
        refund_box.grid(row=2, column=0, padx=10, pady=3, sticky="w")

        # Limits as dropdowns, so no wrong value can be typed
        # Minimum rating: hide companies rated lower, 0 = no limit
        ctk.CTkLabel(filters_frame, text="Minimum rating").grid(row=0, column=1, padx=(30, 5), sticky="w")
        rating_picker = ctk.CTkOptionMenu(filters_frame, values=["0", "1", "2", "3", "4", "5"], width=80)
        rating_picker.set("0")
        rating_picker.grid(row=0, column=2, pady=3, sticky="w")

        # Max price in EUR, Any = no limit
        ctk.CTkLabel(filters_frame, text="Max price (EUR)").grid(row=1, column=1, padx=(30, 5), sticky="w")
        price_picker = ctk.CTkOptionMenu(filters_frame, values=["Any", "20", "30", "40", "60", "80"], width=80)
        price_picker.set("Any")
        price_picker.grid(row=1, column=2, pady=3, sticky="w")

        # Max travel time in hours, from departure to arrival, Any = no limit
        ctk.CTkLabel(filters_frame, text="Max duration (hours)").grid(row=2, column=1, padx=(30, 5), sticky="w")
        duration_picker = ctk.CTkOptionMenu(filters_frame, values=["Any", "2", "4", "8", "12", "24"], width=80)
        duration_picker.set("Any")
        duration_picker.grid(row=2, column=2, pady=3, sticky="w")

        # Minimum score: hide offers with a lower total score (shown 0-10), 0 = no limit
        ctk.CTkLabel(filters_frame, text="Minimum score").grid(row=3, column=1, padx=(30, 5), sticky="w")
        score_picker = ctk.CTkOptionMenu(filters_frame, values=[str(number) for number in range(11)], width=80)
        score_picker.set("0")
        score_picker.grid(row=3, column=2, pady=3, sticky="w")

        # Preferences: soft wishes, they only change the order of the results (nothing is removed)
        ctk.CTkLabel(content, text="Preferences: how important, 0-10", font=ctk.CTkFont(weight="bold")).pack()

        # 2 x 2 grid of dropdowns, like the filters
        preferences_frame = ctk.CTkFrame(content, fg_color="transparent")
        preferences_frame.pack(pady=5)
        importance_values = [str(number) for number in range(11)]

        # Default 8 / 5 / 3 / 4 = the spec's example weights 40 / 25 / 15 / 20 %
        ctk.CTkLabel(preferences_frame, text="Price").grid(row=0, column=0, padx=(10, 5), sticky="w")
        price_importance = ctk.CTkOptionMenu(preferences_frame, values=importance_values, width=70)
        price_importance.set("8")
        price_importance.grid(row=0, column=1, pady=3, sticky="w")

        ctk.CTkLabel(preferences_frame, text="Duration").grid(row=0, column=2, padx=(30, 5), sticky="w")
        duration_importance = ctk.CTkOptionMenu(preferences_frame, values=importance_values, width=70)
        duration_importance.set("5")
        duration_importance.grid(row=0, column=3, pady=3, sticky="w")

        ctk.CTkLabel(preferences_frame, text="Departure time").grid(row=1, column=0, padx=(10, 5), sticky="w")
        time_importance = ctk.CTkOptionMenu(preferences_frame, values=importance_values, width=70)
        time_importance.set("3")
        time_importance.grid(row=1, column=1, pady=3, sticky="w")

        ctk.CTkLabel(preferences_frame, text="Flexibility").grid(row=1, column=2, padx=(30, 5), sticky="w")
        flex_importance = ctk.CTkOptionMenu(preferences_frame, values=importance_values, width=70)
        flex_importance.set("4")
        flex_importance.grid(row=1, column=3, pady=3, sticky="w")

        # Button right under the choices, packed before the results so it is never squashed
        # lambda because find_buses is written further down
        ctk.CTkButton(content, text="Find buses", command=lambda: find_buses()).pack(pady=10)

        results_frame = ctk.CTkScrollableFrame(content)
        results_frame.pack(pady=10, fill="both", expand=True)

        # Ranked offers: the top 3 box, then the table with a bold header row and one row per offer (best first)
        def show_table(ranked, first_row, with_wait):
            headers = ["Company", "Rating", "Price", "Day", "Departs", "Arrives", "Duration", "Seats", "Score"]
            if with_wait:
                headers = ["Company", "Rating", "Price", "Day", "Departs", "Arrives", "Duration", "Wait", "Seats", "Score"]

            # Day 1 buses first, then day 2. sorted() keeps the order of equal days,
            # so inside each day the best score is still first
            ranked = sorted(ranked, key=lambda item: item["offer"].departure // (24 * 60))
            # Plain tk labels: much faster than CTkLabel when there are hundreds of cells
            # Same colours as the customtkinter dark theme, the font is set once in run()
            table_bg = "gray20"
            text_color = "#DCE4EE"
            bold = ctk.CTkFont(weight="bold")

            # Top 3 box: rank, company, departure, score, the explanation and the description from the company's profile
            # "for your choices", because the best offer depends on the filters and preferences
            tk.Label(results_frame, text="Top 3 for your choices:", font=bold, bg=table_bg, fg=text_color, pady=5).grid(row=first_row, column=0, columnspan=len(headers), padx=5, sticky="w")

            # Top 3: the best bus of 3 different companies, so it shows real alternatives
            # (a transfer counts as its pair of companies, like CostaLink -> VerdeBus)
            top = []
            used = []
            for item in ranked:
                names = []
                for company in item["offer"].companies:
                    names.append(company.name)
                name_text = " -> ".join(names)
                if name_text not in used:
                    used.append(name_text)
                    top.append(item)
                if len(top) == 3:
                    break

            # Explanation: the top 3 compared with each other (lowest / medium / highest price, travel time, flexibility)
            top_offers = []
            for item in top:
                top_offers.append(item["offer"])
            explanations = ranking.explain_top3(top_offers)

            row = first_row + 1
            number = 1
            for item in top:
                offer = item["offer"]
                # A transfer has 2 companies, so it shows both names and both descriptions
                names = []
                descriptions = []
                for company in offer.companies:
                    names.append(company.name)
                    descriptions.append(company.profile.description)
                name_text = " -> ".join(names)
                description_text = " / ".join(descriptions)
                # Line 1: the explanation, line 2: what the company says about itself
                explanation = explanations[number - 1]
                # Day from the week minutes: 0-1439 = day 1, 1440-2879 = day 2
                day = offer.departure // (24 * 60) + 1
                text = f"{number}. {name_text} on day {day} at {to_time_text(offer.departure)} (score {item['total'] * 10:.1f}): {explanation}\n     {description_text}"
                # wraplength: a long transfer text goes onto 2 lines instead of making the table wider
                tk.Label(results_frame, text=text, bg=table_bg, fg=text_color, wraplength=900, justify="left").grid(row=row, column=0, columnspan=len(headers), padx=5, sticky="w")
                row += 1
                number += 1

            # Space between the top 3 box and the table
            for col in range(len(headers)):
                tk.Label(results_frame, text=headers[col], font=bold, bg=table_bg, fg=text_color, pady=5).grid(row=row, column=col, padx=5, pady=(15, 0), sticky="w")

            row += 1
            for item in ranked:
                offer = item["offer"]
                # Transfers show both companies and ratings, like SolRuta -> CostaLink, 3.8 / 4.2
                names = []
                ratings = []
                for company in offer.companies:
                    names.append(company.name)
                    ratings.append(str(company.profile.rating))

                # Day the bus leaves; if it arrives on a later day, the arrival says which day
                day = offer.departure // (24 * 60) + 1
                arrival_day = offer.arrival // (24 * 60) + 1
                arrival_text = to_time_text(offer.arrival)
                if arrival_day != day:
                    arrival_text = f"{arrival_text} (day {arrival_day})"

                # Duration: the whole journey, for a transfer including the wait in Madrid
                duration_text = to_duration_text(offer.arrival - offer.departure)

                values = [" -> ".join(names), " / ".join(ratings), f"{offer.price} EUR", f"Day {day}", to_time_text(offer.departure), arrival_text, duration_text]
                if with_wait:
                    values.append(to_duration_text(offer.wait))
                values.append(offer.seats)

                # Total score is 0-1 in ranking.py, shown 0-10 with 1 decimal, like 7.7
                values.append(f"{item['total'] * 10:.1f}")

                for col in range(len(values)):
                    tk.Label(results_frame, text=str(values[col]), bg=table_bg, fg=text_color, pady=5).grid(row=row, column=col, padx=5, sticky="w")
                row += 1

        # The "Must have" rules from the GUI, used on direct buses and on transfers
        def apply_filters(offers):
            if luggage_box.get() == 1:
                offers = journey.luggage_allowed(offers)
            offers = journey.rating_allowed(offers, int(rating_picker.get()))
            offers = journey.flexibility_allowed(offers, change_box.get() == 1, refund_box.get() == 1)

            max_price = price_picker.get()
            if max_price != "Any":
                offers = journey.price_allowed(offers, float(max_price))

            # The picker is in hours, the offers are in minutes
            max_hours = duration_picker.get()
            if max_hours != "Any":
                offers = journey.duration_allowed(offers, int(max_hours) * 60)
            return offers

        def find_buses():
            for widget in results_frame.winfo_children():
                widget.destroy()

            start = start_picker.get()
            finish = finish_picker.get()

            # Preferences from the GUI -> weights that add up to 1.0, ranking.py does the rest
            importance = {
                "price": int(price_importance.get()),
                "duration": int(duration_importance.get()),
                "dep_time": int(time_importance.get()),
                "flexibility": int(flex_importance.get()),
            }
            # results_frame uses grid for the table, so the messages use grid too (never mix with pack)
            try:
                weights = ranking.make_weights(importance)
            except ValueError:
                ctk.CTkLabel(results_frame, text="Set at least one preference above 0").grid(row=0, column=0, padx=10, sticky="w")
                return
            # "08:00" -> 480 minutes, the ranking works in minutes
            preff = to_minutes(time_picker.get())

            min_score = int(score_picker.get())

            # Full buses are removed first, so a transfer never uses a full bus
            available = journey.seats_available(data["offers"])

            # Rank first (the scores compare the offers with each other), then remove the ones under the minimum score
            options = apply_filters(journey.get_direct_offers(available, start, finish))
            ranked = ranking.score_allowed(ranking.rank_offers(options, weights, preff), min_score)
            if ranked:
                show_table(ranked, 0, False)
                return

            transfers = apply_filters(journey.get_transfer_options(available, start, finish))
            ranked = ranking.score_allowed(ranking.rank_offers(transfers, weights, preff), min_score)

            if not ranked:
                ctk.CTkLabel(results_frame, text="No bus on this route matches your choices").grid(row=0, column=0, padx=10, sticky="w")
                return

            ctk.CTkLabel(results_frame, text="No direct bus - recommended transfers via Madrid:").grid(row=0, column=0, columnspan=10, padx=10, pady=(0, 5), sticky="w")
            show_table(ranked, 1, True)


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
