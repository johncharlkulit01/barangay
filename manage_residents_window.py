import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection

class ManageResidentsDashboard(ctk.CTkFrame):
    
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller
        self.pack(fill="both", expand=True, padx=30, pady=30)

        # Title
        ctk.CTkLabel(
            self, 
            text="Manage Resident Accounts", 
            font=("Segoe UI", 24, "bold"),
            text_color="#1E293B"  # Dark text for light theme
        ).pack(anchor="w", pady=(0, 20))

        # Header Bar
        header = ctk.CTkFrame(
            self, 
            fg_color="#1f538d",  # Keep your original blue header
            height=45, 
            corner_radius=8
        )
        header.pack(fill="x", pady=(0, 5))
        
        header.columnconfigure((0, 1, 2, 3), weight=1)
        columns = ["USERNAME", "FULL NAME", "CONTACT", "ACTIONS"]
        for i, text in enumerate(columns):
            ctk.CTkLabel(
                header, 
                text=text, 
                font=("Segoe UI", 12, "bold"), 
                text_color="white"
            ).grid(row=0, column=i, padx=5)

        # Scrollable List Area
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

        # Refresh Button
        ctk.CTkButton(
            self, 
            text="Refresh Resident List", 
            command=self.load_residents,
            fg_color="#3B82F6",        # Primary blue
            hover_color="#2563EB",     # Darker blue on hover
            text_color="white",
            height=40
        ).pack(pady=10)

        self.load_residents()

    def load_residents(self):
        # Clear old rows
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if not conn:
                raise Exception("Database connection failed.")
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT username, full_name, contact 
                FROM users 
                WHERE role = 'resident' 
                ORDER BY username ASC
            """)
            residents = cursor.fetchall()

            if not residents:
                label = ctk.CTkLabel(
                    self.list_frame, 
                    text="No residents found.", 
                    text_color="#64748B", 
                    font=("Segoe UI", 14)
                )
                label.pack(pady=50)
                return

            # ✅ Alternating row colors for LIGHT THEME
            for i, res in enumerate(residents):
                username = res.get("username") or "Unknown"
                full_name = res.get("full_name") or res.get("fullname") or "N/A"
                contact = res.get("contact") or "N/A"

                # Even row = White, Odd row = Light Gray
                bg_color = "#FFFFFF" if i % 2 == 0 else "#F1F5F9"
                
                row = ctk.CTkFrame(
                    self.list_frame, 
                    fg_color=bg_color, 
                    height=55, 
                    corner_radius=10
                )
                row.pack(fill="x", pady=4, padx=5)
                row.columnconfigure((0, 1, 2, 3), weight=1)

                # Labels with proper text color
                ctk.CTkLabel(
                    row, 
                    text=username,
                    text_color="#1E293B"
                ).grid(row=0, column=0, padx=5, sticky="ew")
                
                ctk.CTkLabel(
                    row, 
                    text=full_name,
                    text_color="#1E293B"
                ).grid(row=0, column=1, padx=5, sticky="ew")
                
                ctk.CTkLabel(
                    row, 
                    text=contact,
                    text_color="#1E293B"
                ).grid(row=0, column=2, padx=5, sticky="ew")

                # Delete Button
                ctk.CTkButton(
                    row, 
                    text="Delete", 
                    width=80, 
                    fg_color="#dc3545", 
                    hover_color="#a71d2a",
                    text_color="white",
                    command=lambda u=username: self.delete_resident(u)
                ).grid(row=0, column=3, padx=10)

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load residents:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_resident(self, username):
        if not messagebox.askyesno("Confirm Delete", f"Delete resident account:\n{username}?"):
            return

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE username = %s AND role = 'resident'", (username,))
            conn.commit()
            messagebox.showinfo("Success", f"{username} deleted successfully.")
            self.load_residents()
        except Exception as e:
            messagebox.showerror("Delete Error", f"Could not delete resident:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()