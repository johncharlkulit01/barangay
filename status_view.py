import customtkinter as ctk
from db_config import get_db_connection


class StatusDashboard(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#F8FAFC")  # Light background
        self.running = True
        self.app = app_controller
        self.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Header ---
        ctk.CTkLabel(
            self,
            text="📊 Barangay Analytics & System Status",
            font=("Segoe UI", 28, "bold"),
            text_color="#1E293B"
        ).pack(anchor="w", pady=(10, 30))

        # --- Stats Cards Container ---
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=10)

        # Create stat cards
        self.pending_card = self._create_stat_card("PENDING REQUESTS", "#F59E0B")
        self.queue_card = self._create_stat_card("ACTIVE QUEUE", "#16A34A")

        self.pending_card.pack(side="left", fill="both", expand=True, padx=10)
        self.queue_card.pack(side="left", fill="both", expand=True, padx=10)

        # Start auto-update
        self.update_stats()

    def _create_stat_card(self, title, color):
        card = ctk.CTkFrame(
            self.stats_frame,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#E2E8F0",
            height=150
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color="#475569"
        ).pack(pady=(25, 5))

        label = ctk.CTkLabel(
            card,
            text="0",
            font=("Segoe UI", 48, "bold"),
            text_color=color
        )
        label.pack(pady=(0, 25))

        card.value_label = label
        return card

    def update_stats(self):
        if not self.winfo_exists() or not self.running:
            return

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()

            # Count pending requests
            cursor.execute("""
                SELECT COUNT(*)
                FROM appointments
                WHERE LOWER(status) = 'pending'
            """)
            pending = cursor.fetchone()[0]

            # Count active queue items (approved or processing)
            cursor.execute("""
                SELECT COUNT(*)
                FROM appointments
                WHERE LOWER(status) IN ('approved', 'processing')
            """)
            queue = cursor.fetchone()[0]

            # Update display
            self.pending_card.value_label.configure(text=str(pending))
            self.queue_card.value_label.configure(text=str(queue))

        except Exception as e:
            print(f"Error updating status: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # Refresh every 5 seconds
        self.after(5000, self.update_stats)

    def stop(self):
        self.running = False