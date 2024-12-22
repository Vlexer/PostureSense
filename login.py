
from utils import get_google_credentials, fetch_user_info
from tkinter import messagebox
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from app import run_app  # Ensure run_app is correctly imported
from PIL import Image, ImageTk, ImageDraw
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 
          'https://www.googleapis.com/auth/userinfo.email']
from google_auth_oauthlib.flow import InstalledAppFlow

def get_google_credentials():
    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return credentials
class LoginWindow:
    
    def __init__(self):
        # Root window configuration
        self.root = ctk.CTk()
        self.root.title("Posture Corrector - Login")
        window_width = 1280
        window_height = 720

        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the position to center the window on the screen
        position_top = int(screen_height / 2 - window_height / 2)
        position_left = int(screen_width / 2 - window_width / 2)

        # Set the window size and position it at the center
        self.root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")
        self.root.configure(bg="#f1f8e9")  # Subtle green background for professionalism

        # Main frame setup
        self.main_frame = ctk.CTkFrame(
            self.root, corner_radius=20, fg_color="#ffffff", width=500, height=700
        )
        self.main_frame.pack(pady=0, padx=0,fill="both", expand=True)

        # Create layout divisions
        self.create_header_section()
        self.create_content_section()
        self.create_footer_section()

    def create_header_section(self):
        # Header division
        header_frame = ctk.CTkFrame(
            self.main_frame, fg_color="transparent"
        )  # Transparent for clean division
        header_frame.pack(pady=(30, 20))

        # Logo
        try:
            from PIL import Image, ImageTk, ImageDraw

            logo_img = Image.open("posture.png")
            logo_img = logo_img.resize((180, 180), Image.Resampling.LANCZOS)

            # Create a mask for rounded edges
            mask = Image.new("L", logo_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, logo_img.size[0], logo_img.size[1]), fill=255)

            # Apply the mask to the logo
            rounded_logo = Image.new("RGBA", logo_img.size)
            rounded_logo.paste(logo_img, (0, 0), mask=mask)

            self.logo_photo = ImageTk.PhotoImage(rounded_logo)
            logo_label = ctk.CTkLabel(header_frame, image=self.logo_photo, text="")
            logo_label.pack()
        except Exception as e:
            print(f"Error loading rounded logo: {e}")

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Posture Corrector",
            font=("Arial Rounded MT Bold", 28),
            text_color="#2e7d32",  # Professional green
        )
        title_label.pack(pady=(20, 5))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Empower yourself to stay healthy and aligned",
            font=("Calibri", 16),
            text_color="#455a64",  # Neutral gray
        )
        subtitle_label.pack()

    def create_content_section(self):
        # Content division
        content_frame = ctk.CTkFrame(
            self.main_frame, fg_color="transparent"
        )
        content_frame.pack(pady=(30, 40), padx=40, fill="x")

        # Sign-in Button
        self.google_button = ctk.CTkButton(
            content_frame,
            text="Sign in with Google",
            command=self.handle_google_login,
            height=60,
            corner_radius=30,
            fg_color="#4caf50",  # Bright green
            hover_color="#388e3c",  # Darker green hover effect
            font=("Arial", 18, "bold"),
            text_color="#ffffff",  # White text for contrast
        )
        self.google_button.pack(pady=20, fill="x")

        # Divider
        divider_label = ctk.CTkLabel(
            content_frame,
            text="──────── OR ────────",
            font=("Calibri", 14),
            text_color="#9e9e9e",
        )
        divider_label.pack(pady=(20, 10))

        # Additional Info Label
        info_label = ctk.CTkLabel(
            content_frame,
            text="Use your credentials to access the app.",
            font=("Calibri", 14),
            text_color="#616161",
        )
        info_label.pack(pady=(10, 20))

        # Placeholder for additional login methods
        placeholder_label = ctk.CTkLabel(
            content_frame,
            text="[Future Options for Username/Password Login]",
            font=("Calibri", 14),
            text_color="#9e9e9e",
        )
        placeholder_label.pack(pady=10)

    def create_footer_section(self):
        # Footer division
        footer_frame = ctk.CTkFrame(
            self.main_frame, fg_color="transparent"
        )
        footer_frame.pack(side="bottom", pady=20)

        footer_label = ctk.CTkLabel(
            footer_frame,
            text="Stay Healthy. Stay Aligned.",
            font=("Calibri", 14, "italic"),
            text_color="#2e7d32",
        )
        footer_label.pack()
    def handle_google_login(self):
        try:
            self.credentials = get_google_credentials()
            self.user_info = fetch_user_info(self.credentials)

        # Delay import to avoid circular dependency
            from app import run_app

        # Close the current login window and open the main app
            self.root.destroy()
            run_app(self.user_info)

        except Exception as e:
            self.show_error(f"Login failed: {str(e)}")
    def show_error(self, message):
        messagebox.showerror(
            title="Error",
            message=message,
            icon="error"
        )
    
    def run(self):
        self.root.mainloop()

