
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import oracledb
import uuid

# ---------- ORACLE DATABASE ----------
DB_USER = "BUSGO"
DB_PASSWORD = "Busgo123"
DB_DSN = "localhost:1521/XEPDB1"


def connect_db():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )


# ---------- MAIN APPLICATION ----------
class BusGoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MI BUS- Bus Booking System")
        self.root.geometry("1050x700")
        self.root.configure(bg="#f0f4f8")

        self.primary = "#173b63"
        self.accent = "#2878bd"
        self.selected_bus = None
        self.selected_seats = set()
        self.bus_rows = []
        self.ticket_id = None

        self.build_header()
        self.container = tk.Frame(root, bg="#f0f4f8")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.pages = {}
        for name in (
            "Home", "Search", "Seats", "Passenger",
            "Payment", "Ticket", "Bookings", "Cancellation"
        ):
            self.pages[name] = tk.Frame(self.container, bg="#f0f4f8")

        self.build_home()
        self.build_search()
        self.build_seats()
        self.build_passenger()
        self.build_payment()
        self.build_ticket()
        self.build_bookings()
        self.build_cancellation()

        self.show_page("Home")

    def build_header(self):
        header = tk.Frame(self.root, bg=self.primary, height=65)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="MI BUS 🚌", bg=self.primary, fg="white",
            font=("Arial", 23, "bold")
        ).pack(side="left", padx=20)

        nav = tk.Frame(header, bg=self.primary)
        nav.pack(side="right", padx=10)

        for text, page in [
            ("Home", "Home"),
            ("Search", "Search"),
            ("Bookings", "Bookings"),
            ("Cancel", "Cancellation")
        ]:
            tk.Button(
                nav, text=text,
                command=lambda p=page: self.show_page(p),
                bg=self.primary, fg="white",
                activebackground=self.accent,
                relief="flat", font=("Arial", 10, "bold")
            ).pack(side="left", padx=5, pady=15)

    def show_page(self, name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[name].pack(fill="both", expand=True)

        if name == "Bookings":
            self.refresh_bookings()
        elif name == "Cancellation":
            self.refresh_cancel_list()

    def heading(self, page, title, subtitle=""):
        tk.Label(
            page, text=title, bg="#f0f4f8", fg=self.primary,
            font=("Arial", 22, "bold")
        ).pack(anchor="w", pady=(0, 5))

        if subtitle:
            tk.Label(
                page, text=subtitle, bg="#f0f4f8", fg="#536579",
                font=("Arial", 10)
            ).pack(anchor="w", pady=(0, 15))

    def button(self, page, text, command, color=None):
        return tk.Button(
            page, text=text, command=command,
            bg=color or self.accent, fg="white",
            activebackground=self.primary,
            activeforeground="white",
            relief="flat", font=("Arial", 10, "bold"),
            padx=15, pady=8, cursor="hand2"
        )

    def db_error(self, title, exc):
        messagebox.showerror(title, f"{exc}\n\nCheck Oracle service, username, password and tables.")

    # ---------- PAGE 1: HOME ----------
    def build_home(self):
        p = self.pages["Home"]
        self.heading(p, "Welcome to BusGo", "Your bus booking dashboard")

        hero = tk.Frame(p, bg=self.primary, padx=30, pady=30)
        hero.pack(fill="x", pady=15)

        tk.Label(
            hero, text="Book Your Journey",
            bg=self.primary, fg="white",
            font=("Arial", 25, "bold")
        ).pack(anchor="w")

        tk.Label(
            hero, text="Search buses, choose seats and get your e-ticket.",
            bg=self.primary, fg="white",
            font=("Arial", 12)
        ).pack(anchor="w", pady=10)

        self.button(
            hero, "SEARCH BUSES", lambda: self.show_page("Search")
        ).pack(anchor="w")

        actions = tk.Frame(p, bg="#f0f4f8")
        actions.pack(fill="x", pady=15)

        for text, page in [
            ("Search Buses", "Search"),
            ("My Bookings", "Bookings"),
            ("Cancel Ticket", "Cancellation")
        ]:
            card = tk.Frame(actions, bg="white", padx=20, pady=25)
            card.pack(side="left", fill="both", expand=True, padx=7)
            tk.Label(
                card, text=text, bg="white", fg=self.primary,
                font=("Arial", 14, "bold")
            ).pack(pady=8)
            self.button(
                card, "Open", lambda p=page: self.show_page(p)
            ).pack()

    # ---------- PAGE 2: SEARCH BUSES ----------
    def build_search(self):
        p = self.pages["Search"]
        self.heading(p, "Search Buses", "Enter route and journey date")

        form = tk.Frame(p, bg="white", padx=15, pady=15)
        form.pack(fill="x", pady=10)

        self.pickup = tk.StringVar()
        self.destination = tk.StringVar()
        self.journey_date = tk.StringVar(value=date.today().isoformat())

        for col, text in enumerate(["Pickup", "Destination", "Date (YYYY-MM-DD)"]):
            tk.Label(
                form, text=text, bg="white", fg=self.primary,
                font=("Arial", 10, "bold")
            ).grid(row=0, column=col, sticky="w", padx=5)

        self.pickup_box = ttk.Combobox(
            form, textvariable=self.pickup, width=23
        )
        self.destination_box = ttk.Combobox(
            form, textvariable=self.destination, width=23
        )
        ttk.Entry(
            form, textvariable=self.journey_date, width=20
        ).grid(row=1, column=2, padx=5, pady=8)

        self.pickup_box.grid(row=1, column=0, padx=5, pady=8)
        self.destination_box.grid(row=1, column=1, padx=5, pady=8)

        self.button(form, "Search", self.search_buses).grid(
            row=1, column=3, padx=10
        )

        columns = (
            "ID", "Operator", "Type", "Pickup", "Destination",
            "Departure", "Arrival", "Fare", "Available"
        )
        self.bus_tree = ttk.Treeview(
            p, columns=columns, show="headings", height=11
        )
        for col in columns:
            self.bus_tree.heading(col, text=col)
            self.bus_tree.column(col, width=105, anchor="center")
        self.bus_tree.pack(fill="both", expand=True, pady=10)

        self.button(
            p, "Select Seats →", self.select_bus
        ).pack(anchor="e")

        self.load_routes()

    def load_routes(self):
        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT DISTINCT pickup FROM bg_buses "
                        "WHERE active='Y' ORDER BY pickup"
                    )
                    pickups = [r[0] for r in cur.fetchall()]

                    cur.execute(
                        "SELECT DISTINCT drop_location FROM bg_buses "
                        "WHERE active='Y' ORDER BY drop_location"
                    )
                    destinations = [r[0] for r in cur.fetchall()]

            self.pickup_box["values"] = pickups
            self.destination_box["values"] = destinations

        except Exception as exc:
            self.db_error("Oracle Connection Error", exc)

    def search_buses(self):
        pickup = self.pickup.get().strip()
        destination = self.destination.get().strip()

        try:
            travel_date = datetime.strptime(
                self.journey_date.get().strip(), "%Y-%m-%d"
            ).date()
        except ValueError:
            messagebox.showwarning("Date", "Use YYYY-MM-DD format.")
            return

        if not pickup or not destination or pickup.lower() == destination.lower():
            messagebox.showwarning(
                "Route", "Enter different pickup and destination locations."
            )
            return

        if travel_date < date.today():
            messagebox.showwarning("Date", "Journey date cannot be in the past.")
            return

        self.bus_rows = []
        for item in self.bus_tree.get_children():
            self.bus_tree.delete(item)

        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT b.bus_id, b.operator, b.bus_type, b.pickup,
                               b.drop_location, b.departure, b.arrival, b.fare,
                               24 - (
                                   SELECT COUNT(*)
                                   FROM bg_booking_seats s
                                   JOIN bg_bookings bk
                                     ON bk.ticket_id = s.ticket_id
                                   WHERE s.bus_id = b.bus_id
                                     AND s.journey_date = :jd
                                     AND bk.booking_status = 'CONFIRMED'
                               ) AS available
                        FROM bg_buses b
                        WHERE b.active = 'Y'
                          AND LOWER(b.pickup) = LOWER(:pu)
                          AND LOWER(b.drop_location) = LOWER(:dr)
                        ORDER BY b.departure
                    """, jd=travel_date, pu=pickup, dr=destination)
                    self.bus_rows = cur.fetchall()

            for row in self.bus_rows:
                values = list(row)
                values[7] = f"{float(values[7]):.2f}"
                self.bus_tree.insert("", "end", values=values)

            if not self.bus_rows:
                messagebox.showinfo("No Buses", "No buses found for this route.")

        except Exception as exc:
            self.db_error("Search Error", exc)

    # ---------- PAGE 3: SEAT SELECTION ----------
    def select_bus(self):
        selected = self.bus_tree.selection()
        if not selected:
            messagebox.showwarning("Bus", "Select a bus first.")
            return

        bus_id = int(self.bus_tree.item(selected[0], "values")[0])
        self.selected_bus = next(
            row for row in self.bus_rows if int(row[0]) == bus_id
        )
        self.selected_seats = set()
        self.draw_seats()
        self.show_page("Seats")

    def build_seats(self):
        p = self.pages["Seats"]
        self.heading(p, "Seat Selection", "Choose up to 6 seats")

        self.seat_bus_label = tk.Label(
            p, text="", bg="#f0f4f8", fg=self.primary,
            font=("Arial", 12, "bold")
        )
        self.seat_bus_label.pack(anchor="w", pady=10)

        card = tk.Frame(p, bg="white", padx=25, pady=20)
        card.pack(anchor="w")

        tk.Label(
            card, text="FRONT OF BUS", bg="white",
            font=("Arial", 10, "bold")
        ).pack(pady=8)

        self.seat_grid = tk.Frame(card, bg="white")
        self.seat_grid.pack()

        self.seat_summary = tk.Label(
            p, text="", bg="#f0f4f8", fg=self.primary,
            font=("Arial", 12, "bold")
        )
        self.seat_summary.pack(anchor="w", pady=15)

        self.button(
            p, "← Back", lambda: self.show_page("Search"), "#64748b"
        ).pack(side="left")
        self.button(
            p, "Continue →", self.continue_passenger
        ).pack(side="right")

    def draw_seats(self):
        for widget in self.seat_grid.winfo_children():
            widget.destroy()

        bus = self.selected_bus
        self.seat_bus_label.config(
            text=f"{bus[1]} | {bus[2]} | {bus[3]} → {bus[4]}"
        )

        travel_date = datetime.strptime(
            self.journey_date.get().strip(), "%Y-%m-%d"
        ).date()

        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT s.seat_no
                        FROM bg_booking_seats s
                        JOIN bg_bookings bk ON bk.ticket_id=s.ticket_id
                        WHERE s.bus_id=:bid AND s.journey_date=:jd
                          AND bk.booking_status='CONFIRMED'
                    """, bid=int(bus[0]), jd=travel_date)
                    booked = {int(r[0]) for r in cur.fetchall()}
        except Exception as exc:
            self.db_error("Seat Error", exc)
            return

        self.seat_vars = {}
        for seat in range(1, 25):
            row = (seat - 1) // 4
            col = (seat - 1) % 4
            if col >= 2:
                col += 1

            if seat in booked:
                btn = tk.Button(
                    self.seat_grid, text=f"{seat}\nBooked",
                    state="disabled", bg="#d1d5db", width=9, height=2
                )
            else:
                var = tk.BooleanVar()
                self.seat_vars[seat] = var
                btn = tk.Checkbutton(
                    self.seat_grid, text=f"Seat {seat}", variable=var,
                    indicatoron=False, width=9, height=2,
                    bg="#d8f3dc", selectcolor="#b9d8ff",
                    command=lambda s=seat: self.toggle_seat(s)
                )

            btn.grid(row=row, column=col, padx=5, pady=5)

        self.update_seat_summary()

    def toggle_seat(self, seat):
        if self.seat_vars[seat].get():
            if len(self.selected_seats) >= 6:
                self.seat_vars[seat].set(False)
                messagebox.showwarning("Seat Limit", "Maximum 6 seats.")
                return
            self.selected_seats.add(seat)
        else:
            self.selected_seats.discard(seat)
        self.update_seat_summary()

    def update_seat_summary(self):
        fare = float(self.selected_bus[7]) if self.selected_bus else 0
        seats = ", ".join(map(str, sorted(self.selected_seats))) or "None"
        total = fare * len(self.selected_seats)
        self.seat_summary.config(
            text=f"Seats: {seats}     Total: ₹{total:.2f}"
        )

    def continue_passenger(self):
        if not self.selected_seats:
            messagebox.showwarning("Seats", "Select at least one seat.")
            return

        self.passenger_seats_label.config(
            text="Seats: " + ", ".join(map(str, sorted(self.selected_seats)))
        )
        self.passenger_fare_label.config(
            text=f"Total Fare: ₹{len(self.selected_seats) * float(self.selected_bus[7]):.2f}"
        )
        self.show_page("Passenger")

    # ---------- PAGE 4: PASSENGER DETAILS ----------
    def build_passenger(self):
        p = self.pages["Passenger"]
        self.heading(p, "Passenger Details", "Enter passenger information")

        form = tk.Frame(p, bg="white", padx=25, pady=25)
        form.pack(fill="x")

        self.passenger_name = tk.StringVar()
        self.mobile = tk.StringVar()

        tk.Label(form, text="Passenger Name", bg="white").pack(anchor="w")
        ttk.Entry(
            form, textvariable=self.passenger_name, width=45
        ).pack(anchor="w", pady=(5, 15))

        tk.Label(form, text="Mobile Number (10 digits)", bg="white").pack(anchor="w")
        ttk.Entry(
            form, textvariable=self.mobile, width=45
        ).pack(anchor="w", pady=(5, 15))

        self.passenger_seats_label = tk.Label(
            form, text="Seats:", bg="white", font=("Arial", 11)
        )
        self.passenger_seats_label.pack(anchor="w", pady=5)

        self.passenger_fare_label = tk.Label(
            form, text="Total Fare:", bg="white", fg="#17834a",
            font=("Arial", 13, "bold")
        )
        self.passenger_fare_label.pack(anchor="w", pady=5)

        self.button(
            p, "← Back", lambda: self.show_page("Seats"), "#64748b"
        ).pack(side="left", pady=15)
        self.button(
            p, "Proceed to Payment →", self.go_payment
        ).pack(side="right", pady=15)

    def go_payment(self):
        name = self.passenger_name.get().strip()
        mobile = self.mobile.get().strip()

        if not name:
            messagebox.showwarning("Name", "Enter passenger name.")
            return
        if not mobile.isdigit() or len(mobile) != 10:
            messagebox.showwarning("Mobile", "Enter a valid 10-digit mobile number.")
            return

        self.payment_summary.config(
            text=f"Passenger: {name}\n"
                 f"Route: {self.selected_bus[3]} → {self.selected_bus[4]}\n"
                 f"Date: {self.journey_date.get()}\n"
                 f"Seats: {', '.join(map(str, sorted(self.selected_seats)))}\n"
                 f"Total: ₹{len(self.selected_seats) * float(self.selected_bus[7]):.2f}"
        )
        self.show_page("Payment")

    # ---------- PAGE 5: DEMO PAYMENT ----------
    def build_payment(self):
        p = self.pages["Payment"]
        self.heading(p, "Payment", "Demo only: no real money is charged.")

        card = tk.Frame(p, bg="white", padx=25, pady=25)
        card.pack(fill="x")

        self.payment_summary = tk.Label(
            card, text="", bg="white", justify="left",
            font=("Arial", 12)
        )
        self.payment_summary.pack(anchor="w", pady=10)

        self.payment_method = tk.StringVar(value="UPI")
        for method in ["UPI", "Card", "Cash"]:
            ttk.Radiobutton(
                card, text=method, variable=self.payment_method,
                value=method
            ).pack(anchor="w", pady=5)

        self.button(
            p, "← Back", lambda: self.show_page("Passenger"), "#64748b"
        ).pack(side="left", pady=15)
        self.button(
            p, "CONFIRM BOOKING", self.confirm_booking, "#17834a"
        ).pack(side="right", pady=15)

    def confirm_booking(self):
        bus = self.selected_bus
        if not bus or not self.selected_seats:
            messagebox.showwarning("Booking", "Select bus and seats first.")
            return

        travel_date = datetime.strptime(
            self.journey_date.get().strip(), "%Y-%m-%d"
        ).date()
        name = self.passenger_name.get().strip()
        mobile = self.mobile.get().strip()
        method = self.payment_method.get()
        status = "PAID" if method != "Cash" else "PAY AT BOARDING"
        total = len(self.selected_seats) * float(bus[7])
        ticket = "BG" + uuid.uuid4().hex[:10].upper()

        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    # Recheck chosen seats before saving.
                    cur.execute("""
                        SELECT seat_no FROM bg_booking_seats
                        WHERE bus_id=:bid AND journey_date=:jd
                    """, bid=int(bus[0]), jd=travel_date)
                    occupied = {int(r[0]) for r in cur.fetchall()}

                    if occupied.intersection(self.selected_seats):
                        conn.rollback()
                        messagebox.showwarning(
                            "Seat Taken",
                            "A selected seat has just been booked. Please choose again."
                        )
                        self.draw_seats()
                        self.show_page("Seats")
                        return

                    passenger_id_var = cur.var(oracledb.NUMBER)
                    cur.execute("""
                        INSERT INTO bg_passengers (passenger_name, mobile)
                        VALUES (:name, :mobile)
                        RETURNING passenger_id INTO :pid
                    """, name=name, mobile=mobile, pid=passenger_id_var)
                    passenger_id = int(passenger_id_var.getvalue()[0])

                    cur.execute("""
                        INSERT INTO bg_bookings
                        (ticket_id, passenger_id, bus_id, journey_date, total_fare,
                         payment_method, payment_status, booking_status)
                        VALUES (:tid, :pid, :bid, :jd, :fare, :method, :pstatus, 'CONFIRMED')
                    """, tid=ticket, pid=passenger_id, bid=int(bus[0]),
                         jd=travel_date, fare=total, method=method, pstatus=status)

                    for seat in sorted(self.selected_seats):
                        cur.execute("""
                            INSERT INTO bg_booking_seats
                            (ticket_id, bus_id, journey_date, seat_no)
                            VALUES (:tid, :bid, :jd, :seat)
                        """, tid=ticket, bid=int(bus[0]), jd=travel_date, seat=seat)

                    cur.execute("""
                        INSERT INTO bg_payments
                        (ticket_id, payment_method, amount, payment_status)
                        VALUES (:tid, :method, :amount, :status)
                    """, tid=ticket, method=method, amount=total, status=status)

                conn.commit()

            self.ticket_id = ticket
            self.ticket_details = {
                "ticket": ticket, "name": name, "mobile": mobile,
                "operator": bus[1], "type": bus[2], "pickup": bus[3],
                "drop": bus[4], "departure": bus[5], "arrival": bus[6],
                "date": travel_date.isoformat(),
                "seats": sorted(self.selected_seats), "fare": total,
                "method": method, "payment_status": status,
                "booking_status": "CONFIRMED"
            }
            self.show_ticket(self.ticket_details)
            messagebox.showinfo("Success", f"Booking saved!\nTicket ID: {ticket}")
            self.show_page("Ticket")

        except Exception as exc:
            self.db_error("Booking Failed", exc)

    # ---------- PAGE 6: E-TICKET ----------
    def build_ticket(self):
        p = self.pages["Ticket"]
        self.heading(p, "E-Ticket", "Your booking confirmation")

        self.ticket_box = tk.Label(
            p, text="No ticket generated yet.", bg="white",
            fg=self.primary, justify="left",
            font=("Consolas", 12), padx=25, pady=25,
            anchor="w"
        )
        self.ticket_box.pack(fill="x", pady=10)

        self.button(
            p, "My Bookings", lambda: self.show_page("Bookings")
        ).pack(side="left", pady=10)
        self.button(
            p, "Cancel Ticket", lambda: self.open_cancel_ticket(),
            "#b42318"
        ).pack(side="left", padx=10, pady=10)
        self.button(
            p, "Home", lambda: self.show_page("Home"), "#64748b"
        ).pack(side="right", pady=10)

    def show_ticket(self, d):
        self.ticket_box.config(text=(
            "BUSGO                         E-TICKET\n"
            "-------------------------------------------------\n"
            f"Ticket ID  : {d['ticket']}\n"
            f"Passenger  : {d['name']}\n"
            f"Mobile     : {d['mobile']}\n"
            f"Operator   : {d['operator']}\n"
            f"Bus Type   : {d['type']}\n"
            f"Route      : {d['pickup']} → {d['drop']}\n"
            f"Departure  : {d['departure']}\n"
            f"Arrival    : {d['arrival']}\n"
            f"Journey    : {d['date']}\n"
            f"Seats      : {', '.join(map(str, d['seats']))}\n"
            f"Total Fare : ₹{d['fare']:.2f}\n"
            f"Payment    : {d['method']} ({d['payment_status']})\n"
            f"Status     : {d['booking_status']}\n"
            "-------------------------------------------------\n"
            "Please arrive at the boarding point on time."
        ))

    # ---------- PAGE 7: MY BOOKINGS ----------
    def build_bookings(self):
        p = self.pages["Bookings"]
        self.heading(p, "My Bookings", "Bookings saved in Oracle Database")

        bar = tk.Frame(p, bg="#f0f4f8")
        bar.pack(fill="x", pady=5)
        self.button(bar, "Refresh", self.refresh_bookings).pack(side="left")
        self.button(
            bar, "View Ticket", self.view_booking
        ).pack(side="left", padx=8)
        self.button(
            bar, "Cancel Selected", self.cancel_selected, "#b42318"
        ).pack(side="left")

        cols = ("Ticket", "Passenger", "Route", "Date", "Seats", "Fare", "Status")
        self.booking_tree = ttk.Treeview(
            p, columns=cols, show="headings", height=14
        )
        for col in cols:
            self.booking_tree.heading(col, text=col)
            self.booking_tree.column(col, width=130, anchor="center")
        self.booking_tree.pack(fill="both", expand=True, pady=10)

    def refresh_bookings(self):
        if not hasattr(self, "booking_tree"):
            return

        for item in self.booking_tree.get_children():
            self.booking_tree.delete(item)

        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT bk.ticket_id, p.passenger_name,
                               b.pickup || ' -> ' || b.drop_location,
                               TO_CHAR(bk.journey_date, 'YYYY-MM-DD'),
                               (SELECT LISTAGG(s.seat_no, ', ')
                                  WITHIN GROUP (ORDER BY s.seat_no)
                                FROM bg_booking_seats s
                                WHERE s.ticket_id=bk.ticket_id),
                               bk.total_fare, bk.booking_status
                        FROM bg_bookings bk
                        JOIN bg_passengers p ON p.passenger_id=bk.passenger_id
                        JOIN bg_buses b ON b.bus_id=bk.bus_id
                        ORDER BY bk.created_at DESC
                    """)
                    rows = cur.fetchall()

            for row in rows:
                self.booking_tree.insert("", "end", values=(
                    row[0], row[1], row[2], row[3],
                    row[4] or "-", f"{float(row[5]):.2f}", row[6]
                ))

        except Exception as exc:
            self.db_error("Bookings Error", exc)

    def chosen_ticket(self):
        selection = self.booking_tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Select a booking row first.")
            return None
        return self.booking_tree.item(selection[0], "values")[0]

    def view_booking(self):
        ticket = self.chosen_ticket()
        if ticket:
            details = self.get_ticket_details(ticket)
            if details:
                self.ticket_id = ticket
                self.show_ticket(details)
                self.show_page("Ticket")

    def cancel_selected(self):
        ticket = self.chosen_ticket()
        if ticket:
            self.cancel_id.set(ticket)
            self.show_page("Cancellation")

    # ---------- PAGE 8: CANCELLATION ----------
    def build_cancellation(self):
        p = self.pages["Cancellation"]
        self.heading(p, "Cancel Ticket", "Select a confirmed ticket to cancel.")

        card = tk.Frame(p, bg="white", padx=25, pady=25)
        card.pack(fill="x")

        tk.Label(
            card, text="Ticket ID", bg="white",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        self.cancel_id = tk.StringVar()
        self.cancel_combo = ttk.Combobox(
            card, textvariable=self.cancel_id, width=40
        )
        self.cancel_combo.pack(anchor="w", pady=8)

        self.cancel_info = tk.Label(
            card, text="", bg="white", fg=self.primary,
            justify="left", font=("Arial", 11)
        )
        self.cancel_info.pack(anchor="w", pady=12)

        self.button(
            card, "Check Ticket", self.check_cancel_ticket, "#64748b"
        ).pack(anchor="w", pady=5)
        self.button(
            card, "CONFIRM CANCELLATION", self.cancel_booking, "#b42318"
        ).pack(anchor="w", pady=5)

    def refresh_cancel_list(self):
        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT ticket_id FROM bg_bookings
                        WHERE booking_status='CONFIRMED'
                        ORDER BY created_at DESC
                    """)
                    ids = [r[0] for r in cur.fetchall()]
            self.cancel_combo["values"] = ids
        except Exception as exc:
            self.db_error("Cancellation Error", exc)

    def get_ticket_details(self, ticket):
        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT bk.ticket_id, p.passenger_name, p.mobile,
                               b.operator, b.bus_type, b.pickup, b.drop_location,
                               b.departure, b.arrival,
                               TO_CHAR(bk.journey_date,'YYYY-MM-DD'),
                               bk.total_fare, bk.payment_method,
                               bk.payment_status, bk.booking_status
                        FROM bg_bookings bk
                        JOIN bg_passengers p ON p.passenger_id=bk.passenger_id
                        JOIN bg_buses b ON b.bus_id=bk.bus_id
                        WHERE bk.ticket_id=:ticket
                    """, ticket=ticket)
                    r = cur.fetchone()
                    if not r:
                        messagebox.showwarning("Not Found", "Ticket not found.")
                        return None

                    cur.execute("""
                        SELECT seat_no FROM bg_booking_seats
                        WHERE ticket_id=:ticket ORDER BY seat_no
                    """, ticket=ticket)
                    seats = [int(x[0]) for x in cur.fetchall()]

            return {
                "ticket": r[0], "name": r[1], "mobile": r[2],
                "operator": r[3], "type": r[4], "pickup": r[5],
                "drop": r[6], "departure": r[7], "arrival": r[8],
                "date": r[9], "fare": float(r[10]), "method": r[11],
                "payment_status": r[12], "booking_status": r[13],
                "seats": seats
            }
        except Exception as exc:
            self.db_error("Ticket Error", exc)
            return None

    def check_cancel_ticket(self):
        ticket = self.cancel_id.get().strip()
        if not ticket:
            messagebox.showwarning("Ticket", "Choose a Ticket ID.")
            return

        d = self.get_ticket_details(ticket)
        if d:
            self.cancel_info.config(text=(
                f"Ticket: {d['ticket']}\n"
                f"Passenger: {d['name']}\n"
                f"Route: {d['pickup']} → {d['drop']}\n"
                f"Date: {d['date']}\n"
                f"Seats: {', '.join(map(str, d['seats'])) or 'None'}\n"
                f"Fare: ₹{d['fare']:.2f}\n"
                f"Status: {d['booking_status']}"
            ))

    def cancel_booking(self):
        ticket = self.cancel_id.get().strip()
        if not ticket:
            messagebox.showwarning("Ticket", "Choose a Ticket ID.")
            return

        if not messagebox.askyesno(
            "Confirm", f"Are you sure you want to cancel {ticket}?"
        ):
            return

        try:
            with connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT booking_status FROM bg_bookings
                        WHERE ticket_id=:ticket FOR UPDATE
                    """, ticket=ticket)
                    row = cur.fetchone()

                    if not row:
                        messagebox.showerror("Not Found", "Ticket not found.")
                        return

                    if row[0] != "CONFIRMED":
                        messagebox.showinfo("Status", "This ticket is already cancelled.")
                        return

                    cur.execute("""
                        UPDATE bg_bookings SET booking_status='CANCELLED'
                        WHERE ticket_id=:ticket
                    """, ticket=ticket)

                    cur.execute("""
                        UPDATE bg_payments SET payment_status='CANCELLED (DEMO)'
                        WHERE ticket_id=:ticket
                    """, ticket=ticket)

                    # Remove seat allocations so seats can be booked again.
                    cur.execute("""
                        DELETE FROM bg_booking_seats WHERE ticket_id=:ticket
                    """, ticket=ticket)

                conn.commit()

            self.cancel_info.config(
                text=f"Ticket {ticket} cancelled successfully.\nSeats are now available."
            )
            messagebox.showinfo("Cancelled", "Booking cancelled successfully.")
            self.refresh_cancel_list()
            self.refresh_bookings()

        except Exception as exc:
            self.db_error("Cancellation Failed", exc)

    def open_cancel_ticket(self):
        if self.ticket_id:
            self.cancel_id.set(self.ticket_id)
        self.show_page("Cancellation")


# ---------- RUN APPLICATION ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = BusGoApp(root)
    root.mainloop()
