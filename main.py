import customtkinter as ctk

from user_login import LoginFrame
from admin_window import AdminDashboard
from resident_window import ResidentDashboard
from monitor_window import MonitorDashboard
from history_window import HistoryDashboard  
from appointments_window import AppointmentsDashboard
from settings_window import SettingsDashboard
from admin_settings_window import AdminSettingsDashboard
from registration_window import RegistrationWindow
from calendar_window import CalendarView
from request_form import RequestFormWindow     
from emergency_window import EmergencyDashboard
from welcome_window import WelcomeDashboard

# --- Theme Imports ---
from theme_config import get_color, toggle_theme


ctk.set_appearance_mode("light")          # ✅ Changed to Light mode
ctk.set_default_color_theme("blue")


class BarangayApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.minsize(1000, 650)
        self.title("Barangay Appointment and Queue Management System")

        # CENTER WINDOW
        window_width = 1200
        window_height = 700

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(1000, 650)

        self.sidebar_visible = True
        self.username = None
        self.role = None

        self.nav_buttons = {}
        self.active_page = None

        # ✅ YOUR LIGHT THEME COLORS DEFINED HERE
        self.COLOR_BG_MAIN = "#F8FAFC"
        self.COLOR_BG_CARD = "#FFFFFF"
        self.COLOR_TEXT_PRIMARY = "#1E293B"
        self.COLOR_TEXT_MUTED = "#555555"
        self.COLOR_BORDER = "#D1D5DB"
        self.COLOR_HOVER = "#E5E7EB"
        self.COLOR_PRIMARY = "#3B82F6"
        self.COLOR_DANGER = "#DC2626"
        self.COLOR_DANGER_HOVER = "#991B1B"
        self.COLOR_WARNING = "#CA8A04"

        # Main container background using your light color
        self.container = ctk.CTkFrame(self, fg_color=self.COLOR_BG_MAIN)
        self.container.pack(fill="both", expand=True)

        self.display_area = None
        self.sidebar = None

        self.show_login()

    def create_sidebar(self):
        if self.sidebar:
            btn_appts = ctk.CTkButton(
                self.sidebar, 
                text="📋 Appointments", 
                fg_color="transparent", 
                anchor="w",
                font=("Segoe UI", 15),
                height=45,
                hover_color=self.COLOR_HOVER,
                text_color=self.COLOR_TEXT_PRIMARY
            )
            btn_appts.pack(fill="x", pady=5, padx=15)
            self.nav_buttons["Appointments"] = btn_appts

    def set_notification(self, button_key, has_notification):
        btn = self.nav_buttons.get(button_key)
        if not btn: 
            return

        # Remove old badge
        for widget in btn.winfo_children():
            if getattr(widget, "is_badge", False):
                widget.destroy()

        if has_notification:
            badge = ctk.CTkLabel(
                btn,
                text="",
                width=12,
                height=12,
                corner_radius=6, 
                fg_color="#EF4444"
            )
            badge.is_badge = True
            badge.place(relx=0.85, rely=0.15)

    def show_login(self):
        self.clear_container()
        self.container.configure(fg_color=self.COLOR_BG_MAIN)
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        LoginFrame(frame, self)

    def show_register(self):
        try:
            reg = RegistrationWindow(self)   # create register window first
            self.withdraw()                 # hide login window
        except Exception as e:
            print("Register Error:", e)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.grid_remove()
            self.sidebar_visible = False
        else:
            self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
            self.sidebar_visible = True

    def show_dashboard(self, role, username):
        self.clear_container()
        self.username = username
        self.role = role.lower()

        # Layout configuration
        self.container.grid_columnconfigure(0, weight=0)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(
            self.container, 
            width=280, 
            fg_color=self.COLOR_BG_CARD,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # User icon
        ctk.CTkLabel(
            self.sidebar, 
            text="👤", 
            font=("Segoe UI Emoji", 45),
            text_color=self.COLOR_TEXT_PRIMARY
        ).pack(pady=(30, 0))
        
        # Panel Title
        title = "ADMIN PANEL" if self.role == "admin" else "USER PANEL"
        title_color = self.COLOR_WARNING if self.role == "admin" else self.COLOR_TEXT_PRIMARY
        ctk.CTkLabel(
            self.sidebar, 
            text=title, 
            font=("Segoe UI", 20, "bold"), 
            text_color=title_color
        ).pack(pady=(20, 5))
        
        # Username
        ctk.CTkLabel(
            self.sidebar, 
            text=self.username, 
            text_color=self.COLOR_TEXT_MUTED,
            font=("Segoe UI", 13)
        ).pack()

        # Divider
        ctk.CTkFrame(
            self.sidebar, 
            height=2, 
            fg_color=self.COLOR_BORDER
        ).pack(fill="x", padx=20, pady=15)

        # --- Navigation Buttons ---
        self.nav_buttons.clear()
        for text, page in self.get_buttons(self.role):
            btn = ctk.CTkButton(
                self.sidebar, 
                text=text, 
                fg_color="transparent",
                hover_color=self.COLOR_HOVER,
                anchor="w", 
                height=45,
                font=("Segoe UI", 15),
                text_color=self.COLOR_TEXT_PRIMARY,
                corner_radius=8,
                command=lambda p=page: self.load_content(p)
            )
            btn.pack(fill="x", padx=15, pady=5)
            self.nav_buttons[page] = btn

        # --- Logout Button ---
        ctk.CTkButton(
            self.sidebar, 
            text="Logout", 
            fg_color=self.COLOR_DANGER, 
            hover_color=self.COLOR_DANGER_HOVER,
            text_color="#FFFFFF",
            font=("Segoe UI", 15, "bold"),
            height=45,
            corner_radius=8,
            command=self.logout
        ).pack(side="bottom", fill="x", padx=15, pady=25)

        # --- Main Display Area ---
        self.main_display = ctk.CTkFrame(
            self.container, 
            fg_color=self.COLOR_BG_MAIN
        )
        self.main_display.grid(row=0, column=1, sticky="nsew")

        # Hamburger Menu Button
        self.hamburger_btn = ctk.CTkButton(
            self.main_display, 
            text="☰", 
            width=42, 
            height=42,
            fg_color=self.COLOR_BG_CARD,
            hover_color=self.COLOR_HOVER,
            text_color=self.COLOR_TEXT_PRIMARY,
            corner_radius=8,
            font=("Segoe UI", 16),
            command=self.toggle_sidebar
        )
        self.hamburger_btn.pack(anchor="nw", padx=15, pady=15)

        # Content container
        self.display_area = ctk.CTkFrame(
            self.main_display, 
            fg_color="transparent"
        )
        self.display_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Load initial page
        initial_page = "Admin" if self.role == "admin" else "Welcome"
        self.load_content(initial_page)
   
    def get_buttons(self, role):
        if role == "admin":
            return [
                ("📊 Dashboard", "Admin"),
                ("🚨 Emergency", "Emergency"),
                ("📋 Appointments", "Appointments"),
                ("🔢 Queue", "Queue"),
                ("📜 History", "History"),
                ("📅 Calendar", "Calendar"),
                ("⚙️ Settings", "AdminSettings")
            ]
        else:
            return [
                ("🏠 Dashboard", "Welcome"),
                ("📝 Create Appointment", "Request"),
                ("🚨 Emergency", "Emergency"),
                ("📅 Calendar", "Calendar"),
                ("📜 History", "History"),
                ("⚙️ Settings", "Settings")
            ]

    def load_content(self, page):
        if not self.display_area:
            return

        # Clear old content
        for widget in self.display_area.winfo_children():
            widget.destroy()

        pages = {
            "Admin": AdminDashboard,
            "Resident": ResidentDashboard,
            "Welcome": WelcomeDashboard,
            "Appointments": AppointmentsDashboard,
            "Queue": MonitorDashboard,
            "History": HistoryDashboard,
            "Calendar": CalendarView,
            "Settings": SettingsDashboard,
            "AdminSettings": AdminSettingsDashboard,
            "Emergency": EmergencyDashboard,
            "Request": RequestFormWindow,
        }

        page_class = pages.get(page)

        if not page_class:
            print("Unknown page:", page)
            return

        try:
            if page == "Request":
                frame = page_class(
                    self.display_area,
                    self,
                    self.username,
                    self.role,
                    None
                )
            elif page == "Admin":
                frame = page_class(self.display_area, self)
            else:    
                frame = page_class(self.display_area, self)

            frame.pack(fill="both", expand=True)
            self.update_nav_highlight(page)
            self.active_page = page

        except Exception as e:
            print(f"Error loading {page}: {e}")
            ctk.CTkLabel(
                self.display_area,
                text=f"❌ Error loading page: {page}",
                text_color=self.COLOR_DANGER,
                font=("Segoe UI", 16, "bold")
            ).pack(pady=50)

    def update_nav_highlight(self, active_page):
        for page, btn in self.nav_buttons.items():
            if page == active_page:
                btn.configure(
                    fg_color=self.COLOR_PRIMARY,
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.COLOR_TEXT_PRIMARY
                )

    def refresh_theme(self):
        """I-update ang lahat ng kulay kapag nagpalit ng tema"""
        self.configure(fg_color=self.COLOR_BG_MAIN)
        self.container.configure(fg_color=self.COLOR_BG_MAIN)
        
        if self.main_display:
            self.main_display.configure(fg_color=self.COLOR_BG_MAIN)
        
        if self.sidebar:
            self.sidebar.configure(fg_color=self.COLOR_BG_CARD)
            # I-update ang mga kulay ng text sa sidebar
            for widget in self.sidebar.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    if "ADMIN PANEL" in widget.cget("text") or "USER PANEL" in widget.cget("text"):
                        title_color = self.COLOR_WARNING if self.role == "admin" else self.COLOR_TEXT_PRIMARY
                        widget.configure(text_color=title_color)
                    elif widget.cget("text") == "👤":
                        widget.configure(text_color=self.COLOR_TEXT_PRIMARY)
                    else:
                        widget.configure(text_color=self.COLOR_TEXT_MUTED)
                elif isinstance(widget, ctk.CTkFrame) and widget.cget("height") == 2:
                    widget.configure(fg_color=self.COLOR_BORDER)
            
            self.update_nav_highlight(self.active_page)

        # I-refresh ang kasalukuyang pahina
        if self.active_page:
            self.load_content(self.active_page)

    def logout(self):
        self.username = None
        self.role = None
        self.show_login()


if __name__ == "__main__":
    app = BarangayApp()
    app.mainloop()