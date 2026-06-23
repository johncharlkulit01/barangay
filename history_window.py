import customtkinter as ctk
from tkinter import ttk, messagebox
from db_config import get_db_connection


class HistoryDashboard(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#F8FAFC")  # ✅ Light main background
        self.app = app_controller
        self.pack(fill="both", expand=True, padx=15, pady=15)

        # --- Custom Treeview Style with alternating row colors ---
        style = ttk.Style()
        style.theme_use("default")

        # Base style
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#1E293B",
            fieldbackground="#FFFFFF",
            rowheight=30,
            font=("Segoe UI", 11)
        )

        style.configure(
            "Treeview.Heading",
            background="#E2E8F0",
            foreground="#1E293B",
            font=("Segoe UI", 12, "bold")
        )

        # Selected row color
        style.map(
            "Treeview",
            background=[("selected", "#3B82F6")],
            foreground=[("selected", "#FFFFFF")]
        )

        # ✅ Define alternating row colors for light theme
        self.row_colors = [
            "#FFFFFF",   # White
            "#F1F5F9"    # Very light gray
        ]

        # --- Header ---
        ctk.CTkLabel(
            self,
            text="TRANSACTION HISTORY",
            font=("Segoe UI", 26, "bold"),
            text_color="#1E293B"
        ).pack(pady=(15, 20))

        # --- Search & Action Buttons ---
        search_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12)
        search_frame.pack(fill="x", padx=5, pady=(0, 15))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=320,
            height=40,
            placeholder_text="🔍 Search by username...",
            fg_color="#F1F5F9",
            border_color="#CBD5E1",
            text_color="#1E293B"
        )
        self.search_entry.pack(side="left", padx=15, pady=12)

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=80,
            height=40,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.search_data
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Refresh",
            width=80,
            height=40,
            fg_color="#94A3B8",
            hover_color="#64748B",
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.load_data
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Daily Report",
            width=100,
            height=40,
            fg_color="#16A34A",
            hover_color="#15803D",
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.generate_daily_report
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Delete Selected",
            width=110,
            height=40,
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.delete_selected
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Delete All",
            width=90,
            height=40,
            fg_color="#B91C1C",
            hover_color="#991B1B",
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.delete_all
        ).pack(side="left", padx=5)

        # --- Table Container ---
        table_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        columns = ("ID", "Queue", "Username", "Service", "Details", "Date/Time")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Define columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        # Adjust specific column widths
        self.tree.column("Details", width=220, anchor="w")
        self.tree.column("Date/Time", width=160)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_data()
        self.auto_refresh()

    def delete_selected(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record first!")
            return

        values = self.tree.item(selected, "values")
        record_id = values[0]

        if not messagebox.askyesno("Confirm", "Delete this selected record?"):
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM transaction_history WHERE id=%s", (record_id,))
            conn.commit()
            messagebox.showinfo("Success", "✅ Record deleted successfully!")
            self.load_data()
        finally:
            if conn:
                conn.close()

    def delete_all(self):
        if not messagebox.askyesno("WARNING", "Delete ALL history records? This cannot be undone!"):
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()
            if self.app.role == "admin":
                cur.execute("DELETE FROM transaction_history")
            else:
                cur.execute("DELETE FROM transaction_history WHERE username=%s", (self.app.username,))
            conn.commit()
            messagebox.showinfo("Success", "✅ All history records deleted!")
            self.load_data()
        finally:
            if conn:
                conn.close()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor(dictionary=True)

            if self.app.role != "admin":
                query = """
                    SELECT id, queue_id, username, action, details, timestamp
                    FROM transaction_history
                    WHERE username=%s
                    ORDER BY timestamp DESC
                """
                params = (self.app.username,)
            else:
                query = """
                    SELECT id, queue_id, username, action, details, timestamp
                    FROM transaction_history
                    ORDER BY timestamp DESC
                """
                params = ()

            cur.execute(query, params)

            # ✅ Insert rows with alternating colors
            for index, r in enumerate(cur.fetchall()):
                row_id = self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["id"],
                        r.get("queue_id", "N/A"),
                        r["username"],
                        r["action"],
                        r["details"],
                        r["timestamp"]
                    )
                )
                # Apply color based on even/odd row number
                self.tree.tag_configure(f"row_{index}", background=self.row_colors[index % 2])
                self.tree.item(row_id, tags=(f"row_{index}",))

        finally:
            if conn:
                conn.close()

    def search_data(self):
        keyword = self.search_entry.get().strip()
        self.tree.delete(*self.tree.get_children())

        if not keyword:
            self.load_data()
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor(dictionary=True)

            if self.app.role != "admin":
                query = """
                    SELECT id, queue_id, username, action, details, timestamp
                    FROM transaction_history
                    WHERE username LIKE %s AND username=%s
                    ORDER BY timestamp DESC
                """
                params = (f"%{keyword}%", self.app.username)
            else:
                query = """
                    SELECT id, queue_id, username, action, details, timestamp
                    FROM transaction_history
                    WHERE username LIKE %s
                    ORDER BY timestamp DESC
                """
                params = (f"%{keyword}%",)

            cur.execute(query, params)

            # ✅ Also apply alternating colors to search results
            for index, r in enumerate(cur.fetchall()):
                row_id = self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["id"],
                        r.get("queue_id", "N/A"),
                        r["username"],
                        r["action"],
                        r["details"],
                        r["timestamp"]
                    )
                )
                self.tree.tag_configure(f"row_{index}", background=self.row_colors[index % 2])
                self.tree.item(row_id, tags=(f"row_{index}",))

        finally:
            if conn:
                conn.close()

    def generate_daily_report(self):
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")

        self.tree.delete(*self.tree.get_children())

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor(dictionary=True)
            query = "SELECT * FROM transaction_history WHERE DATE(timestamp) = %s"
            cur.execute(query, (today,))

            records = cur.fetchall()
            # ✅ Apply alternating colors to daily report results
            for index, r in enumerate(records):
                row_id = self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["id"], r.get("queue_id", "N/A"), r["username"],
                        r["action"], r["details"], r["timestamp"]
                    )
                )
                self.tree.tag_configure(f"row_{index}", background=self.row_colors[index % 2])
                self.tree.item(row_id, tags=(f"row_{index}",))

            if not records:
                messagebox.showinfo("Report", "No transactions recorded today.")
        finally:
            conn.close()

    def auto_refresh(self):
        if self.winfo_exists():
            self.load_data()
            self.after(8000, self.auto_refresh)