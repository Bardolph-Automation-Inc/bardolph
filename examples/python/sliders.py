#!/usr/bin/env python

"""
This program uses tkinter to display a panel of three sliders: one for
red, one for green, and one for blue. Each time you adjust a slider, 
a short script to update the light named "Lamp" is generated and run.
"""
import tkinter as tk

from bardolph.controller import ls_module

# Change to the name of your light.
#
light_name = "Lamp"


def on_slider_move(event=None):
    r = red_slider.get()
    g = green_slider.get()
    b = blue_slider.get()
    fmt = f"""
        units rgb
        red {r}
        green {g}
        blue {b}
        kelvin 3500
        duration 0.5
        set "{light_name}"
    """
    ls_module.run_script(fmt)


root = tk.Tk()
root.title("RGB Controller")
root.geometry("300x280")

tk.Label(root, text="Red", fg="red").pack()
red_slider = tk.Scale(root, from_=0, to=100,
                      orient="horizontal", command=on_slider_move)
red_slider.pack(fill="x", padx=20)

tk.Label(root, text="Green", fg="green").pack()
green_slider = tk.Scale(root, from_=0, to=100,
                        orient="horizontal", command=on_slider_move)
green_slider.pack(fill="x", padx=20)

tk.Label(root, text="Blue", fg="blue").pack()
blue_slider = tk.Scale(root, from_=0, to=100,
                       orient="horizontal", command=on_slider_move)
blue_slider.pack(fill="x", padx=20)

ls_module.configure()
ls_module.queue_script(f'set "{light_name}" duration 1 on "{light_name}"')
root.mainloop()
ls_module.queue_script(f'duration 1 off "{light_name}"')
