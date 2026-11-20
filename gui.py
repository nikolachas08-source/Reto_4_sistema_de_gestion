# -*- coding: utf-8 -*-
"""Tkinter graphical interface (in English) for Software FJ. (Rol 1)

Grupo colaborativo: 599.

The interface only calls the model classes; it contains no business rules.
Visual design: a LinkedIn-style workspace (top bar, profile sidebar, cards,
custom tabs, contextual hints and colour-coded status) to make the system
easier and more didactic to use.
"""

# tkinter: standard GUI library.
import tkinter as tk
# ttk: themed widgets; messagebox: user notices.
from tkinter import messagebox, ttk

# Model classes used by the interface.
from modelo.cliente import Cliente
from modelo.excepciones import DatoInvalidoError, ErrorSistema
from modelo.gestor import GestorFJ
from modelo.registro import ARCHIVO_LOG, obtener_logger
from modelo.servicios import Asesoria, AlquilerEquipo, ReservaSala
# Simulation of 24 operations.
from simulaciones import ejecutar_simulaciones

# Logger shared by the whole system.
logger = obtener_logger()

# ------------------------------------------------------------------ design tokens
# LinkedIn-like palette: light gray canvas, white cards, corporate blue.
BLUE = "#0A66C2"
BLUE_DARK = "#004182"
BLUE_LIGHT = "#E8F1FA"
BG = "#F4F2EE"
WHITE = "#FFFFFF"
BORDER = "#DFDDD8"
TEXT = "#1D2226"
MUTED = "#6B6F73"
FAINT = "#8B8F93"
GREEN = "#057642"
GREEN_LIGHT = "#E7F4EC"
RED = "#B24020"
RED_LIGHT = "#FCEEE9"
AMBER = "#915907"
AMBER_LIGHT = "#FDF3E2"
FONT = "Segoe UI"


# Returns a font tuple for the whole application.
def fuente(size=10, weight="normal"):
    """Builds a Segoe UI font tuple (presentation only)."""
    # Font family, size and weight.
    return (FONT, size, weight)


# Service types offered in the form: label -> (class, label of the specific field).
SERVICE_TYPES = {
    "Room reservation": (ReservaSala, "Capacity (people)"),
    "Equipment rental": (AlquilerEquipo, "Serial number"),
    "Specialized consulting": (Asesoria, "Specialty"),
}
# Label of the extra option of each service class when creating a reservation.
EXTRA_LABELS = {
    ReservaSala: "Guests (people)",
    AlquilerEquipo: "Additional insurance ($)",
    Asesoria: "High complexity (yes/no)",
}


# Converts text typed by the user into a number (presentation task only).
def to_number(text: str, field: str, integer: bool = False):
    """Returns int/float or raises DatoInvalidoError (chained to the ValueError)."""
    # Try to convert the text.
    try:
        # Integers use int(), the rest use float().
        return int(text) if integer else float(text)
    # The text is not a valid number.
    except ValueError as error:
        # Chaining: the original ValueError is kept as the cause.
        raise DatoInvalidoError(f"The field '{field}' must be a valid number.") from error


