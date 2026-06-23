import customtkinter as ctk
import calendar
from datetime import datetime, date
import holidays
from tkinter import messagebox
from db_config import get_db_connection

class CalendarView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#F8FAFC")  # ✅ Light main background
        self.app = app_controller
        self.pack(fill="both", expand=True, padx=15, pady=15)

        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month

        # --- Header Navigation ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(10, 20))

        ctk.CTkButton(
            self.header_frame, 
            text="<", 
            width=45, 
            height=40,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#1E293B",
            corner_radius=8,
            command=self.prev_month
        ).pack(side="left")

        self.lbl_month_year = ctk.CTkLabel(
            self.header_frame, 
            text="", 
            font=("Segoe UI", 22, "bold"),
            text_color="#1E293B"
        )
        self.lbl_month_year.pack(side="left", expand=True)

        ctk.CTkButton(
            self.header_frame, 
            text=">", 
            width=45, 
            height=40,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#1E293B",
            corner_radius=8,
            command=self.next_month
        ).pack(side="right")

        # --- Legend ---
        self.legend_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12)
        self.legend_frame.pack(fill="x", pady=(0, 15), padx=5)
        self.create_legend()

        # --- Calendar Grid ---
        self.calendar_grid = ctk.CTkFrame(
            self, 
            fg_color="#F1F5F9", 
            corner_radius=15
        )
        self.calendar_grid.pack(fill="both", expand=True, padx=5, pady=5)
        
        for i in range(7): 
            self.calendar_grid.columnconfigure(i, weight=1)
        
        self.draw_calendar()

    def create_legend(self):
        legend_items = [
            ("Today", "#D1FAE5"),
            ("Booked", "#FEF3C7"),
            ("Holiday", "#FEE2E2")
        ]
        for text, color in legend_items:
            frame = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
            frame.pack(side="left", padx=20, pady=12)
            
            ctk.CTkLabel(
                frame, 
                text="", 
                fg_color=color, 
                width=16, 
                height=16, 
                corner_radius=4
            ).pack(side="left", padx=6)
            
            ctk.CTkLabel(
                frame, 
                text=text, 
                font=("Segoe UI", 12),
                text_color="#334155"
            ).pack(side="left")

    def fetch_appointments(self):
        conn = None
        try:
            conn = get_db_connection()
            if not conn: return []
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, appointment_date, fullname, status FROM appointments")
            return cursor.fetchall()
        except Exception as e:
            print("Fetch Error:", e)
            return []
        finally:
            if conn: conn.close()

    def draw_calendar(self):
        for w in self.calendar_grid.winfo_children(): 
            w.destroy()

        self.lbl_month_year.configure(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        # Day Names Header
        for i, day_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            ctk.CTkLabel(
                self.calendar_grid, 
                text=day_name, 
                font=("Segoe UI", 13, "bold"),
                text_color="#475569"
            ).grid(row=0, column=i, pady=8)

        appointments = self.fetch_appointments()
        ph_holidays = holidays.PH(years=self.current_year)
        booked_days = {}

        for app in appointments:
            appt_date = app.get("appointment_date")
            if not appt_date: continue
            
            if isinstance(appt_date, str): 
                appt_date = datetime.strptime(appt_date, "%Y-%m-%d")
            elif isinstance(appt_date, date): 
                appt_date = datetime.combine(appt_date, datetime.min.time())
            
            if appt_date.year == self.current_year and appt_date.month == self.current_month:
                booked_days.setdefault(appt_date.day, []).append(app)

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        for r, week in enumerate(cal, start=1):
            for c, day in enumerate(week):
                if day == 0: 
                    continue

                current_date = date(self.current_year, self.current_month, day)

                # Determine background color
                if current_date in ph_holidays:
                    bg_color = "#FEE2E2"       # Holiday
                elif current_date == date.today():
                    bg_color = "#D1FAE5"       # Today
                elif day in booked_days:
                    bg_color = "#FEF3C7"       # Booked
                else:
                    bg_color = "#FFFFFF"       # Normal day

                # Calendar Day Button
                ctk.CTkButton(
                    self.calendar_grid, 
                    text=str(day), 
                    width=85, 
                    height=85, 
                    fg_color=bg_color,
                    hover_color="#E2E8F0",
                    text_color="#1E293B",
                    font=("Segoe UI", 15, "bold"),
                    corner_radius=10,
                    border_width=1,
                    border_color="#CBD5E1",
                    command=lambda d=day: self.show_day_details(d, booked_days.get(d, []))
                ).grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

    def show_day_details(self, day, appointments):
        if not appointments:
            messagebox.showinfo("Schedule", f"No appointments on {day}.")
            return

        app = appointments[0]

        # --- Details Window ---
        window = ctk.CTkToplevel(self)
        window.title(f"Appointment: {app.get('fullname')}")
        window.geometry("420x450")
        window.configure(fg_color="#FFFFFF")  # ✅ Light popup background
        window.attributes("-topmost", True)

        ctk.CTkLabel(
            window, 
            text="📅 APPOINTMENT DETAILS", 
            font=("Segoe UI", 18, "bold"),
            text_color="#1E293B"
        ).pack(pady=20)

        # Info Card
        info_frame = ctk.CTkFrame(window, fg_color="#F8FAFC", corner_radius=12)
        info_frame.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(
            info_frame, 
            text=f"👤 Name: {app.get('fullname')}", 
            font=("Segoe UI", 13),
            text_color="#1E293B"
        ).pack(anchor="w", padx=15, pady=5)

        ctk.CTkLabel(
            info_frame, 
            text=f"📌 Status: {app.get('status')}", 
            font=("Segoe UI", 13),
            text_color="#334155"
        ).pack(anchor="w", padx=15, pady=5)

        # Reschedule Section
        input_frame = ctk.CTkFrame(window, fg_color="#F8FAFC", corner_radius=12)
        input_frame.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(
            input_frame, 
            text="📆 New Date (YYYY-MM-DD):", 
            font=("Segoe UI", 12, "bold"),
            text_color="#1E293B"
        ).pack(anchor="w", padx=15, pady=(10, 5))

        date_entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text="2026-06-25",
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B",
            height=35
        )
        date_entry.insert(0, f"{self.current_year}-{self.current_month:02d}-{day:02d}")
        date_entry.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            input_frame, 
            text="✏️ Reason for Reschedule:", 
            font=("Segoe UI", 12, "bold"),
            text_color="#1E293B"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        reason_entry = ctk.CTkEntry(
            input_frame, 
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B",
            height=35
        )
        reason_entry.pack(fill="x", padx=15, pady=(0, 10))

        def save_resched():
            new_date = date_entry.get()
            reason = reason_entry.get()

            if not reason.strip():
                messagebox.showwarning("Input Required", "Please enter a reason for rescheduling.")
                return

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                query = "UPDATE appointments SET appointment_date = %s, reason = %s, status = 'Rescheduled' WHERE id = %s"
                cursor.execute(query, (new_date, reason, app['id']))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "✅ Appointment rescheduled successfully!")
                window.destroy()
                self.draw_calendar()

            except Exception as e:
                messagebox.showerror("Error", f"Update Failed: {e}")

        ctk.CTkButton(
            window, 
            text="✅ Confirm Reschedule", 
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="#FFFFFF",
            height=40,
            corner_radius=8,
            command=save_resched
        ).pack(pady=20)

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1: 
            self.current_month, self.current_year = 12, self.current_year - 1
        self.draw_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12: 
            self.current_month, self.current_year = 1, self.current_year + 1
        self.draw_calendar()