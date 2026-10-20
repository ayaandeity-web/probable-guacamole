import csv
import os
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import streamlit as st

fn = "students.csv"
cols = ["Roll no", "Name", "Class", "Section", "Marks"]


def load():
  students = []
  if os.path.exists(fn):
    with open(fn, "r", newline="") as f:
      for r in csv.reader(f):
        if len(r) == 5:
          try:
            students.append({
                "roll": int(r[0]),
                "name": r[1],
                "class": r[2],
                "section": r[3],
                "marks": int(r[4]),
            })
          except ValueError:
            continue
  return students


def save(students):
  with open(fn, "w", newline="") as f:
    w = csv.writer(f)
    for s in students:
      w.writerow([s["roll"], s["name"], s["class"], s["section"], s["marks"]])


# Authentication state
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if not st.session_state.logged_in:
  st.title("🎓 Student Management System - Login")
  username = st.text_input("Username")
  password = st.text_input("Password", type="password")
  if st.button("Login"):
    if username == "admin" and password == "1234":
      st.session_state.logged_in = True
      st.rerun()
    else:
      st.error("Wrong username or password")
else:
  st.title("🎓 Student Management System")
  if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

  students = load()

  # Sidebar Navigation
  st.sidebar.header("Navigation")
  choice = st.sidebar.radio(
      "Choose Action", [
          "View & Search",
          "Add Student",
          "Update Student",
          "Delete Student",
          "Statistics",
          "Performance Groups (AI)",
      ]
  )

  if choice == "View & Search":
    st.subheader("Student Records")
    search_query = st.text_input("Search by Roll No or Name").strip().lower()

    filtered = students
    if search_query:
      filtered = [
          s
          for s in students
          if str(s["roll"]) == search_query
          or search_query in s["name"].lower()
      ]

    if filtered:
      df = pd.DataFrame(filtered)
      df.columns = cols
      st.dataframe(df, use_container_width=True)
    else:
      st.info("No records found.")

    if st.button("Sort by Marks (Descending)"):
      students.sort(key=lambda x: x["marks"], reverse=True)
      save(students)
      st.success("Sorted by marks!")
      st.rerun()

  elif choice == "Add Student":
    st.subheader("Add New Student")
    with st.form("add_form"):
      roll = st.number_input("Roll No", min_value=1, step=1)
      name = st.text_input("Name")
      clas = st.text_input("Class")
      section = st.text_input("Section")
      marks = st.number_input("Marks (0-100)", min_value=0, max_value=100, step=1)
      submitted = st.form_submit_button("Add Student")
      if submitted:
        if not name or not clas or not section:
          st.error("Please fill all details.")
        elif any(s["roll"] == roll for s in students):
          st.error("Roll no already exists!")
        else:
          students.append({
              "roll": int(roll),
              "name": name,
              "class": clas,
              "section": section,
              "marks": int(marks),
          })
          save(students)
          st.success("Record added successfully!")

  elif choice == "Update Student":
    st.subheader("Update Student Record")
    roll_to_update = st.number_input("Enter Roll No to Update", min_value=1, step=1)
    target = next((s for s in students if s["roll"] == roll_to_update), None)

    if target:
      with st.form("update_form"):
        name = st.text_input("Name", value=target["name"])
        clas = st.text_input("Class", value=target["class"])
        section = st.text_input("Section", value=target["section"])
        marks = st.number_input(
            "Marks", min_value=0, max_value=100, value=target["marks"], step=1
        )
        updated = st.form_submit_button("Update Student")
        if updated:
          target["name"] = name
          target["class"] = clas
          target["section"] = section
          target["marks"] = int(marks)
          save(students)
          st.success("Record updated successfully!")
    else:
      st.warning("Enter a valid roll number existing in the system.")

  elif choice == "Delete Student":
    st.subheader("Delete Student Record")
    roll_to_del = st.number_input("Enter Roll No to Delete", min_value=1, step=1)
    if st.button("Delete"):
      initial_len = len(students)
      students = [s for s in students if s["roll"] != roll_to_del]
      if len(students) < initial_len:
        save(students)
        st.success("Record deleted successfully!")
        st.rerun()
      else:
        st.error("Record not found.")

  elif choice == "Statistics":
    st.subheader("Class Statistics")
    if not students:
      st.info("No records found.")
    else:
      marks_list = [s["marks"] for s in students]
      total = sum(marks_list)
      avg = total / len(marks_list)
      col1, col2, col3 = st.columns(3)
      col1.metric("Total Students", len(students))
      col2.metric("Total Marks", total)
      col3.metric("Average Marks", round(avg, 2))

      col4, col5 = st.columns(2)
      col4.metric("Highest Marks", max(marks_list))
      col5.metric("Lowest Marks", min(marks_list))

  elif choice == "Performance Groups (AI)":
    st.subheader("AI Performance Clustering (KMeans)")
    if len(students) < 3:
      st.warning("At least 3 students are needed for clustering.")
    else:
      marks_arr = np.array([[s["marks"]] for s in students])
      model = KMeans(n_clusters=3, n_init=10, random_state=0)
      model.fit(marks_arr)
      order = sorted(range(3), key=lambda i: model.cluster_centers_[i][0])
      names = ["Needs Improvement", "Average", "Excellent"]
      groups = {"Needs Improvement": [], "Average": [], "Excellent": []}
      for i in range(len(students)):
        pos = order.index(model.labels_[i])
        groups[names[pos]].append(students[i]["name"])

      for g_name, members in groups.items():
        st.markdown(f"**{g_name}**: {', '.join(members) if members else 'None'}")