# Main window.
class SoftwareFJApp(tk.Tk):
    """LinkedIn-style workspace with four sections: Customers, Services,
    Reservations and Activity (log + simulation)."""

    # Constructor: builds the window and its sections.
    def __init__(self):
        # Initialize the Tk window.
        super().__init__()
        # Window title.
        self.title("Software FJ | Professional Workspace")
        # Initial size.
        self.geometry("1180x760")
        # Minimum size.
        self.minsize(1050, 680)
        # Light canvas behind the cards.
        self.configure(bg=BG)
        # Object that holds the internal lists (no database).
        self.manager = GestorFJ()
        # Tk errors that escape a callback are logged instead of stopping the app.
        self.report_callback_exception = self._on_tk_error
        # List of notebook tabs (their native strip will be hidden).
        self._tabs = []
        # Widgets of the custom tab bar.
        self._tab_widgets = []
        # Shared look and feel.
        self._configure_style()
        # Top navigation bar.
        self._build_header()
        # Left sidebar + main content.
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        self._build_sidebar(body)
        self._build_main(body)
        # Status bar at the bottom.
        self._build_status_bar()
        # Log the opening of the window.
        logger.info("Graphical interface opened (LinkedIn-style workspace).")

    # --------------------------------------------------------------- appearance
    # Configures colours, fonts and widget styles.
    def _configure_style(self):
        """Sets a flat, modern theme inspired by LinkedIn's design system."""
        # 'clam' lets us control widget colours on every platform.
        style = ttk.Style()
        # Fall back to the default theme if clam is unavailable.
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        # Base font and colours.
        style.configure(".", font=fuente(10), background=BG, foreground=TEXT)
        # Generic frames.
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=fuente(10))
        # Labels placed inside white cards.
        style.configure("Card.TLabel", background=WHITE, foreground=TEXT, font=fuente(10))
        # Small grey helper text under form fields.
        style.configure("Hint.TLabel", background=WHITE, foreground=FAINT, font=fuente(8))
        # Section title inside a card.
        style.configure("Title.TLabel", background=WHITE, foreground=TEXT, font=fuente(12, "bold"))
        # Uppercase caption.
        style.configure("Caption.TLabel", background=WHITE, foreground=BLUE, font=fuente(9, "bold"))
        # Primary (blue) button.
        style.configure("TButton", font=fuente(10, "bold"), background=BLUE,
                        foreground=WHITE, borderwidth=0, padding=(10, 7))
        style.map("TButton", background=[("active", BLUE_DARK)])
        # Secondary (white/blue) button.
        style.configure("Subtle.TButton", font=fuente(9, "bold"), background=WHITE,
                        foreground=BLUE, borderwidth=1, padding=(8, 6))
        style.map("Subtle.TButton", background=[("active", BLUE_LIGHT)])
        # Text fields and combo boxes.
        style.configure("TEntry", fieldbackground=WHITE, bordercolor=BORDER, padding=5)
        style.configure("TCombobox", fieldbackground=WHITE, bordercolor=BORDER, padding=4)
        # Tables.
        style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                        foreground=TEXT, rowheight=30, borderwidth=0, font=fuente(10))
        style.configure("Treeview.Heading", background=WHITE, foreground=MUTED,
                        font=fuente(9, "bold"), borderwidth=0, relief="flat")
        style.map("Treeview.Heading", background=[("active", "#EFEFEC")])
        # Notebook content (its tab strip is hidden by custom tabs).
        style.configure("TNotebook", background=BG, borderwidth=0)

    # Creates a white card with a thin border and inner padding.
    def _card(self, parent, padding=12):
        """Returns a white card frame ready to receive widgets."""
        # White background, 1 px border and internal padding.
        return tk.Frame(parent, bg=WHITE, highlightthickness=1,
                        highlightbackground=BORDER, bd=0, padx=padding, pady=padding)

    # Top navigation bar with brand and signed-in user.
    def _build_header(self):
        """Builds the fixed white header with the LinkedIn-like logo."""
        # White bar with a fixed height.
        header = tk.Frame(self, bg=WHITE, height=62)
        header.pack(fill="x", side="top")
        # Do not let children resize the bar.
        header.pack_propagate(False)
        # Blue square with the "in" mark.
        logo = tk.Label(header, text="in", bg=BLUE, fg=WHITE,
                        font=fuente(13, "bold"), width=3)
        logo.pack(side="left", padx=(18, 10), pady=10)
        # Product name.
        tk.Label(header, text="Software FJ", bg=WHITE, fg=TEXT,
                 font=fuente(16, "bold")).pack(side="left")
        # Short description next to the brand.
        tk.Label(header, text="|  Clients · Services · Reservations",
                 bg=WHITE, fg=MUTED, font=fuente(10)).pack(side="left", padx=(10, 0))
        # Badge with the group number.
        avatar = tk.Label(header, text="599", bg=BLUE_LIGHT, fg=BLUE_DARK,
                          font=fuente(11, "bold"), width=3)
        avatar.pack(side="right", padx=(8, 18), pady=10)
        # Group identification (no personal names are shown).
        who = tk.Frame(header, bg=WHITE)
        who.pack(side="right", pady=10)
        # Group number.
        tk.Label(who, text="Grupo 599", bg=WHITE, fg=TEXT,
                 font=fuente(10, "bold")).pack(anchor="e")
        # Project and phase.
        tk.Label(who, text="Software FJ · Fase 4", bg=WHITE, fg=MUTED,
                 font=fuente(9)).pack(anchor="e")
        # Thin blue accent under the header.
        tk.Frame(self, bg=BLUE, height=3).pack(fill="x", side="top")

    # Left sidebar: profile card and step-by-step guide.
    def _build_sidebar(self, parent):
        """Builds the fixed sidebar with stats and a didactic quick guide."""
        # Fixed-width light column.
        side = tk.Frame(parent, bg=BG, width=276)
        side.pack(side="left", fill="y", padx=(14, 8), pady=14)
        side.pack_propagate(False)
        # ------------------------------ profile card
        profile = self._card(side, padding=14)
        profile.pack(fill="x")
        # Circular-looking badge with the group number.
        big_avatar = tk.Label(profile, text="599", bg=BLUE, fg=WHITE,
                              font=fuente(16, "bold"), width=3, height=2)
        big_avatar.pack(anchor="w")
        # Group number.
        tk.Label(profile, text="Grupo 599", bg=WHITE, fg=TEXT,
                 font=fuente(12, "bold"), wraplength=230,
                 justify="left").pack(anchor="w", pady=(10, 0))
        # Project and phase.
        tk.Label(profile, text="Software FJ · Fase 4 · Programación 213023", bg=WHITE, fg=MUTED,
                 font=fuente(9), wraplength=230, justify="left").pack(anchor="w", pady=(3, 10))
        # Divider.
        tk.Frame(profile, bg=BORDER, height=1).pack(fill="x", pady=4)
        # Counters that are refreshed from the manager.
        self.stat_vars = {}
        # One row per counter.
        for key, label, colour in (("clientes", "Customers", BLUE),
                                   ("servicios", "Services", GREEN),
                                   ("reservas", "Reservations", AMBER)):
            # Row container.
            row = tk.Frame(profile, bg=WHITE)
            row.pack(fill="x", pady=3)
            # Number.
            value = tk.Label(row, text="0", bg=WHITE, fg=colour,
                             font=fuente(14, "bold"), width=3, anchor="w")
            value.pack(side="left")
            # Caption.
            tk.Label(row, text=label, bg=WHITE, fg=MUTED,
                     font=fuente(9)).pack(side="left", padx=(6, 0))
            # Store the label to update it later.
            self.stat_vars[key] = value
        # ------------------------------ didactic guide card
        guide = self._card(side, padding=14)
        guide.pack(fill="x", pady=(12, 0))
        # Caption.
        ttk.Label(guide, text="HOW IT WORKS", style="Caption.TLabel").pack(anchor="w")
        # The three steps of the workflow.
        steps = (
            ("1", "Register customers", "Add the people who can book."),
            ("2", "Create services", "Rooms, equipment or consulting."),
            ("3", "Book & process", "Pick a customer, a service and confirm."),
        )
        # Draw each step with a blue number badge.
        for number, title, detail in steps:
            # Row of one step.
            step = tk.Frame(guide, bg=WHITE)
            step.pack(fill="x", pady=(8, 0))
            # Number badge.
            badge = tk.Label(step, text=number, bg=BLUE, fg=WHITE,
                             font=fuente(9, "bold"), width=2)
            badge.pack(side="left")
            # Title and explanation.
            text = tk.Frame(step, bg=WHITE)
            text.pack(side="left", padx=(8, 0))
            # Step title.
            tk.Label(text, text=title, bg=WHITE, fg=TEXT,
                     font=fuente(10, "bold")).pack(anchor="w")
            # Step explanation.
            tk.Label(text, text=detail, bg=WHITE, fg=MUTED, font=fuente(8),
                     wraplength=190, justify="left").pack(anchor="w")
        # Tip at the bottom of the guide.
        tk.Label(guide, text="TIP: open Activity → Run simulation to see 24 examples.",
                 bg=WHITE, fg=BLUE, font=fuente(8), wraplength=220,
                 justify="left").pack(anchor="w", pady=(12, 0))

    # Main column: custom tab bar and notebook content.
    def _build_main(self, parent):
        """Builds the custom LinkedIn-style tabs and the notebook below."""
        # Light column that fills the remaining space.
        main = tk.Frame(parent, bg=BG)
        main.pack(side="left", fill="both", expand=True, padx=(4, 14), pady=14)
        # White card that contains the tab labels.
        tabbar = self._card(main, padding=0)
        tabbar.pack(fill="x")
        # Section name and icon shown in each tab.
        sections = (("Customers", "◉"), ("Services", "◆"),
                    ("Reservations", "▦"), ("Activity", "▤"))
        # Draw one clickable tab per section.
        for name, icon in sections:
            # Holder keeps the label and its blue underline.
            holder = tk.Frame(tabbar, bg=WHITE)
            holder.pack(side="left")
            # Clickable label.
            label = tk.Label(holder, text=f"{icon}   {name}", bg=WHITE, fg=MUTED,
                             font=fuente(10, "bold"), padx=16, pady=10, cursor="hand2")
            label.pack()
            # Underline that marks the active section.
            underline = tk.Frame(holder, bg=WHITE, height=3)
            underline.pack(fill="x")
            # Select this tab when clicked.
            label.bind("<Button-1>", lambda event, i=len(self._tab_widgets): self._select_tab(i))
            # Remember the widgets to repaint them later.
            self._tab_widgets.append((label, underline))
        # Notebook holds the four sections; its native tabs are hidden.
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill="both", expand=True, pady=(10, 0))
        # Build the content of every section.
        self._build_customers_tab()
        self._build_services_tab()
        self._build_reservations_tab()
        self._build_log_tab()
        # Hide the native tab strip: the custom bar is the visible one.
        for tab in self._tabs:
            self.notebook.tab(tab, state="hidden")
        # Show the first section as active.
        self._select_tab(0)

    # Highlights the chosen tab and shows its content.
    def _select_tab(self, index):
        """Selects a section and repaints the custom tab bar."""
        # Ask the notebook to show that section.
        self.notebook.select(index)
        # Repaint every tab label and underline.
        for number, (label, underline) in enumerate(self._tab_widgets):
            # Active tab is blue, the others are grey.
            label.config(fg=BLUE if number == index else MUTED)
            # Only the active tab has a blue underline.
            underline.config(bg=BLUE if number == index else WHITE)

    # Bottom status bar with a coloured dot.
    def _build_status_bar(self):
        """Builds the status bar used to give feedback after each action."""
        # White bar fixed at the bottom.
        bar = tk.Frame(self, bg=WHITE, height=34)
        bar.pack(fill="x", side="bottom")
        # Do not let children resize the bar.
        bar.pack_propagate(False)
        # Coloured dot: blue (info), green (ok), amber (warning), red (error).
        self.status_dot = tk.Label(bar, text="●", bg=WHITE, fg=BLUE, font=fuente(11))
        self.status_dot.pack(side="left", padx=(16, 6))
        # Text variable shared by every action.
        self.status = tk.StringVar(value="Ready. Start by registering a customer.")
        # Message label.
        tk.Label(bar, textvariable=self.status, bg=WHITE, fg=TEXT,
                 font=fuente(9)).pack(side="left")

    # Updates the status text and its coloured dot.
    def _set_status(self, text, kind="info"):
        """Shows a message with a colour that matches its importance."""
        # Colour associated with each kind of message.
        colours = {"info": BLUE, "ok": GREEN, "warn": AMBER, "error": RED}
        # Update the text.
        self.status.set(text)
        # Update the dot colour.
        self.status_dot.config(fg=colours.get(kind, BLUE))

    # ------------------------------------------------------------------ helpers
    # Logs Tk callback errors and keeps the window alive.
    def _on_tk_error(self, exc_type, exc_value, exc_tb):
        # Write the full traceback to the log.
        logger.error("Unexpected error in the interface.", exc_info=(exc_type, exc_value, exc_tb))
        # Tell the user without closing the program.
        messagebox.showerror("Unexpected error", f"{exc_type.__name__}: {exc_value}\nThe program keeps running.")
        # Inform in the status bar too.
        if hasattr(self, "status_dot"):
            self._set_status(f"{exc_type.__name__}: {exc_value}", "error")

    # Wraps an action so that no error can stop the application.
    def _guard(self, action):
        """Returns a handler that runs 'action' and shows any error in a dialog."""
        # Handler that Tk will call.
        def handler():
            # Try to run the action.
            try:
                # Run it.
                action()
            # Controlled system error (invalid data, unavailable service, ...).
            except ErrorSistema as error:
                # Log it.
                logger.warning("Interface: %s: %s", type(error).__name__, error)
                # Show a warning with the detail.
                messagebox.showwarning("Operation rejected", str(error))
                # Update the status bar.
                self._set_status(f"Rejected: {error}", "warn")
            # Any other error: log with traceback and continue.
            except Exception as error:
                # Log with traceback.
                logger.exception("Unexpected error in the interface.")
                # Show an error dialog.
                messagebox.showerror("Unexpected error", f"{type(error).__name__}: {error}")
                # Update the status bar.
                self._set_status("Unexpected error (see the log).", "error")
            # Always refresh the lists, even after an error.
            finally:
                # Refresh tables and combo boxes.
                self._refresh_all()
        # Return the handler.
        return handler

    # Adds a floating explanation when the pointer rests on a widget.
    def _tooltip(self, widget, text):
        """Shows a small dark tooltip with extra didactic information."""
        # Holder for the temporary window (a list keeps the index always valid).
        tip = [None]
        # Show the tooltip.
        def show(event):
            # Do not duplicate the window.
            if tip[0] is not None:
                return
            # Position it near the widget.
            x = widget.winfo_rootx() + 18
            y = widget.winfo_rooty() + widget.winfo_height() + 4
            # Borderless top-level window.
            window = tk.Toplevel(widget)
            window.wm_overrideredirect(True)
            window.wm_geometry(f"+{x}+{y}")
            # Dark bubble with white text.
            tk.Label(window, text=text, bg=TEXT, fg=WHITE, font=fuente(9),
                     padx=9, pady=6, justify="left", wraplength=270).pack()
            # Remember it so it can be closed.
            tip[0] = window
        # Hide and destroy the tooltip.
        def hide(event):
            # Take the window out of the holder before destroying it, so a later
            # <Enter> always sees a valid slot and cannot raise KeyError.
            window = tip[0]
            tip[0] = None
            # Destroy it if it existed.
            if window is not None:
                window.destroy()
        # Bind both events.
        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    # Builds a labelled entry with a helper line, returning its StringVar.
    def _field(self, parent, label, row, width=24, hint=None):
        """Creates a field label, an entry and an optional helper text."""
        # Label of the field.
        ttk.Label(parent, text=label, style="Card.TLabel").grid(
            row=row, column=0, sticky="w", padx=(0, 8), pady=(7, 0))
        # Variable that stores the text.
        variable = tk.StringVar()
        # Entry widget.
        ttk.Entry(parent, textvariable=variable, width=width).grid(
            row=row, column=1, sticky="w", pady=(7, 0))
        # Helper text (format or example) placed under the entry.
        if hint:
            # Small grey caption.
            ttk.Label(parent, text=hint, style="Hint.TLabel").grid(
                row=row + 1, column=1, sticky="w", pady=(0, 1))
        # Return the variable.
        return variable

    # Creates a button inside a form grid, optionally with a tooltip.
    def _grid_button(self, parent, text, command, row, tip=None, subtle=False):
        """Adds a styled button to a form grid."""
        # Secondary or primary style.
        style = "Subtle.TButton" if subtle else "TButton"
        # Create the button.
        button = ttk.Button(parent, text=text, command=command, style=style)
        # Fill the two form columns.
        button.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        # Add extra explanation on hover.
        if tip:
            self._tooltip(button, tip)
        # Return the widget.
        return button

    # Adds the title and explanation banner at the top of a section.
    def _banner(self, parent, title, subtitle):
        """Creates the white introductory card of a section."""
        # White card across the section width.
        card = self._card(parent, padding=11)
        card.pack(fill="x", padx=12, pady=(12, 8))
        # Section title.
        tk.Label(card, text=title, bg=WHITE, fg=TEXT,
                 font=fuente(13, "bold")).pack(anchor="w")
        # One-line explanation of what the user can do here.
        tk.Label(card, text=subtitle, bg=WHITE, fg=MUTED, font=fuente(9),
                 wraplength=760, justify="left").pack(anchor="w", pady=(2, 0))
        # Return the card for callers that need to add widgets.
        return card

    # Builds a table (Treeview) with a scrollbar and coloured tags.
    def _table(self, parent, columns, widths):
        """Creates a scrollable table inside a white holder frame."""
        # Holder that packs the table and its scrollbar.
        holder = tk.Frame(parent, bg=WHITE)
        holder.pack(fill="both", expand=True)
        # Create the table.
        tree = ttk.Treeview(holder, columns=columns, show="headings", height=12)
        # Configure every column.
        for column, width in zip(columns, widths):
            # Column title.
            tree.heading(column, text=column)
            # Column width.
            tree.column(column, width=width, anchor="w")
        # Alternating row colour for easier reading.
        tree.tag_configure("odd", background="#FAF9F7")
        # Semantic colours for values and statuses.
        tree.tag_configure("good", foreground=GREEN)
        tree.tag_configure("bad", foreground=RED)
        tree.tag_configure("warn", foreground=AMBER)
        # Vertical scrollbar.
        scroll = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        # Connect both widgets.
        tree.configure(yscrollcommand=scroll.set)
        # Place them.
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        # Return the table.
        return tree

    # ---------------------------------------------------------------- customers
    # Builds the Customers section.
    def _build_customers_tab(self):
        # Frame of the section.
        tab = ttk.Frame(self.notebook)
        # Remember it so the native tab can be hidden later.
        self._tabs.append(tab)
        # Add it to the notebook.
        self.notebook.add(tab, text="Customers")
        # Didactic banner.
        self._banner(tab, "Customers",
                     "Register the people who can make reservations. Every field is validated before saving.")
        # Row with the form card and the table card.
        content = tk.Frame(tab, bg=BG)
        content.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        # Form on the left.
        form = self._card(content, padding=14)
        form.pack(side="left", fill="y")
        # Step caption.
        ttk.Label(form, text="STEP 1 · NEW CUSTOMER", style="Caption.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
        # Form fields with examples and validation rules.
        self.c_id = self._field(form, "ID", 1, hint="Unique code, e.g. CLI-10")
        self.c_name = self._field(form, "Full name", 3, hint="Letters, spaces and apostrophes")
        self.c_doc = self._field(form, "National ID", 5, hint="7 to 12 digits, numbers only")
        self.c_email = self._field(form, "Email", 7, hint="Format: name@example.com")
        self.c_phone = self._field(form, "Phone", 9, hint="Example: 3001234567")
        # Register button.
        self._grid_button(form, "Register customer", self._guard(self._register_customer), 11,
                          tip="Validates name, document, email and phone, then saves the customer in memory.")
        # Table card on the right.
        list_card = self._card(content, padding=8)
        list_card.pack(side="left", fill="both", expand=True, padx=(12, 0))
        # Small caption above the table.
        ttk.Label(list_card, text="REGISTERED CUSTOMERS", style="Caption.TLabel").pack(anchor="w", pady=(2, 6))
        # Table of customers.
        self.c_table = self._table(list_card,
                                   ("ID", "Name", "National ID", "Email", "Phone"),
                                   (80, 180, 110, 210, 110))

    # Registers a customer using the typed data.
    def _register_customer(self):
        # Build the customer (the class validates every field).
        customer = Cliente(self.c_id.get(), self.c_name.get(), self.c_doc.get(),
                           self.c_email.get(), self.c_phone.get())
        # Store it in the manager (checks duplicates).
        self.manager.registrar_cliente(customer)
        # Clear the form.
        for variable in (self.c_id, self.c_name, self.c_doc, self.c_email, self.c_phone):
            # Empty the variable.
            variable.set("")
        # Update the status bar.
        self._set_status(f"Customer {customer.identificador} registered successfully.", "ok")

    # ----------------------------------------------------------------- services
    # Builds the Services section.
    def _build_services_tab(self):
        # Frame of the section.
        tab = ttk.Frame(self.notebook)
        # Remember it so the native tab can be hidden later.
        self._tabs.append(tab)
        # Add it to the notebook.
        self.notebook.add(tab, text="Services")
        # Didactic banner.
        self._banner(tab, "Services",
                     "Create the offer: a room, an equipment rental or a consulting session. Select a row to enable or disable it.")
        # Row with the form card and the table card.
        content = tk.Frame(tab, bg=BG)
        content.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        # Form on the left.
        form = self._card(content, padding=14)
        form.pack(side="left", fill="y")
        # Step caption.
        ttk.Label(form, text="STEP 2 · NEW SERVICE", style="Caption.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
        # Type selector label.
        ttk.Label(form, text="Type", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=(7, 0))
        # Variable of the selector.
        self.s_type = tk.StringVar(value="Room reservation")
        # Combo box with the three types.
        combo = ttk.Combobox(form, textvariable=self.s_type, values=list(SERVICE_TYPES),
                             state="readonly", width=22)
        # Place the combo box.
        combo.grid(row=1, column=1, sticky="w", pady=(7, 0))
        # Helper text for the type.
        ttk.Label(form, text="Choose what the customer can book", style="Hint.TLabel").grid(
            row=2, column=1, sticky="w")
        # Common fields.
        self.s_id = self._field(form, "ID", 3, hint="Unique code, e.g. SRV-10")
        self.s_name = self._field(form, "Service name", 5, hint="Name shown in the reservation form")
        self.s_cost = self._field(form, "Base cost ($)", 7, hint="Must be greater than zero")
        # Label of the specific field (changes with the type).
        self.s_extra_label = ttk.Label(form, text=SERVICE_TYPES["Room reservation"][1],
                                       style="Card.TLabel")
        # Place the label.
        self.s_extra_label.grid(row=9, column=0, sticky="w", pady=(7, 0))
        # Variable of the specific field.
        self.s_extra = tk.StringVar()
        # Entry of the specific field.
        ttk.Entry(form, textvariable=self.s_extra, width=24).grid(row=9, column=1, sticky="w", pady=(7, 0))
        # Hint of the specific field.
        self.s_extra_hint = ttk.Label(form, text="Capacity must be greater than zero", style="Hint.TLabel")
        self.s_extra_hint.grid(row=10, column=1, sticky="w")
        # Change the label and the hint when the type changes.
        def on_type_change(event):
            # Selected type.
            selected = self.s_type.get()
            # Update the field label.
            self.s_extra_label.config(text=SERVICE_TYPES[selected][1])
            # Update its helper text.
            hints = {"Room reservation": "Whole number greater than zero",
                     "Equipment rental": "Example: SRV-DELL-9922",
                     "Specialized consulting": "Example: Software Architecture"}
            self.s_extra_hint.config(text=hints[selected])
        # Bind the change event.
        combo.bind("<<ComboboxSelected>>", on_type_change)
        # Action buttons.
        self._grid_button(form, "Create service", self._guard(self._create_service), 11,
                          tip="Builds the selected service class; its own validations are applied.")
        self._grid_button(form, "Enable selected", self._guard(lambda: self._set_availability(True)), 12,
                          tip="Select a service in the table first.", subtle=True)
        self._grid_button(form, "Disable selected", self._guard(lambda: self._set_availability(False)), 13,
                          tip="Disabled services disappear from the reservation form.", subtle=True)
        # Table card on the right.
        list_card = self._card(content, padding=8)
        list_card.pack(side="left", fill="both", expand=True, padx=(12, 0))
        # Caption above the table.
        ttk.Label(list_card, text="SERVICE CATALOG", style="Caption.TLabel").pack(anchor="w", pady=(2, 6))
        # Table of services.
        self.s_table = self._table(list_card,
                                   ("ID", "Type", "Name", "Base cost", "Per", "Available"),
                                   (70, 130, 190, 100, 70, 80))

    # Creates a service of the chosen type.
    def _create_service(self):
        # Class and label that correspond to the selected type.
        service_class, _ = SERVICE_TYPES[self.s_type.get()]
        # Base cost typed by the user.
        cost = to_number(self.s_cost.get(), "base cost")
        # Specific value: capacity is a number, the others are text.
        specific = to_number(self.s_extra.get(), "capacity", integer=True) if service_class is ReservaSala \
            else self.s_extra.get()
        # Build the service (the class validates its parameters).
        service = service_class(self.s_id.get(), self.s_name.get(), cost, specific)
        # Store it in the manager (checks duplicates).
        self.manager.registrar_servicio(service)
        # Clear the form.
        for variable in (self.s_id, self.s_name, self.s_cost, self.s_extra):
            # Empty the variable.
            variable.set("")
        # Update the status bar.
        self._set_status(f"Service {service.identificador} created successfully.", "ok")

    # Enables or disables the service selected in the table.
    def _set_availability(self, enabled: bool):
        # Selected rows.
        selection = self.s_table.selection()
        # Nothing selected.
        if not selection:
            # Controlled error.
            raise DatoInvalidoError("Select a service in the table first.")
        # Identifier of the selected service.
        service = self.manager.buscar_servicio(self.s_table.item(selection[0])["values"][0])
        # Enable or disable.
        service.habilitar() if enabled else service.deshabilitar()
        # Update the status bar.
        self._set_status(f"Service {service.identificador} "
                         f"{'enabled' if enabled else 'disabled'}.", "ok")

    # ------------------------------------------------------------- reservations
    # Builds the Reservations section.
    def _build_reservations_tab(self):
        # Frame of the section.
        tab = ttk.Frame(self.notebook)
        # Remember it so the native tab can be hidden later.
        self._tabs.append(tab)
        # Add it to the notebook.
        self.notebook.add(tab, text="Reservations")
        # Didactic banner.
        self._banner(tab, "Reservations",
                     "Choose a customer and an available service, set the duration and adjust cost options, then process and confirm.")
        # Row with the form card and the table card.
        content = tk.Frame(tab, bg=BG)
        content.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        # Form on the left.
        form = self._card(content, padding=14)
        form.pack(side="left", fill="y")
        # Step caption.
        ttk.Label(form, text="STEP 3 · NEW RESERVATION", style="Caption.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
        # Customer selector label.
        ttk.Label(form, text="Customer", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=(7, 0))
        # Variable of the customer selector.
        self.r_customer = tk.StringVar()
        # Combo box of customers.
        self.r_customer_box = ttk.Combobox(form, textvariable=self.r_customer,
                                           state="readonly", width=26)
        # Place it.
        self.r_customer_box.grid(row=1, column=1, sticky="w", pady=(7, 0))
        # Helper text.
        ttk.Label(form, text="Registered people only", style="Hint.TLabel").grid(row=2, column=1, sticky="w")
        # Service selector label.
        ttk.Label(form, text="Service", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=(7, 0))
        # Variable of the service selector.
        self.r_service = tk.StringVar()
        # Combo box of services.
        self.r_service_box = ttk.Combobox(form, textvariable=self.r_service,
                                          state="readonly", width=26)
        # Place it.
        self.r_service_box.grid(row=3, column=1, sticky="w", pady=(7, 0))
        # Helper text.
        ttk.Label(form, text="Only enabled services appear here", style="Hint.TLabel").grid(
            row=4, column=1, sticky="w")
        # Update the extra label when the service changes.
        self.r_service_box.bind("<<ComboboxSelected>>", lambda event: self._update_extra_label())
        # Numeric fields with meaning and examples.
        self.r_duration = self._field(form, "Duration", 5, 26,
                                      hint="Hours, days or sessions (must be > 0)")
        self.r_discount = self._field(form, "Discount (%)", 7, 26,
                                      hint="Optional, from 0 to 100")
        self.r_tax = self._field(form, "Tax (%)", 9, 26,
                                 hint="Optional, for example 19")
        # Label of the extra option (changes with the service).
        self.r_extra_label = ttk.Label(form, text="Extra option", style="Card.TLabel")
        # Place the label.
        self.r_extra_label.grid(row=11, column=0, sticky="w", pady=(7, 0))
        # Variable of the extra option.
        self.r_extra = tk.StringVar()
        # Entry of the extra option.
        ttk.Entry(form, textvariable=self.r_extra, width=26).grid(row=11, column=1, sticky="w", pady=(7, 0))
        # Helper text of the extra option.
        self.r_extra_hint = ttk.Label(form, text="Depends on the chosen service", style="Hint.TLabel")
        self.r_extra_hint.grid(row=12, column=1, sticky="w")
        # Action buttons.
        self._grid_button(form, "Create and process", self._guard(self._create_reservation), 13,
                          tip="Calculates the total cost and registers the reservation as processed.")
        self._grid_button(form, "Confirm selected", self._guard(self._confirm_reservation), 14,
                          tip="Only a processed reservation can be confirmed.", subtle=True)
        self._grid_button(form, "Cancel selected", self._guard(self._cancel_reservation), 15,
                          tip="A cancelled reservation cannot be cancelled again.", subtle=True)
        # Table card on the right.
        list_card = self._card(content, padding=8)
        list_card.pack(side="left", fill="both", expand=True, padx=(12, 0))
        # Caption above the table.
        ttk.Label(list_card, text="RESERVATION BOARD", style="Caption.TLabel").pack(anchor="w", pady=(2, 6))
        # Colour legend under the caption.
        legend = tk.Frame(list_card, bg=WHITE)
        legend.pack(fill="x", pady=(0, 6))
        # One coloured item per state.
        for text, colour in (("Confirmed", GREEN), ("Pending", AMBER),
                             ("Cancelled / Failed", RED)):
            # Coloured dot.
            tk.Label(legend, text="●", bg=WHITE, fg=colour, font=fuente(8)).pack(side="left")
            # Caption.
            tk.Label(legend, text=f" {text}   ", bg=WHITE, fg=MUTED, font=fuente(8)).pack(side="left")
        # Table of reservations.
        self.r_table = self._table(list_card,
                                   ("ID", "Customer", "Service", "Duration", "Status", "Total"),
                                   (80, 145, 180, 90, 95, 110))

    # Extracts the identifier from a combo box value like "CLI-01 - Name".
    @staticmethod
    def _identifier_of(text: str) -> str:
        # The identifier is everything before the first " - ".
        return text.split(" - ")[0].strip()

    # Updates the label and hint of the extra option according to the service.
    def _update_extra_label(self):
        # Intentionally tolerant: if nothing is selected the default label stays.
        try:
            # Service selected in the combo box.
            service = self.manager.buscar_servicio(self._identifier_of(self.r_service.get()))
            # Label that matches its class.
            self.r_extra_label.config(text=EXTRA_LABELS.get(type(service), "Extra option"))
            # Helper text that matches its class.
            hints = {ReservaSala: "Number of guests (whole number)",
                     AlquilerEquipo: "Additional insurance amount in dollars",
                     Asesoria: "Type 'yes' or 'no'"}
            self.r_extra_hint.config(text=hints.get(type(service), "Depends on the chosen service"))
        # Not found: keep the default label.
        except ErrorSistema:
            # Default label and hint.
            self.r_extra_label.config(text="Extra option")
            self.r_extra_hint.config(text="Depends on the chosen service")

    # Builds the options dictionary from the form.
    def _read_options(self, service) -> dict:
        # Dictionary of options for the cost calculation.
        options = {}
        # Discount typed by the user (empty means none).
        if self.r_discount.get().strip():
            # Convert and store it.
            options["descuento"] = to_number(self.r_discount.get(), "discount")
        # Tax typed by the user (empty means none).
        if self.r_tax.get().strip():
            # Convert and store it.
            options["impuesto"] = to_number(self.r_tax.get(), "tax")
        # Extra option typed by the user (empty means none).
        extra = self.r_extra.get().strip()
        # Only if something was typed.
        if extra:
            # Rooms: number of guests.
            if isinstance(service, ReservaSala):
                # Convert and store it.
                options["personas"] = to_number(extra, "guests", integer=True)
            # Equipment: additional insurance.
            elif isinstance(service, AlquilerEquipo):
                # Convert and store it.
                options["seguro_adicional"] = to_number(extra, "additional insurance")
            # Consulting: high complexity yes/no.
            else:
                # Only "yes" or "no" are accepted.
                if extra.lower() not in ("yes", "no"):
                    # Controlled error.
                    raise DatoInvalidoError("High complexity must be 'yes' or 'no'.")
                # Store the boolean.
                options["alta_complejidad"] = extra.lower() == "yes"
        # Return the options.
        return options

    # Creates and processes a reservation.
    def _create_reservation(self):
        # Selected customer and service identifiers.
        customer_id = self._identifier_of(self.r_customer.get())
        service_id = self._identifier_of(self.r_service.get())
        # Service object (needed to interpret the extra option).
        service = self.manager.buscar_servicio(service_id)
        # Duration typed by the user.
        duration = to_number(self.r_duration.get(), "duration")
        # Show whole numbers without decimals (2.0 -> 2).
        duration = int(duration) if float(duration).is_integer() else duration
        # Create the reservation (validates customer, service, duration).
        reservation = self.manager.crear_reserva(customer_id, service_id, duration, self._read_options(service))
        # Process it (calculates the cost); errors are shown by the guard.
        reservation.procesar()
        # Update the status bar.
        self._set_status(f"Reservation {reservation.identificador} processed: "
                         f"${reservation.costo_total:,.2f}.", "ok")

    # Returns the reservation selected in the table.
    def _selected_reservation(self):
        # Selected rows.
        selection = self.r_table.selection()
        # Nothing selected.
        if not selection:
            # Controlled error.
            raise DatoInvalidoError("Select a reservation in the table first.")
        # Search it by identifier.
        return self.manager.buscar_reserva(self.r_table.item(selection[0])["values"][0])

    # Confirms the selected reservation.
    def _confirm_reservation(self):
        # Selected reservation.
        reservation = self._selected_reservation()
        # Confirm it.
        reservation.confirmar()
        # Update the status bar.
        self._set_status(f"Reservation {reservation.identificador} confirmed.", "ok")

    # Cancels the selected reservation.
    def _cancel_reservation(self):
        # Selected reservation.
        reservation = self._selected_reservation()
        # Cancel it.
        reservation.cancelar()
        # Update the status bar.
        self._set_status(f"Reservation {reservation.identificador} cancelled.", "ok")

    # ------------------------------------------------------------ log/simulation
    # Builds the Activity section.
    def _build_log_tab(self):
        # Frame of the section.
        tab = ttk.Frame(self.notebook)
        # Remember it so the native tab can be hidden later.
        self._tabs.append(tab)
        # Add it to the notebook.
        self.notebook.add(tab, text="Activity")
        # Didactic banner.
        self._banner(tab, "Activity & log",
                     "Run the 24 simulated operations to learn how errors are handled, then inspect every event recorded in sistema.log.")
        # Card with the action bar and the log viewer.
        card = self._card(tab, padding=10)
        card.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        # Bar with the buttons.
        bar = tk.Frame(card, bg=WHITE)
        bar.pack(fill="x", pady=(0, 8))
        # Button that runs the 24 operations.
        run = ttk.Button(bar, text="Run simulation (24 operations)",
                         command=self._guard(self._run_simulation))
        run.pack(side="left")
        # Tooltip with a didactic explanation.
        self._tooltip(run, "10 successful operations and 14 controlled errors; the system never stops.")
        # Button that refreshes the log view.
        refresh = ttk.Button(bar, text="Refresh log", command=self._guard(self._refresh_log),
                             style="Subtle.TButton")
        refresh.pack(side="left", padx=8)
        # Tooltip for the refresh button.
        self._tooltip(refresh, "Loads the last 300 lines of logs/sistema.log into this viewer.")
        # Caption above the log.
        ttk.Label(card, text="logs/sistema.log  ·  last 300 lines", style="Caption.TLabel").pack(
            anchor="w", pady=(0, 4))
        # Frame that holds the text area and its scrollbar.
        viewer = tk.Frame(card, bg=WHITE)
        viewer.pack(fill="both", expand=True)
        # Read-only text area for the log.
        self.log_text = tk.Text(viewer, height=20, wrap="none", state="disabled",
                                bg="#FCFCFB", fg=TEXT, font=("Consolas", 9),
                                highlightthickness=1, highlightbackground=BORDER)
        # Vertical scrollbar for the log.
        scroll = ttk.Scrollbar(viewer, orient="vertical", command=self.log_text.yview)
        # Connect both widgets.
        self.log_text.configure(yscrollcommand=scroll.set)
        # Place them.
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    # Runs the simulation on a separate manager so the user's data is not mixed.
    def _run_simulation(self):
        # Run the 24 operations without printing to the console.
        summary = ejecutar_simulaciones(GestorFJ(), imprimir=False)
        # Show the summary.
        messagebox.showinfo(
            "Simulation finished",
            f"Operations: {summary['operaciones']}\nSuccessful: {summary['exitosas']}\n"
            f"Controlled errors: {summary['errores_controlados']}\n"
            f"As expected: {summary['segun_lo_esperado']} of {summary['operaciones']}")
        # Update the status bar.
        self._set_status("Simulation finished: 24 operations, no crashes. See the log.", "ok")

    # Loads the last lines of sistema.log into the text area.
    def _refresh_log(self):
        # Try to read the file.
        try:
            # Read all lines.
            lines = ARCHIVO_LOG.read_text(encoding="utf-8").splitlines()
        # The file may not exist yet or be unreadable.
        except OSError:
            # Show a friendly message.
            lines = ["(The log file could not be read yet.)"]
        # Unlock the text area.
        self.log_text.config(state="normal")
        # Clear it.
        self.log_text.delete("1.0", "end")
        # Insert the last 300 lines.
        self.log_text.insert("end", "\n".join(lines[-300:]))
        # Scroll to the end.
        self.log_text.see("end")
        # Lock it again.
        self.log_text.config(state="disabled")

    # ------------------------------------------------------------------ refresh
    # Refreshes tables, counters and combo boxes from the manager.
    def _refresh_all(self):
        # Remember the selected rows so the selection survives the refresh.
        kept = {table: [table.item(i)["values"][0] for i in table.selection()]
                for table in (self.s_table, self.r_table)}
        # Customers table.
        self.c_table.delete(*self.c_table.get_children())
        # Fill it.
        for index, c in enumerate(self.manager.clientes):
            # Alternating background colour.
            tags = ("odd",) if index % 2 else ()
            # Insert one row per customer.
            self.c_table.insert("", "end",
                                values=(c.identificador, c.nombre, c.documento, c.correo, c.telefono),
                                tags=tags)
        # Services table.
        self.s_table.delete(*self.s_table.get_children())
        # Fill it.
        for index, s in enumerate(self.manager.servicios):
            # Alternating background and red text if disabled.
            tags = (("odd",) if index % 2 else ()) + (() if s.disponible else ("bad",))
            # Insert one row per service.
            self.s_table.insert("", "end",
                                values=(s.identificador, type(s).__name__, s.nombre,
                                        f"${s.costo_base:,.2f}", s.unidad_duracion,
                                        "yes" if s.disponible else "no"),
                                tags=tags)
        # Colours used for each reservation state.
        state_tags = {"Confirmada": ("good",), "Cancelada": ("bad",), "Fallida": ("bad",),
                      "Error crítico": ("bad",), "Pendiente": ("warn",)}
        # Reservations table.
        self.r_table.delete(*self.r_table.get_children())
        # Fill it.
        for index, r in enumerate(self.manager.reservas):
            # Alternating background plus a colour for the state.
            tags = (("odd",) if index % 2 else ()) + state_tags.get(r.estado.value, ())
            # Insert one row per reservation.
            self.r_table.insert("", "end",
                                values=(r.identificador, r.cliente.nombre, r.servicio.nombre,
                                        f"{r.duracion} {r.servicio.unidad_duracion}",
                                        r.estado.value, f"${r.costo_total:,.2f}"),
                                tags=tags)
        # Restore the selection in each table.
        for table, identifiers in kept.items():
            # Look for the rows with the remembered identifiers.
            rows = [row for row in table.get_children() if table.item(row)["values"][0] in identifiers]
            # Select them again.
            table.selection_set(rows)
        # Customer combo box.
        self.r_customer_box["values"] = [f"{c.identificador} - {c.nombre}" for c in self.manager.clientes]
        # Service combo box (only available services can be reserved).
        self.r_service_box["values"] = [f"{s.identificador} - {s.nombre}" for s in self.manager.servicios
                                        if s.disponible]
        # Update the counters of the profile card.
        self.stat_vars["clientes"].config(text=str(len(self.manager.clientes)))
        self.stat_vars["servicios"].config(text=str(len(self.manager.servicios)))
        self.stat_vars["reservas"].config(text=str(len(self.manager.reservas)))
        # Refresh the log view.
        self._refresh_log()


# Starts the application.
def iniciar_aplicacion():
    """Creates the window and enters the Tk main loop."""
    # Create the window.
    app = SoftwareFJApp()
    # Fill the tables for the first time.
    app._refresh_all()
    # Enter the event loop.
    app.mainloop()
