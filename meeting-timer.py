from tkinter import *
from tkinter import ttk
from tkinter import font
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import datetime
import json
import os
import webbrowser
import subprocess
import threading


# Global variables
timeremaining_warning = 240 
timeremaining_critical = 180
fullscreen = False

color_bg = "#282c34"
color_mute = "#abb2bf"
color_green = "#8dc270"
color_highlights = "#ffffff"
color_button = "#4b89da"
color_button_text = "#ffffff"

def set_input_theme():
    root.tk_setPalette(background=color_bg, foreground=color_highlights)

def play_audio(file_path):
    if os.name == 'nt':
        subprocess.Popen(['powershell', 'New-Object', 'Media.SoundPlayer', file_path]).wait()
    elif os.name == 'posix':
        subprocess.Popen(['aplay', file_path]).wait()
    elif os.name == 'darwin':
        subprocess.Popen(['afplay', file_path]).wait()

def play_alarm_sound_async():
    threading.Thread(target=play_audio("alarm.wav")).start()


def show_success_message():
    success_dialog = Toplevel(root)
    success_dialog.title("Success")
    success_dialog.configure(background=color_bg)
    
    lbl_success = Label(success_dialog, text="Meeting added successfully.", font=fntSmall, foreground=color_highlights, background=color_bg)
    lbl_success.pack(padx=20, pady=10)
    
    ok_button = Button(success_dialog, text="OK", font=fntSmall, bg=color_button, fg=color_button_text, command=success_dialog.destroy)
    ok_button.pack(padx=20, pady=10)
   
    success_dialog.update_idletasks()
    x = (success_dialog.winfo_screenwidth() - success_dialog.winfo_reqwidth()) / 2
    y = (success_dialog.winfo_screenheight() - success_dialog.winfo_reqheight()) / 2
    success_dialog.geometry("+%d+%d" % (x, y))


    success_dialog.focus_set()
    success_dialog.grab_set()
    success_dialog.wait_window(success_dialog)


def add_meeting_info():
    set_input_theme() 
    title = simpledialog.askstring("Input", "Enter meeting title:", parent=root)
    if title is None:
        return
    speaker = simpledialog.askstring("Input", "Enter speaker name:", parent=root)
    if speaker is None:
        return
    end_date = simpledialog.askstring("Input", "Enter end date (YYYYMMDD):", parent=root)
    if end_date is None:
      return

    end_time1 = simpledialog.askstring("Input", "Enter end time (HHMMSS):", parent=root)
    if end_time1 is None:
     return

    end_time = end_date + end_time1


    try:
        datetime.datetime.strptime(end_time, '%Y%m%d%H%M%S')
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Please enter date in YYYYMMDDHHMMSS format.")
        return

    meeting_link = simpledialog.askstring("Input", "Enter meeting link (optional):", parent=root)
    if meeting_link is None:
        return
    
    if os.path.exists('meetings.json'):
        with open('meetings.json', 'r') as file:
            data = json.load(file)
    else:
        data = []

    data.append({
        'title': title,
        'speaker': speaker,
        'endtime': end_time,
        'link': meeting_link
    })

    with open('meetings.json', 'w') as file:
        json.dump(data, file, indent=4)

    update_agenda()
    
    show_success_message()

    sessionTitle.set("")
    currentSpeaker.set("")

redirected = False
def update_agenda():
    global timeremaining_warning  
    now = datetime.datetime.now()
    realTime.set(now.strftime('%H:%M'))

    with open('meetings.json', 'r') as json_file:
        data = json.load(json_file)

    remaining_time = None  

    for session in data:
        endtime = datetime.datetime.strptime(session['endtime'], '%Y%m%d%H%M%S')
        if now < endtime:
            sessionTitle.set(session['title'])
            currentSpeaker.set(session['speaker'])
            remainder = endtime - now
            remainder = remainder - datetime.timedelta(microseconds=remainder.microseconds)

            if now > (endtime - datetime.timedelta(seconds=timeremaining_warning)):
                lblCountdownTime.configure(foreground='orange')
            elif now > (endtime - datetime.timedelta(seconds=timeremaining_critical)):
                lblCountdownTime.configure(foreground='red')
            else:
                lblCountdownTime.configure(foreground=color_green)

            remaining_time = remainder
            if remainder.total_seconds() == 0 and session['link']:
                response = messagebox.askyesno("Join Meeting", "The meeting is about to start. Do you want to join?")
                if response:
                    webbrowser.open_new(session['link'])
                    redirected = True
                else:
                    redirected = False
                
            elif 5 <= remainder.total_seconds() <= 10:
                play_alarm_sound_async()
            break 

    if remaining_time is not None:  
        remainingTime.set(str(remaining_time))

    root.after(1000, update_agenda)


root = Tk()
imgicon = PhotoImage(file=os.path.join(os.path.dirname(os.path.realpath(__file__)),'icon.gif'))
root.tk.call('wm', 'iconphoto', root._w, imgicon)
root.geometry("800x600")  
root.title("Meeting Timer (sagar, jay, varun)")
root.configure(background=color_bg)
root.bind("x", quit)
style = ttk.Style()
style.theme_use('classic')
style.configure("Red.TLabel", fg='red')

fntNormal = font.Font(family='League Gothic', size=30, weight='bold')
fntForCountdown = font.Font(family='League Gothic', size=60, weight='bold')
fntForTitle = font.Font(family='League Gothic', size=50, weight='bold')
fntSmall = font.Font(family='League Gothic', size=18, weight='bold')

remainingTime = StringVar()
sessionTitle = StringVar()
realTime = StringVar()
currentSpeaker = StringVar()

lblRealTime = ttk.Label(root, textvariable=realTime, font=fntNormal, foreground=color_mute, background=color_bg)
lblRealTime.place(relx=0.9, rely=0.1, anchor=CENTER)

lblTimeRemaining = ttk.Label(root, text="Time Remaining: ", font=fntSmall, foreground=color_mute, background=color_bg)
lblTimeRemaining.place(relx=0.5, rely=0.45, anchor=CENTER)

lblTitle =  ttk.Label(root, textvariable=sessionTitle, font=fntForTitle, foreground=color_highlights, background=color_bg)
lblTitle.place(relx=0.5, rely=0.2, anchor=CENTER)

lblSpeaker =  ttk.Label(root, textvariable=currentSpeaker, font=fntNormal, foreground=color_highlights, background=color_bg)
lblSpeaker.place(relx=0.5, rely=0.3, anchor=CENTER)

lblCountdownTime = ttk.Label(root, textvariable=remainingTime, font=fntForCountdown, foreground=color_green, background=color_bg)
lblCountdownTime.place(relx=0.5, rely=0.6, anchor=CENTER)

btnAddMeeting = Button(root, text="Add Meeting", font=fntSmall, bg=color_button, fg=color_button_text, command=add_meeting_info)
btnAddMeeting.place(relx=0.5, rely=0.8, anchor=CENTER)

root.after(1000, update_agenda)

root.mainloop()
