import tkinter as tk
from tkinter import ttk, font, messagebox
from PIL import Image, ImageTk
import threading
import customtkinter
import json
import re
from posture_detection import *


class UserDataManager:
    def __init__(self):
        self.user_file = 'user_data.json'

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def validate_username(self, username):
        """Validate username format"""
        # Username should be 3-20 characters, alphanumeric and underscores only
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None

    def save_user_data(self, username, email):
        """Save username and email to a JSON file"""
        try:
            data = {}
            # Try to load existing data
            try:
                with open(self.user_file, 'r') as file:
                    data = json.load(file)
            except FileNotFoundError:
                pass
            
            # Update data
            data['username'] = username
            data['email'] = email
            
            # Save updated data
            with open(self.user_file, 'w') as file:
                json.dump(data, file)
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False

    def get_stored_data(self):
        """Retrieve stored user data"""
        try:
            with open(self.user_file, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            return {}

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None
def run_app(user_info):
    def start_camera():
        threading.Thread(target=start_posture_detection, daemon=True).start()

    def start_background_detection():
        threading.Thread(target=detect_posture_in_background, daemon=True).start()

    def close_app():
        root.destroy()
    def show_statistics():
        data = summarize_posture_data()
        if data["total_time"] == 0:
            tk.messagebox.showinfo("Statistics", "No data available yet!")
            return

        stats_window = tk.Toplevel()
        stats_window.title("Posture Analytics Dashboard")
        stats_window.geometry("1000x800")
        
        # Configure style
        style = ttk.Style()
        style.configure("Dashboard.TFrame", background="#f5f5f5")
        style.configure("Card.TFrame", background="white", relief="raised")
        style.configure("Dashboard.TLabel", background="#f5f5f5", font=("Helvetica", 12))
        style.configure("CardTitle.TLabel", background="white", font=("Helvetica", 14, "bold"))
        style.configure("Stats.TLabel", background="white", font=("Helvetica", 24, "bold"))
        
        # Main container
        main_frame = ttk.Frame(stats_window, style="Dashboard.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame, style="Dashboard.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text="Posture Analytics Dashboard",
            font=("Helvetica", 24, "bold"),
            style="Dashboard.TLabel"
        ).pack(side="left")
        
        # Create grid for cards
        grid_frame = ttk.Frame(main_frame, style="Dashboard.TFrame")
        grid_frame.pack(fill="both", expand=True)
        grid_frame.grid_columnconfigure((0, 1), weight=1, uniform="column")
        
        def create_card(parent, title):
            card = ttk.Frame(parent, style="Card.TFrame", padding=15)
            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
            return card
        
        def animate_progress(progress_bar, target_value, steps=50):
            current = 0
            step_size = target_value / steps
            
            def step():
                nonlocal current
                if current < target_value:
                    current += step_size
                    progress_bar["value"] = current
                    stats_window.after(20, step)
            
            step()
        
        def animate_value(label, target_value, prefix="", suffix="", steps=50, duration=1000):
            current = 0
            step_size = target_value / steps
            step_duration = duration / steps
            
            def step():
                nonlocal current
                if current < target_value:
                    current += step_size
                    label.config(text=f"{prefix}{int(current)}{suffix}")
                    stats_window.after(int(step_duration), step)
            
            step()
        
        # Card 1: Overall Statistics
        stats_card = create_card(grid_frame, "Overall Statistics")
        stats_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        active_time_percentage = (data["good_posture_time"] / data["total_time"]) * 100
        
        total_time_label = ttk.Label(stats_card, text="0", style="Stats.TLabel")
        total_time_label.pack(pady=10)
        animate_value(total_time_label, data["total_time"], suffix=" sec")
        
        ttk.Label(stats_card, text="Active Time Progress", style="Dashboard.TLabel").pack(pady=(20, 5))
        progress_bar = ttk.Progressbar(
            stats_card,
            orient="horizontal",
            length=300,
            mode="determinate",
            style="Accent.Horizontal.TProgressbar"
        )
        progress_bar.pack(pady=5)
        animate_progress(progress_bar, active_time_percentage)
        
        # Card 2: Pie Chart
        pie_card = create_card(grid_frame, "Posture Distribution")
        pie_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        def animate_pie():
            values = [data["good_posture_time"], data["bad_posture_time"]]
            colors = ["#4caf50", "#f44336"]
            
            for i in range(181):  # Rotate from 0 to 180 degrees
                ax.clear()
                ax.pie(
                    values,
                    labels=["Good Posture", "Bad Posture"],
                    autopct="%1.1f%%",
                    startangle=90 + i,
                    colors=colors,
                    wedgeprops=dict(width=0.7)
                )
                canvas.draw()
                stats_window.update()
                
        fig.patch.set_facecolor('#ffffff')
        canvas = FigureCanvasTkAgg(fig, pie_card)
        canvas.get_tk_widget().pack(pady=10)
        
        # Card 3: Daily Trends
        trends_card = create_card(grid_frame, "Daily Posture Trends")
        trends_card.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        fig2 = Figure(figsize=(10, 4), dpi=100)
        ax2 = fig2.add_subplot(111)
        
        dates = list(data["dates"].keys())
        good_posture = [data["dates"][date]["good_posture"] for date in dates]
        bad_posture = [data["dates"][date]["bad_posture"] for date in dates]
        
        def animate_bars():
            bar_height = max(max(good_posture), max(bad_posture))
            steps = 20
            
            for i in range(steps + 1):
                ax2.clear()
                current_good = [h * (i/steps) for h in good_posture]
                current_bad = [h * (i/steps) for h in bad_posture]
                
                ax2.bar(dates, current_good, label="Good Posture", color="#4caf50", alpha=0.8)
                ax2.bar(dates, current_bad, bottom=current_good, label="Bad Posture", color="#f44336", alpha=0.8)
                
                ax2.set_title("Daily Posture Trends", pad=20)
                ax2.set_ylabel("Time (seconds)")
                ax2.set_xlabel("Date")
                ax2.legend()
                ax2.grid(True, linestyle='--', alpha=0.7)
                
                fig2.tight_layout()
                canvas2.draw()
                stats_window.update()
                time.sleep(0.05)
        
        fig2.patch.set_facecolor('#ffffff')
        canvas2 = FigureCanvasTkAgg(fig2, trends_card)
        canvas2.get_tk_widget().pack(pady=10, fill="both", expand=True)
        
        # Start animations
        stats_window.after(100, animate_pie)
        stats_window.after(100, animate_bars)
        
        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close Dashboard",
            style="Accent.TButton",
            command=stats_window.destroy
        )
        close_btn.pack(pady=20)
        
        # Configure hover effects
        def on_enter(e):
            e.widget['style'] = 'AccentHover.TButton'
        
        def on_leave(e):
            e.widget['style'] = 'Accent.TButton'
        
        close_btn.bind('<Enter>', on_enter)
        close_btn.bind('<Leave>', on_leave)
    
    root = tk.Tk()
    root.title(f"Posture Corrector - Welcome {user_info['name']}")
   
    WARM_ORANGE = "#FF9B50"  # Warm orange background
    DARKER_ORANGE = "#FF7B29"  # Darker orange for hover states
    WHITE = "#FFFFFF"  # White text
    
    # Window setup
    window_width = 1280
    window_height = 720
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int((screen_height / 2) - (window_height / 2))
    position_left = int((screen_width / 2) - (window_width / 2))
    root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")
    # root.configure(bg=trans)

    # Set appearance mode
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("blue")
    
    # Define fonts
    title_font = customtkinter.CTkFont(family="Trebuchet MS", size=28, weight="bold")
    app_title_font = customtkinter.CTkFont(family="Trebuchet MS", size=32, weight="bold")
    button_font = customtkinter.CTkFont(family="Trebuchet MS", size=24, weight="bold")
    label_font = customtkinter.CTkFont(family="Trebuchet MS", size=14)

    # Header Frame (keeps original background)
    header_frame = customtkinter.CTkFrame(root, fg_color=WARM_ORANGE, height=150)
    header_frame.pack(fill="x", pady=(0, 0))
    header_frame.pack_propagate(False)  

    # Configure grid columns for header
    header_frame.grid_columnconfigure(1, weight=1)

    # Left section (Person icon and Hello message)
    left_header = customtkinter.CTkFrame(header_frame, fg_color=WARM_ORANGE)
    left_header.grid(row=0, column=0, sticky="w", padx=(20, 0))

    try:
        person_img = Image.open("person-workin.webp")
        ctk_person = customtkinter.CTkImage(light_image=person_img, dark_image=person_img, size=(100, 100))
        person_label = customtkinter.CTkLabel(left_header, image=ctk_person, text="")
        person_label.pack(side="left", padx=(0, 10))
    except Exception as e:
        print(f"Error loading person image: {e}")

    title_label = customtkinter.CTkLabel(
        left_header,
        text=f"Hello, {user_info['name']}",
        font=title_font,
        text_color=WHITE
    )
    title_label.pack(side="left")

    # Right section (Posture Sense title)
    right_header = customtkinter.CTkFrame(header_frame, fg_color=WARM_ORANGE)
    right_header.grid(row=0, column=2, sticky="e", padx=(0, 20))

    app_title = customtkinter.CTkLabel(
        right_header,
        text="Posture Sense",
        font=app_title_font,
        text_color=WHITE
    )
    app_title.pack(side="right")

    # Main content frame with background image
    main_content = customtkinter.CTkFrame(root, fg_color='transparent', bg_color='transparent')
    main_content.pack(fill="both", expand=True)
 
    # Load and set background image
    try:
        # Load the background image
        bg_image = Image.open("background.jpg")  # Replace with your image path
        # Resize image to fit the main content area
        bg_image = bg_image.resize((window_width, window_height - 150))  # Adjust height to account for header
        bg_photo = ImageTk.PhotoImage(bg_image)
        
        # Create a label with the background image
        bg_label = tk.Label(main_content, image=bg_photo)
        bg_label.image = bg_photo  # Keep a reference
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        print(f"Error loading background image: {e}")
        main_content.configure(fg_color=WHITE)  # Fallback color if image fails to load

    content_frame = customtkinter.CTkFrame(main_content, fg_color="transparent", bg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    try:
        # Load the background image
        bg_image = Image.open("background.jpg")  # Replace with your image path
        # Resize image to fit the main content area
        bg_image = bg_image.resize((window_width, window_height - 150))  # Adjust height to account for header
        bg_photo = ImageTk.PhotoImage(bg_image)
        
        # Create a label with the background image
        bg_label = tk.Label(content_frame, image=bg_photo)
        bg_label.image = bg_photo  # Keep a reference
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        print(f"Error loading background image: {e}")
        main_content.configure(fg_color=WHITE)
    # Left Frame (Logo)
    left_frame = customtkinter.CTkFrame(
    content_frame, 
    fg_color="transparent",
    bg_color="transparent",
    corner_radius=15, 
    width=240, 
    height=280
    )
    
    left_frame.pack(side="left", padx=20, pady=20, fill=None, expand=False)
    left_frame.pack_propagate(False)
    def create_round_logo(image_path, size=(200, 200)):
        from PIL import Image, ImageDraw, ImageOps
        # Open and resize the original image
        original_image = Image.open(image_path)
        original_image = original_image.resize(size, Image.Resampling.LANCZOS)

        # Create a new image with an alpha channel
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)

        # Draw a circular mask
        draw.ellipse((0, 0, size[0], size[1]), fill=255)

        # Create output image with transparent background
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        
        # Convert original image to RGBA if it isn't already
        if original_image.mode != 'RGBA':
            original_image = original_image.convert('RGBA')

        # Apply the circular mask to the original image
        output.paste(original_image, (0, 0))
        output.putalpha(mask)

        return output
    
    round_logo = create_round_logo("posture.png", size=(200, 200))
    ctk_logo = customtkinter.CTkImage(
        light_image=round_logo,
        dark_image=round_logo,
        size=(200, 200)
    )
    
    # Create and pack the label
    logo_label = customtkinter.CTkLabel(left_frame, image=ctk_logo, text="")
    logo_label.pack(expand=True)
    # Right Frame (Buttons)
    right_frame = customtkinter.CTkFrame(
    content_frame, 
    fg_color="transparent",
    bg_color="transparent"
)
    right_frame.pack(side="right", padx=0, pady=0, fill="both", expand=True)

    button_frame = customtkinter.CTkFrame(
    right_frame, 
    fg_color="transparent",
    bg_color="transparent"
)
    # button_frame.pack(pady=20, fill="x")

    # buttons = [
    #     {"text": "Show Camera", "command": start_camera},
    #     {"text": "Start Background Detection", "command": start_background_detection},
    #     {"text": "Show Statistics", "command": show_statistics},
    #     {"text": "Close", "command": close_app},
    # ]

    # for btn in buttons:
    #     button = customtkinter.CTkButton(
    #         button_frame,
    #         text=btn["text"],
    #         command=btn["command"],
    #         font=button_font,
    #         fg_color=WHITE,
    #         text_color=WARM_ORANGE,
    #         hover_color=DARKER_ORANGE,
    #         corner_radius=10,
    #         height=70,
    #         border_color=WHITE,
    #         border_width=2
    #     )
    #     button.configure(compound="center")
    #     button.pack(fill="x", pady=12, padx=20)
    def create_animated_button(parent, text, command, icon_name=None):
        """Create an animated button with hover effects and optional icon"""
        button_frame = customtkinter.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=15
        )
        
        # Define colors
        PRIMARY_COLOR = "#FF7E45"  # Warm orange
        HOVER_COLOR = "#FF6B2B"    # Darker orange
        TEXT_COLOR = "#FFFFFF"     # White
        SHADOW_COLOR = "#00000010" # Transparent black

        def on_enter(e):
            # Animate button on hover
            button.configure(
                fg_color=HOVER_COLOR,
                border_width=0,
                scale=1.02  # Slight scale up effect
            )
            # Update shadow
            shadow_label.configure(fg_color=SHADOW_COLOR)
            
        def on_leave(e):
            # Restore original state
            button.configure(
                fg_color=PRIMARY_COLOR,
                border_width=0,
                scale=1.0
            )
            # Reset shadow
            shadow_label.configure(fg_color="transparent")

        def on_click(e):
            # Click animation
            button.configure(scale=0.98)
            parent.after(100, lambda: button.configure(scale=1.0))
            command()

        # Create shadow effect
        shadow_label = customtkinter.CTkLabel(
            button_frame,
            text="",
            fg_color="transparent",
            width=40,
            height=5
        )
        shadow_label.place(relx=0.5, rely=0.95, anchor="center", relwidth=0.95, relheight=0.2)

        # Main button
        button = customtkinter.CTkButton(
            button_frame,
            text=text,
            command=command,
            font=("Helvetica", 16, "bold"),
            fg_color=PRIMARY_COLOR,
            text_color=TEXT_COLOR,
            hover_color=HOVER_COLOR,
            corner_radius=12,
            height=75,
            border_width=0,
            compound="right",
            anchor="center"
        )
        
        # Add icon if specified
        if icon_name:
            try:
                from PIL import Image
                icon = customtkinter.CTkImage(
                    light_image=Image.open(f"icons/{icon_name}.png"),
                    dark_image=Image.open(f"icons/{icon_name}.png"),
                    size=(24, 24)
                )
                button.configure(image=icon, compound="right", anchor="center")
            except Exception as e:
                print(f"Could not load icon {icon_name}: {e}")

        button.pack(fill="x", padx=5, pady=5)
        
        # Bind hover and click events
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<Button-1>", on_click)
        
        return button_frame
    def create_button_panel(parent):
        button_frame = customtkinter.CTkFrame(
            parent,
            fg_color="transparent"
        )
        button_frame.pack(pady=20, fill="x")

        buttons_config = [
            {
                "text": "Open Camera",
                "command": start_camera,
                "icon": "camera"  # Assuming you have camera.png in icons folder
            },
            {
                "text": "Start Detection",
                "command": start_background_detection,
                "icon": "detection"
            },
            {
                "text": "View Statistics",
                "command": show_statistics,
                "icon": "stats"
            },
            {
                "text": "Close Application",
                "command": close_app,
                "icon": "close"
            }
        ]
        
        for btn_config in buttons_config:
            btn_frame = create_animated_button(
                button_frame,
                text=btn_config["text"],
                command=btn_config["command"],
                icon_name=btn_config.get("icon")
            )
            btn_frame.pack(fill="x", pady=8, padx=20)
            

        return button_frame
    create_button_panel(right_frame)
    user_manager = UserDataManager()
    
    def save_user_data_callback():
        """Callback function for save button"""
        username = username_entry.get().strip()
        email = email_entry.get().strip()
        
        # Validate inputs
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
            
        if not email:
            messagebox.showerror("Error", "Please enter an email address")
            return
        
        if not user_manager.validate_username(username):
            messagebox.showerror("Error", "Username must be 3-20 characters long and contain only letters, numbers, and underscores")
            return
            
        if not user_manager.validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        if user_manager.save_user_data(username, email):
            messagebox.showinfo("Success", "User data saved successfully!")
            # Clear the entries
            username_entry.delete(0, 'end')
            email_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Failed to save user data")
    
    # Your existing window setup code here...
    # (everything up to content_frame setup)

    # User Data Collection Frame
    user_data_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
    user_data_frame.pack(side="left", padx=20, pady=20, fill="x", expand=True)

    # Username Field
    username_label = customtkinter.CTkLabel(
        user_data_frame,
        text="Enter your username:",
        font=label_font,
        text_color=WARM_ORANGE
    )
    username_label.pack(pady=(0, 5))

    username_entry = customtkinter.CTkEntry(
        user_data_frame,
        font=label_font,
        width=300,
        height=40,
        placeholder_text="Enter your username"
    )
    username_entry.pack(pady=(0, 15))

    # Email Field
    email_label = customtkinter.CTkLabel(
        user_data_frame,
        text="Enter your email for notifications:",
        font=label_font,
        text_color=WARM_ORANGE
    )
    email_label.pack(pady=(0, 5))

    email_entry = customtkinter.CTkEntry(
        user_data_frame,
        font=label_font,
        width=300,
        height=40,
        placeholder_text="Enter your email"
    )
    email_entry.pack(pady=(0, 15))

    # Try to load existing data
    stored_data = user_manager.get_stored_data()
    if 'username' in stored_data:
        username_entry.insert(0, stored_data['username'])
    if 'email' in stored_data:
        email_entry.insert(0, stored_data['email'])

    # Save Button
    save_button = customtkinter.CTkButton(
        user_data_frame,
        text="Save User Data",
        command=save_user_data_callback,
        font=button_font,
        fg_color=WHITE,
        text_color=WARM_ORANGE,
        hover_color=DARKER_ORANGE,
        corner_radius=10,
        height=40,
        border_color=WHITE,
        border_width=2
    )
    save_button.pack(pady=5)
    footer_frame = customtkinter.CTkFrame(root, fg_color=WARM_ORANGE, height=50)
    footer_frame.pack(fill="x", side="bottom")

    footer_label = customtkinter.CTkLabel(
        footer_frame,
        text="Stay Healthy, Stay Aligned!",
        font=("Helvetica", 14, "italic"),
        text_color=WHITE,
    )
    footer_label.pack(pady=10)

    root.mainloop()

