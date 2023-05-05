import tkinter as tk
import csd_report as csd_report
import bu_report as bu_report


window = tk.Tk()

report_string = ""

greeting = tk.Label(text="auto report tool 1.0")

text_box = tk.Text(window,height=50, width=120)


def run_csd_report():
    global report_string
    report_string = csd_report.main()
    text_box.delete('1.0', tk.END)
    text_box.insert(tk.END, report_string)


def run_exec_report():
    global report_string
    report_string = bu_report.main()
    text_box.delete('1.0', tk.END)
    text_box.insert(tk.END, report_string)

button_csd = tk.Button(text="Run CSD Report", command = run_csd_report)


button_exec = tk.Button(text="Run Exec IT Report", command = run_exec_report)

greeting.pack()
button_csd.pack()
button_exec.pack()
text_box.pack()

window.mainloop()