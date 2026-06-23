import customtkinter as ctk
from db_config import get_db_connection

class ResidentDashboard(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#F8FAFC")  # Light background
        self.app = app_controller
        self.pack(fill="both", expand=True, padx=15, pady=15)

        # --- Welcome Header ---
        ctk.CTkLabel(
            self, 
            text=f"👋 Welcome, {self.app.username}!", 
            font=("Segoe UI", 32, "bold"), 
            text_color="#1E293B"
        ).pack(anchor="w", pady=(10, 25))

        # --- Now Serving Section ---
        queue_frame = ctk.CTkFrame(
            self, 
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#E2E8F0"
        )
        queue_frame.pack(fill="x", pady=(0, 20), padx=5)

        ctk.CTkLabel(
            queue_frame, 
            text="📺 NOW SERVING", 
            font=("Segoe UI", 16, "bold"), 
            text_color="#475569"
        ).pack(pady=(15, 5))

        self.now_serving_label = ctk.CTkLabel(
            queue_frame, 
            text="Loading...", 
            font=("Segoe UI", 48, "bold"), 
            text_color="#3B82F6"
        )
        self.now_serving_label.pack(pady=(0, 20))

        # --- Status Counters ---
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 20))
        
        self.status_labels = {}
        statuses = [
            ("Pending", "#F59E0B"), 
            ("Approved", "#16A34A"), 
            ("Rejected", "#DC2626"), 
            ("Cancelled", "#64748B")
        ]
        
        for i, (s, color) in enumerate(statuses):
            card = ctk.CTkFrame(
                status_frame, 
                fg_color="#FFFFFF",
                corner_radius=12, 
                width=150,
                border_width=1,
                border_color="#E2E8F0"
            )
            card.grid(row=0, column=i, padx=8, pady=5, sticky="ew")
            status_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                card, 
                text=s, 
                font=("Segoe UI", 14, "bold"), 
                text_color=color
            ).pack(pady=(12, 0))
            
            lbl = ctk.CTkLabel(
                card, 
                text="0", 
                font=("Segoe UI", 30, "bold"),
                text_color="#1E293B"
            )
            lbl.pack(pady=(0, 12))
            self.status_labels[s] = lbl

        # --- Info Cards: Mission, Vision, Announcements ---
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=5)
        for i in range(3): 
            grid_frame.grid_columnconfigure(i, weight=1)

        self.create_info_card(
            grid_frame, 0, 
            "Mission", 
            "To provide efficient and accessible public service through innovative digital solutions.", 
            "#FFFFFF"
        )
        self.create_info_card(
            grid_frame, 1, 
            "Vision", 
            "A modernized Barangay where services are accessible at your fingertips.", 
            "#FFFFFF"
        )
        
        announcement_text = (
            "• 🩺 Libreng Tuli: 9:00 AM - 5:00 PM\n"
            "• 🐶 Anti-Rabies Vaccination: 9:00 AM - 5:00 PM\n"
            "• 💉 Bakuna Para sa Lahat: 8:00 AM - 5:00 PM\n"
            "• 🏥 Medical Mission: 7:00 AM - 6:00 PM"
        )
        self.create_info_card(
            grid_frame, 2, 
            "Announcements", 
            announcement_text, 
            "#FFFFFF"
        )

        self.load_data()

    def create_info_card(self, master, col, title, content, color):
        card = ctk.CTkFrame(
            master, 
            fg_color=color, 
            corner_radius=15,
            border_width=1,
            border_color="#E2E8F0"
        )
        card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")
        
        ctk.CTkLabel(
            card, 
            text=title.upper(), 
            font=("Segoe UI", 16, "bold"), 
            text_color="#3B82F6"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            card, 
            text=content, 
            font=("Segoe UI", 14), 
            wraplength=240, 
            justify="center",
            text_color="#334155"
        ).pack(padx=15, pady=(0, 20))

    def load_data(self):
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Load appointment status counts
                cursor.execute("""
                    SELECT status, COUNT(*) as total 
                    FROM appointments 
                    WHERE username=%s 
                    GROUP BY status
                """, (self.app.username,))
                
                for row in cursor.fetchall():
                    if row['status'] in self.status_labels:
                        self.status_labels[row['status']].configure(text=str(row['total']))
                
                # Load currently serving queue number
                cursor.execute("""
                    SELECT queue_id 
                    FROM queue_status 
                    WHERE status='Serving' 
                    ORDER BY id DESC 
                    LIMIT 1
                """)
                q = cursor.fetchone()
                
                self.now_serving_label.configure(
                    text=f"Queue #{q['queue_id']}" if q else "No one being served"
                )

            except Exception as e:
                print("Error loading resident data:", e)
            finally:
                conn.close()