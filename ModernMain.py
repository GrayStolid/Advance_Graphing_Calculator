#!/usr/bin/env python3
"""Tkinter GUI with Matplotlib Expression Plotter

A comprehensive application for plotting mathematical expressions in
different coordinate systems with real-time notation conversion
(prefix, infix, postfix).
"""

from customtkinter import CTkFrame as Frame, CTkLabel as Label
from customtkinter import StringVar, WORD, CTkEntry as Entry
from customtkinter import CTkButton as Button, CTk as Tk
from customtkinter import CTkTextbox as Text, BOTH, END, SUNKEN
from customtkinter import set_default_color_theme, set_appearance_mode
from customtkinter import CTkToplevel as Toplevel, CTkImage
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
from PIL import Image
import Speech2Text, OCR
import sys
import os

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
                                              NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
MATPLOTLIB_AVAILABLE = True

from expression_parser import ExpressionParser
from plotters import Plotter2D, Plotter3D, PlotterPolar, PlotterSpherical


# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
assets_addr_v = ".\\_internal\\Assets\\"


class ThemesAndAppear(ABC):
        
    def light_theme_m(self):
        set_default_color_theme("_internal/Themes/dark-blue.json")
        set_appearance_mode("light")
        self.root.destroy()
        self.root.update()
        main()
        
    def dark_theme_m(self):
        set_default_color_theme("_internal/Themes/dark-blue.json")
        set_appearance_mode("dark")
        self.root.destroy()
        self.root.update()
        main()

    def light_rose_theme_m(self, path_v = ""):
        set_default_color_theme("_internal/Themes/rose.json")
        set_appearance_mode("light")
        self.root.destroy()
        self.root.update()
        main()

    def dark_rose_theme_m(self, path_v = ""):
        set_default_color_theme("_internal/Themes/rose.json")
        set_appearance_mode("dark")
        self.root.destroy()
        self.root.update()
        del self.root, self
        main()

