import sqlite3
from tkinter import *
from tkinter import messagebox
from datetime import datetime

summary_window = None
conn = sqlite3.connect('survey.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS survey_responses(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
dob TEXT,
phone TEXT,
favorite_food TEXT,
age INTEGER,
answers TEXT
)

""")

conn.commit()
# Store survey answers and age list
ages = []
survey_data = []

# Main application
app = Tk()
app.title("Survey Form")
app.geometry("800x700")

# Declared variables
name_var = StringVar()
email_var = StringVar()
phone_var = StringVar()
dob_var = StringVar()
food_var = StringVar(value="None")

# Survey questions and options
questions = [
    "I like to watch movies",
    "I like to listen to radio",
    "I like to eat out",
    "I like to cook",
    "I like to watch Tv"
]
options = ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
responses = []

# Name of Survey
Label(app, text="Please complete the survey form ;)", font=("Arial", 16)).pack(pady=10)

# Survey form and questions
form_frame = Frame(app)
form_frame.pack(pady=10)


Label(form_frame, text=" what is your full Names:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
Entry(form_frame, textvariable=name_var, width=40).grid(row=0, column=1)


Label(form_frame, text="What is your email Address:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
Entry(form_frame, textvariable=email_var, width=40).grid(row=1, column=1)


Label(form_frame, text="Please type in your date of birth in the same format (YYYY-MM-DD):").grid(row=2, column=0, sticky=W, padx=5, pady=5)
Entry(form_frame, textvariable=dob_var, width=40).grid(row=2, column=1)


Label(form_frame, text="What is your phone number (060........):").grid(row=3, column=0, sticky=W, padx=5, pady=5)
Entry(form_frame, textvariable=phone_var, width=40).grid(row=3, column=1)

# Four Favorite Foods
Label(form_frame, text="Between the Four foods which is your favorite:").grid(row=4, column=0, sticky=W, padx=5, pady=5)
food_frame = Frame(form_frame)
food_frame.grid(row=4, column=1, sticky=W)
for food in ["Pizza", "Pap and Wors", "Pasta", "Salad"]:
    Radiobutton(food_frame, text=food, variable=food_var, value=food).pack(side=LEFT)

# Survey Section
Label(app, text="Please answer the following survey questions:;)", font=("Arial", 14)).pack(pady=10)
survey_frame = Frame(app)
survey_frame.pack()
#-------------------------------------------------------------------------------
for q in questions:
    var = IntVar(value=0)
    responses.append(var)
    Label(survey_frame, text=q, font=("Arial", 10)).pack(anchor=W)
    row = Frame(survey_frame)
    row.pack(anchor=W)
    for i, opt in enumerate(options, 1):
        Radiobutton(row, text=opt, variable=var, value=i).pack(side=LEFT)

# Validation for the form's questions
#------------------------------------------------------------------------------------
def register():
    name = name_var.get().strip()
    email = email_var.get().strip()
    phone = phone_var.get().strip()
    dob_str = dob_var.get().strip()

    if not name.replace(" ", "").isalpha():
       messagebox.showerror("!!!!!!!!!", "Name must contain only letters.")
       return
        
    if not phone.isdigit() or len(phone) != 10:
        messagebox.showerror("!!!!!!!!!", "Phone number must be exactly 10 digits.")
        return
    
    try:
    
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        age = (datetime.now() - dob).days // 365
    except ValueError:
        messagebox.showerror("!!!!!!!!!!", "Invalid date format. Use YYYY-MM-DD.")
        return
    if age < 5:
        messagebox.showerror("!!!!!!!!!!!", "You must be at least 5 years old.")
        return

    answers = [var.get() for var in responses]
    answers_str = ",".join(str(a) for a in answers)


    cursor.execute("""
    INSERT INTO survey_responses(name,email,dob,phone,favorite_food,age,
    answers)
    VALUES(?,?,?,?,?,?,?)
    """,(name, email, dob_str, phone, food_var.get(), age, answers_str))   

    conn.commit()             

 # ages are saved  for stats
    ages.append(age)

#clears the form 
    name_var.set("")
    email_var.set("")
    phone_var.set("")
    dob_var.set("")
    food_var.set("None")
    for var in responses:
        var.set(0)


    # Show success message
    messagebox.showinfo("Success", "Survey answered successfully THANK YOU ;)!!!!!!")

#------------------------------------------------------------------------------------------

def view_summary():
    cursor.execute('SELECT COUNT(*), AVG(age), MIN(age), MAX(age) FROM survey_responses')
    result = cursor.fetchone()

    if result is None or result[0] ==0:
        messagebox.showinfo("!!!!!!!!!!!", "FILLLL IN THE SUREVET!!!!!!!!!")
        return

    count, avg_age, min_age, max_age = result
    summary = f"Total Surveys: {count}\n"
    summary += f"Average Age: {avg_age:.1f}\n" if avg_age is not None else "Average Age Users: N/A\n"
    summary += f"Youngest Age: {min_age}\n" if min_age is not None else "Youngest Age Users: N/A\n"
    summary += f"Oldest Age: {max_age}\n" if max_age is not None else "Oldest Age Users: N/A\n"
     
    foods = ["Pizza", "Pap and Wors","Pasta", "Salad"]
    for food in foods:
        cursor.execute('SELECT COUNT(*) FROM survey_responses WHERE favorite_food = ?', (food,))
        food_count = cursor.fetchone()[0]
        percent = (food_count / count) * 100 if count > 0 else 0
        summary += f"Percentage who like {food}: {percent:.1f}%\n"
        summary += "\n"

    #average rating for each survey questions
    #The answers
    avg_ratings = []


    for i in range(len(questions)):
        cursor.execute(f"""
           SELECT answers FROM survey_responses
           WHERE LENGTH(answers) > 0
        """)
        all_answers = cursor.fetchall()
        ratings = []
        for (ans_str,) in all_answers:
            ans_list = ans_str.split(",")
            if len(ans_list) > i:
                try:
                    rating = int(ans_list[i])
                    if rating > 0:  # only consider if answered
                        ratings.append(rating)
                except ValueError:
                    pass
        avg = sum(ratings) / len(ratings) if ratings else 0
        avg_ratings.append(avg)

    for q, avg in zip(questions, avg_ratings):
        summary += f"Average rating for '{q}': {avg:.2f}\n"



#----------------------------------
    global summary_window
    if summary_window and summary_window.winfo_exists():
        summary_window.lift()
        return
    summary_window = Toplevel(app)
    summary_window.title("Suery Summary")
    summary_window.geometry("700x600")
    summary_window.configure(bg="#ffffff")

    Label(summary_window, text="Survey Summary", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)
    text_area = Text(summary_window, wrap=WORD, font=("Arial", 11), bg="#f9f9f9")
    text_area.insert(END, summary)
    text_area.config(state=DISABLED)
    text_area.pack(padx=10, pady=10, fill=BOTH, expand=True)

    Button(summary_window, text="Back to Survey", command=summary_window.destroy,
           bg="#1BE929", fg="white", font=("Arial", 12), relief="flat").pack(pady=10) 

             
    

  

#?^^^^^^^^^^^^^^^^^^^^^^^

app.config(bg="#f4f4f4")  
bg_color = app["bg"]

Button(app, text="Submit Survey", command=register, width=20,
       bg=bg_color, activebackground=bg_color,
       relief="flat", highlightthickness=0).pack(pady=10)

# Correctly styled View Summary button
Button(app, text="View Summary", command=view_summary, width=20,
       bg=bg_color, activebackground=bg_color,
       relief="flat", highlightthickness=0).pack(pady=5)


def on_closing():
    conn.close()
    app.destroy()


def on_close_summary():
        global summary_window
        summary_window.destroy()
        summary_window = None
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()

#referemces
#https://www.google.com/search?q=tkinter&oq=tk&gs_lcrp=EgZjaHJvbWUqDAgCEAAYQxiABBiKBTIGCAAQRRg5MgoIARAuGLEDGIAEMgwIAhAAGEMYgAQYigUyDAgDEAAYQxiABBiKBTIYCAQQLhhDGIMBGMcBGLEDGNEDGIAEGIoFMhgIBRAuGEMYgwEYxwEYsQMY0QMYgAQYigUyDAgGEAAYQxiABBiKBTIHCAcQLhiABDIKCAgQABixAxiABDINCAkQLhivARjHARiABNIBCTk2OTRqMGoxNagCALACAA&sourceid=chrome&ie=UTF-8#fpstate=ive&vld=cid:660e6a6f,vid:epDKamC-V-8,st:0
#https://www.youtube.com/watch?v=pd-0G0MigUA