class ExpressionPlotterGUI(ThemesAndAppear):
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mathematical Expression Plotter")
        self.root.geometry("800x500+500+160")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize expression parser
        self.parser = ExpressionParser()
        
        # Create main frame
        self.main_frame = Frame(root)
        self.main_frame.grid(row=0, column=0, sticky=("wens"), padx=5, pady=5)
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        self.setup_ui()
        
        # Show matplotlib availability warning if needed
        if not MATPLOTLIB_AVAILABLE:
            self.show_matplotlib_warning()
    
    def show_matplotlib_warning(self):
        """Show warning about matplotlib availability"""
        warning_text = (
            "Matplotlib and NumPy are not available in this environment.\n"
            "The expression parsing and GUI interface will work, but plotting"
            " is disabled.\n\n"
            "To use plotting features, install dependencies:\n"
            "pip install matplotlib numpy"
        )
        messagebox.showwarning("Dependencies Missing", warning_text)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Expression input section
        self.setup_expression_input()
        
        # Notation display section
        self.setup_notation_display()
        
        # Tabbed plotting interface
        self.setup_plotting_tabs()
    
    def setup_expression_input(self):
        """Setup expression input section"""
        input_frame = ttk.LabelFrame(self.main_frame, text="Expression Input",
                                     padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=("we"),
                         pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        Label(input_frame, text="Expression:",
              text_color="#000000").grid(row=0, column=0,
                                         sticky="w",
                                         padx=(0, 10))
        
        self.expression_var = StringVar(value="x^2 + 2*x + 1")
        self.expression_entry = Entry(input_frame,
                                          textvariable = self.expression_var,
                                          font=('Consolas', 12))
        self.expression_entry.grid(row=0, column=1, sticky=("we"))
        
        parse_btn = Button(input_frame, text="Parse & Plot", width= 100,
                               command = lambda: self.parse_and_plot(3))
        parse_btn.grid(row=0, column=2, sticky="e", padx = (5,0))

        photo = CTkImage(light_image=Image.open(assets_addr_v +
                                                "Picure Symbol\\"\
                                                "Image2.png"),
                         dark_image=Image.open(assets_addr_v +
                                               "Picure Symbol\\"\
                                               "Image3.png"), size=(20, 20))
        image_btn = Button(input_frame, text="Image", image = photo, width= 50,
                               command = lambda: self.parse_and_plot(1))
        image_btn.grid(row=0, column=3, sticky="e", padx = (5,0))
        
        photo = CTkImage(light_image=Image.open(assets_addr_v +
                                                "Microphon Symbol\\"\
                                                "microphone2.png"),
                         dark_image=Image.open(assets_addr_v +
                                               "Microphon Symbol\\"\
                                               "microphone1.png"),
                                               size=(20, 20))
        audio_btn = Button(input_frame, text="Audio", image=photo,
                           width= 50,
                           command = lambda: self.parse_and_plot(2))
        audio_btn.grid(row=0, column=4, sticky="e", padx = (5,0))
        
        # Bind Enter key to parse
        self.expression_entry.bind('<Return>', lambda e: self.parse_and_plot(3))
    
    def setup_notation_display(self):
        """Setup notation display section"""
        notation_frame = ttk.LabelFrame(self.main_frame,
                                        text="Expression Notations",
                                        padding="10")
        notation_frame.grid(row=1, column=0, sticky=("wens"),
                            padx=(0, 10))
        notation_frame.columnconfigure(0, weight=1)
        
        # Infix notation
        Label(notation_frame, text="Infix:", text_color="#000000",
                  font=('Arial', 10, 'bold')).grid(row=0, column=0,
                                                   sticky="w", pady=(0, 5))
        self.infix_text = Text(notation_frame, height=3, wrap=WORD,
                                  font=('Consolas', 10), bg_color='#e8f4fd')
        self.infix_text.grid(row=1, column=0, sticky=("we"),
                             pady=(0, 10))
        
        # Prefix notation
        Label(notation_frame, text="Prefix:", text_color="#000000",
                  font=('Arial', 10, 'bold')).grid(row=2, column=0,
                                                   sticky="w", pady=(0, 5))
        self.prefix_text = Text(notation_frame, height=3, wrap=WORD,
                                   font=('Consolas', 10), bg_color='#f0f8e8')
        self.prefix_text.grid(row=3, column=0, sticky=("we"),
                              pady=(0, 10))
        
        # Postfix notation
        Label(notation_frame, text="Postfix:", text_color="#000000",
                  font=('Arial', 10, 'bold')).grid(row=4, column=0,
                                                   sticky="w", pady=(0, 5))
        self.postfix_text = Text(notation_frame,
                                    height=3, wrap=WORD,
                                    font=('Consolas', 10), bg_color='#fdf0e8')
        self.postfix_text.grid(row=5, column=0,
                               sticky=("we"), pady=(0, 10))
        
        # Parse tree
        Label(notation_frame, text="Parse Tree:", text_color="#000000",
                  font=('Arial', 10, 'bold')).grid(row=6, column=0,
                                                   sticky="w", pady=(0, 5))
        self.tree_text = Text(notation_frame, height=4, wrap=WORD,
                                 font=('Consolas', 9), bg_color='#f8f0fd')
        self.tree_text.grid(row=7, column=0, sticky=("we"))
        
        # Configure text widgets to expand
        for i in range(8):
            notation_frame.rowconfigure(i, weight=1 if i in [1, 3, 5, 7] else 0)
    
    def setup_plotting_tabs(self):
        """Setup tabbed plotting interface"""
        plot_frame = ttk.LabelFrame(self.main_frame, text="Plotting", padding="10")
        plot_frame.grid(row=1, column=1, sticky=("wens"))
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(plot_frame)
        self.notebook.grid(row=0, column=0, sticky=("wens"))
   
        
        # Create tabs
        self.setup_2d_tab()
        self.setup_3d_tab()
        self.setup_polar_tab()
        self.setup_spherical_tab()
        self.theme_selection_tab()

            
    def setup_2d_tab(self):
        """Setup 2D plotting tab"""
        tab_2d = Frame(self.notebook)
        self.notebook.add(tab_2d, text="2D Plot")
        tab_2d.columnconfigure(0, weight=1)
        tab_2d.rowconfigure(1, weight=1)
        
        # Controls frame
        controls_2d = Frame(tab_2d)
        controls_2d.grid(row=0, column=0, sticky=("we"), pady = 5, padx = 5)
        controls_2d.columnconfigure(1, weight=1)
        controls_2d.columnconfigure(3, weight=1)
        
        Label(controls_2d, text="X Range:").grid(row=0, column=0,
                                                     padx=(2, 5))
        self.x_min_var = StringVar(value="-10")
        Entry(controls_2d, textvariable=self.x_min_var,
                  width=40).grid(row=0, column=1, padx=(0, 5))
        Label(controls_2d, text="to").grid(row=0, column=2, padx=5)
        self.x_max_var = StringVar(value=" 10")
        Entry(controls_2d, textvariable=self.x_max_var, width=40).\
                           grid(row=0, column=3, padx=(0, 10))
        
        Button(controls_2d, text="Plot 2D",
                   command=self.plot_2d).grid(row=0, column=4)
        
        # Plot area
        self.plot_frame_2d = Frame(tab_2d, width = 500, height = 300)
        self.plot_frame_2d.grid(row=1, column=0, padx = 5, pady = (0, 5),
                                sticky=("wens"))
        
        if MATPLOTLIB_AVAILABLE:
            self.fig_2d = Figure(figsize=(5, 3), dpi=100)
            self.canvas_2d = FigureCanvasTkAgg(self.fig_2d,
                                               self.plot_frame_2d)
            self.canvas_2d.get_tk_widget().pack(fill=BOTH, expand=True)
        else:
            self.create_placeholder_plot(self.plot_frame_2d,
                                         "2D Plot\n(Matplotlib not available)")
    
    def setup_3d_tab(self):
        """Setup 3D plotting tab"""
        tab_3d = Frame(self.notebook)
        self.notebook.add(tab_3d, text="3D Plot")
        tab_3d.columnconfigure(0, weight=1)
        tab_3d.rowconfigure(1, weight=1)
        
        # Controls frame
        controls_3d = Frame(tab_3d)
        controls_3d.grid(row=0, column=0, sticky=("we"), pady = 5, padx = 5)
        controls_3d.columnconfigure(1, weight = 1)
        
        Label(controls_3d, text="Expression in x,y:").grid(row=0, column=0,
                                                           padx=(2, 5))
        self.expr_3d_var = StringVar(value="x^2 + y^2")
        Entry(controls_3d, textvariable=self.expr_3d_var).grid(row=0, column=1,
                                                               sticky = "we")
        Button(controls_3d, text="Plot 3D",
                   command=self.plot_3d).grid(row=0, column=2, padx=(5, 0),
                                              sticky="e")
        
        # Plot area
        self.plot_frame_3d = Frame(tab_3d, width = 400, height = 200)
        self.plot_frame_3d.grid(row=1, column=0, padx = 5, pady = (0, 5),
                                sticky=("wens"))
        
        if MATPLOTLIB_AVAILABLE:
            self.fig_3d = Figure(figsize=(4, 2), dpi=80)
            self.canvas_3d = FigureCanvasTkAgg(self.fig_3d, self.plot_frame_3d)
            self.canvas_3d.get_tk_widget().pack(fill=BOTH, expand=True)
        else:
            self.create_placeholder_plot(self.plot_frame_3d,
                                         "3D Plot\n(Matplotlib not available)")
    
    def setup_polar_tab(self):
        """Setup polar plotting tab"""
        tab_polar = Frame(self.notebook)
        self.notebook.add(tab_polar, text="Polar Plot")
        tab_polar.columnconfigure(0, weight=1)
        tab_polar.rowconfigure(1, weight=1)
        
        # Controls frame
        controls_polar = Frame(tab_polar)
        controls_polar.grid(row=0, column=0, sticky=("we"), pady = 5, padx = 5)
        controls_polar.columnconfigure(1, weight=1)
        
        Label(controls_polar, text="r(θ) =").grid(row=0, column=0,
                                                  padx=(2, 5))
        self.expr_polar_var = StringVar(value="((sin(t)*abs(cos(t))^0.5)/(sin(t)+7/5))-2*sin(t)+2")
        Entry(controls_polar, textvariable=self.expr_polar_var).\
                              grid(row=0, column=1, sticky = "we")
        Button(controls_polar, text="Plot Polar",
                   command=self.plot_polar).grid(row=0, column=2, padx=(5,0),
                                                 sticky="e")
        
        # Plot area
        self.plot_frame_polar = Frame(tab_polar, width = 400, height = 200)
        self.plot_frame_polar.grid(row=1, column=0, padx = 5, pady = (0, 5),
                                   sticky=("wens"))
        
        if MATPLOTLIB_AVAILABLE:
            self.fig_polar = Figure(figsize=(4, 2), dpi=80)
            self.canvas_polar = FigureCanvasTkAgg(self.fig_polar,
                                                  self.plot_frame_polar)
            self.canvas_polar.get_tk_widget().pack(fill=BOTH, expand=True)
        else:
            self.create_placeholder_plot(self.plot_frame_polar,
                                         "Polar Plot\n"
                                         "(Matplotlib not available)")
    
    def setup_spherical_tab(self):
        """Setup spherical plotting tab"""
        tab_spherical = Frame(self.notebook)
        self.notebook.add(tab_spherical, text="Spherical Plot")
        tab_spherical.columnconfigure(0, weight=1)
        tab_spherical.rowconfigure(1, weight=1)
        
        # Controls frame
        controls_spherical = Frame(tab_spherical)
        controls_spherical.grid(row=0, column=0, sticky=("we"),
                                pady = 5, padx = 5)
        controls_spherical.columnconfigure(1, weight=1)
        Label(controls_spherical, text="r(θ,φ) =").grid(row=0, column=0,
                                                        padx=(2, 5))
        self.expr_spherical_var = StringVar(value="1 + 0.3*cos(5*phi)*"
                                                     "sin(3*theta)")
        Entry(controls_spherical, textvariable=self.expr_spherical_var).\
                                  grid(row=0, column=1, sticky = "we")
        Button(controls_spherical, text="Plot Spherical",
                   command=self.plot_spherical).grid(row=0, column=2,
                                                     padx=(5,0), sticky = "e")
        
        # Plot area
        self.plot_frame_spherical = Frame(tab_spherical,
                                          width = 400, height = 200)
        self.plot_frame_spherical.grid(row = 1, column = 0,
                                       padx = 5, pady = (0, 5),
                                       sticky=("wens"))
        
        if MATPLOTLIB_AVAILABLE:
            self.fig_spherical = Figure(figsize=(5, 3), dpi=100)
            self.canvas_spherical = FigureCanvasTkAgg(self.fig_spherical,
                                                      self.plot_frame_spherical)
            self.canvas_spherical.get_tk_widget().pack(fill=BOTH, expand=True)
        else:
            self.create_placeholder_plot(self.plot_frame_spherical,
                                         "Spherical Plot\n(Matplotlib not available)")
    
    def theme_selection_tab(self):
        """Setup app themes tab"""
        tab_theme = Frame(self.notebook)
        self.notebook.add(tab_theme, text="App themes")
        tab_theme.columnconfigure(0, weight=1)
        tab_theme.rowconfigure(0, weight=1)
        
        # Controls frame
        controls_Themes = Frame(tab_theme)
        controls_Themes.grid(row=0, column=0, sticky="wens",
                                pady = 5, padx = 5)
        controls_Themes.columnconfigure(0, weight=1)

        theme_one = ttk.LabelFrame(controls_Themes, text="Blue",
                                   padding="10")
        theme_one.grid(row=0, column=0, sticky=("wens"), padx=5)
        theme_one.columnconfigure(0, weight=1)
                   
        light_butt_v = Button(theme_one, text = "Light", width = 333,
                              anchor = "center", hover_color = "#fff985",
                              fg_color = "#f0f0f0", border_color = "#000000",
                              text_color = "#000000",
                              command = self.light_theme_m)
        light_butt_v.grid(row=0, column=0, sticky=("we"), pady = 5)

        dark_butt_v = Button(theme_one, text = "Dark", width = 333,
                             anchor="center", hover_color = "#024ab0",
                             fg_color = "#f0f0f0", border_color = "#000000",
                             text_color = "#000000",
                             command = self.dark_theme_m)
        dark_butt_v.grid(row=1, column=0, sticky=("we"), pady = 5)

        theme_two = ttk.LabelFrame(controls_Themes, text = "Rose",
                                   padding="10")
        theme_two.grid(row=2, column = 0, sticky =("wens"), padx=5)
        theme_two.columnconfigure(0, weight=1)
                       
        light_butt_v2 = Button(theme_two, text = "Light", width = 333,
                              anchor = "center", hover_color = "#fff985",
                              fg_color = "#f0f0f0", border_color = "#000000",
                              text_color = "#000000",
                              command = self.light_rose_theme_m)
        light_butt_v2.grid(row=0, column=0, sticky=("we"), pady = 5)

        dark_butt_v2 = Button(theme_two, text = "Dark", width = 333,
                             anchor="center", hover_color = "#024ab0",
                             fg_color = "#f0f0f0", border_color = "#000000",
                             text_color = "#000000",
                             command = self.dark_rose_theme_m)
        dark_butt_v2.grid(row=1, column=0, sticky=("we"), pady = 5)

    
        
    def create_placeholder_plot(self, parent, text):
        """Create placeholder when matplotlib is not available"""
        placeholder = Label(parent, text=text, font=('Arial', 16), 
                             bg='#f0f0f0', fg='#666666', 
                             relief=SUNKEN, bd=2)
        placeholder.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    def parse_and_plot(self, expression):
        if expression == 1:
            self.expression_var.set(OCR.main())
        elif expression == 2:
            self.expression_var.set(Speech2Text.main())
        """Parse expression and update notation displays"""
        expression = self.expression_var.get().strip()
        if not expression:
            return
        
        try:
            # Parse expression
            infix = self.parser.normalize_expression(expression)
            prefix = self.parser.infix_to_prefix(infix)
            postfix = self.parser.infix_to_postfix(infix)
            tree_repr = self.parser.get_parse_tree_representation(infix)
            
            # Update displays
            self.update_text_widget(self.infix_text, infix)
            self.update_text_widget(self.prefix_text, prefix)
            self.update_text_widget(self.postfix_text, postfix)
            self.update_text_widget(self.tree_text, tree_repr)
            
            # Auto-plot in current tab
            current_tab = self.notebook.select()
            tab_text = self.notebook.tab(current_tab, "text")
            
            if tab_text == "2D Plot":
                self.plot_2d()
            elif tab_text == "Polar Plot":
                self.plot_polar()
            
        except Exception as e:
            messagebox.showerror("Parse Error", f"Error parsing expression: {str(e)}")
    
    def update_text_widget(self, widget, text):
        """Update text widget content"""
        widget.delete(1.0, END)
        widget.insert(1.0, text)
    
    def plot_2d(self):
        """Plot 2D function"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showinfo("Info", "Matplotlib not available for plotting")
            return
        
        try:
            expression = self.expression_var.get().strip()
            x_min = float(self.x_min_var.get())
            x_max = float(self.x_max_var.get())
            
            plotter = Plotter2D()
            plotter.plot(self.fig_2d, expression, x_min, x_max)
            self.canvas_2d.draw()
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error plotting 2D: {str(e)}")
    
    def plot_3d(self):
        """Plot 3D function"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showinfo("Info", "Matplotlib not available for plotting")
            return
        
        try:
            expression = self.expr_3d_var.get().strip()
            plotter = Plotter3D()
            plotter.plot(self.fig_3d, expression)
            self.canvas_3d.draw()
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error plotting 3D: {str(e)}")
    
    def plot_polar(self):
        """Plot polar function"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showinfo("Info", "Matplotlib not available for plotting")
            return
        
        try:
            expression = self.expr_polar_var.get().strip()
            plotter = PlotterPolar()
            plotter.plot(self.fig_polar, expression)
            self.canvas_polar.draw()
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error plotting polar: {str(e)}")
    
    def plot_spherical(self):
        """Plot spherical function"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showinfo("Info", "Matplotlib not available for plotting")
            return
        
        try:
            expression = self.expr_spherical_var.get().strip()
            plotter = PlotterSpherical()
            plotter.plot(self.fig_spherical, expression)
            self.canvas_spherical.draw()
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error plotting spherical: {str(e)}")


def main():
    """Main function to run the application"""
    root = Tk()
    app = ExpressionPlotterGUI(root)
    
    # Initial parse
    app.parse_and_plot(3)
    
    root.mainloop()
    del root, app

if __name__ == "__main__":
    main()
