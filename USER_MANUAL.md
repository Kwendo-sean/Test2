# User Manual: Student Web Application

## Introduction
Welcome to the Student Web Application! This platform is designed to streamline various academic and administrative processes for both students and administrators. For students, it provides easy access to personal information, course resources, attendance records, fee details, and graduation status. For administrators, it offers tools to manage student data, educational resources, attendance tracking, and graduation procedures. This manual will guide you through the features and functionalities of the application.

## Table of Contents
*   **Student Guide**
    *   [Logging In](#1-logging-in)
    *   [Dashboard](#2-dashboard)
    *   [Viewing Attendance](#3-viewing-attendance)
    *   [Accessing Resources](#4-accessing-resources)
    *   [Graduation](#5-graduation)
    *   [AI Assistant](#6-ai-assistant)
*   **Admin Guide**
    *   [Admin Login](#1-admin-login)
    *   [Admin Dashboard](#2-admin-dashboard)
    *   [Managing Students](#3-managing-students)
    *   [Managing Resources](#4-managing-resources)
    *   [Managing Attendance](#5-managing-attendance)
    *   [Managing Graduation](#6-managing-graduation)

---
# Student Section User Manual

This manual provides guidance for students on how to use the features available in the student portal.

## 1. Logging In

To access your student account, you need to log in through the portal.

-   **Accessing the Login Page:**
    Navigate to the main page of the application. If you are not logged in, you will be automatically redirected to the login page. Alternatively, you can directly go to the `/login` URL.

-   **Input Fields:**
    You will see two fields on the login page:
    -   **Email:** Enter the email address associated with your student account.
    -   **Password:** Enter your account password.

-   **Successful Login:**
    Upon entering the correct email and password, you will be redirected to your personal **Student Dashboard**.

-   **Unsuccessful Login:**
    If the email or password you entered is incorrect, an error message "Invalid email or password" will be displayed on the login page. Please ensure your credentials are correct or contact administration if you continue to have issues.

## 2. Dashboard

The Dashboard is your central hub for viewing key information related to your academic progress and account details.

-   **Accessing the Dashboard:**
    You are automatically redirected to the Dashboard after a successful login. If you are already logged in, you can typically find a "Dashboard" link in the navigation menu.

-   **Information Displayed:**
    The Dashboard presents the following information:
    -   **Name:** Your full name (e.g., John Doe).
    -   **Admission Number:** Your unique student admission number (e.g., CYBJAN24-001).
    -   **Email:** Your registered email address.
    -   **Phone:** Your registered phone number.
    -   **Course:** The course you are enrolled in (e.g., Cyber Security).
    -   **Cohort:** Your specific class group or cohort (e.g., JAN24).
    -   **Fee Balance:**
        -   **Expected:** The total fee amount for your course.
        -   **Paid:** The amount of fee you have paid so far.
        -   **Balance:** The remaining fee amount you owe.
    -   **Next Class:** The date and time of your upcoming class, if scheduled and updated by the administration.
    -   **Graduation Status:** Your current status regarding graduation (e.g., Active, Registered, Graduated).

## 3. Viewing Attendance

This section allows you to track your class attendance.

-   **Navigating to the Attendance Page:**
    Look for an "Attendance" link in the navigation menu or on your Dashboard to access this page (typically `/attendance`).

-   **Information Displayed:**
    -   **Attendance Records:** A list of all your recorded class attendances, showing:
        -   **Date:** The date of the class.
        -   **Status:** Your attendance status for that class (e.g., Present, Absent).
    -   **Total Attendance Records:** The total number of classes for which attendance has been recorded.
    -   **Number of Days Absent:** The total count of classes you were marked as 'Absent'.
    -   **Attendance Percentage:** This is calculated as `(Total Present Days / Total Recorded Days) * 100%`. *(Note: The AI assistant uses this standard calculation; the direct attendance page might show an "absenteeism percentage" instead.)*

## 4. Accessing Resources

Find course materials and other relevant documents in the Resources section.

-   **Navigating to the Resources Page:**
    Click on the "Resources" link, usually found in the main navigation menu (typically `/resources`).

-   **Information Displayed:**
    -   **Resource List:** A list of resources specifically available for your course and cohort.
    -   **Resource Details:** For each resource, you will see:
        -   **Title:** The name of the resource (e.g., "Introduction to Python Slides").
        -   **Type:** The type of resource (e.g., PDF, Video, Link).
        -   **Link:** A clickable link to access the resource.
    -   **Accessing a Resource:** Click the "Open" or resource link. This will typically open the resource in a new browser tab or initiate a download.

## 5. Graduation

This section provides information about your graduation status and allows you to register for upcoming graduation events.

-   **Navigating to the Graduation Page:**
    Find and click the "Graduation" link in the site's navigation menu (typically `/graduation`).

-   **Information Displayed:**
    -   **Graduation Status:** Your current academic standing regarding graduation (e.g., "Awaiting Graduation", "Eligible", "Registered", "Graduated").
    -   **Upcoming Graduation Event:** The date of the next scheduled graduation ceremony, if announced.
    -   **Graduation Media:** Links to photos, videos, or other media from past graduation events, if available.

-   **Registering for Graduation:**
    If you are eligible, you can register for an upcoming graduation event:
    -   **Select Role:** Choose your role for the event (e.g., "Graduate" if you are the one graduating, or "Guest" if you are accompanying a graduate).
    -   **Enter Full Name:** Provide your full name as you wish it to appear for the registration.
    -   **Confirmation:**
        -   Upon successful registration, a message like "Registered successfully" will be displayed.
        -   If you have already registered, you will see a message like "You've already registered."

## 6. AI Assistant

The portal includes an AI Assistant to help you quickly find information and perform certain tasks. You can typically find an icon or a chatbox to interact with the assistant, often on the Dashboard.

-   **Interacting with the Assistant:**
    Type your questions or commands into the chat interface provided. The assistant processes your text input and provides a response.

-   **Types of Questions and Commands:**
    The AI assistant can understand requests related to:
    -   **Resources:** "Show me my course resources," "Are there any new documents for Cyber Security?"
    -   **Fee Balance:** "What's my fee balance?", "How much do I owe?"
    -   **Attendance:** "What's my attendance record?", "How many days was I absent?"
    -   **Next Class:** "When is my next class?", "What's the schedule for tomorrow?"
    -   **Graduation:** "Am I eligible for graduation?", "When is the next graduation ceremony?"
    -   **Summarization of Text:**
        -   To summarize specific text: "summarize: [paste your text here]"
        -   To summarize text from an attachment: Upload a text file and ask "summarize the attached document."
        -   To summarize a previous long message from the chat: "summarize that."
    -   **General Knowledge (Wikipedia):** "Tell me about Python," "What is data science?"
    -   **Greetings:** "Hello," "Good morning."
    -   **Help/Capabilities:** "What can you do?", "Help."
    -   **Personal Information:** "What are my student details?", "Show my profile."
    -   **Course Information:** "Tell me about my course."

-   **Assistant's Replies:**
    The assistant provides text-based replies. These may include direct answers, information retrieved from your student record, or links to relevant pages or resources. It may also provide suggestions for follow-up questions.

-   **Limitations:**
    -   **AI Model (Important):** The advanced AI model for complex summarization and general conversation (e.g., Flan-T5) is currently **disabled** due to resource constraints and a dummy model is in use. This means that for open-ended questions or summarization tasks not covered by specific rules, the assistant will likely respond with a message like: "AI model is currently disabled due to resource constraints."
    -   Specific information retrieval (fees, attendance, course details, Wikipedia summaries) is rule-based and should function as described.
    -   The assistant's knowledge is based on the data within the student portal.

---

# Admin Section User Manual

This guide is for administrators to manage the student portal.

## 1. Admin Login

To access the administrative functions, you need to log in to the admin panel.

-   **Accessing the Admin Login Page:**
    Navigate to the `/admin/admin-login` URL in your browser.

-   **Input Fields:**
    -   **Email:** Enter your administrator email address.
    -   **Password:** Enter your administrator password.

-   **Successful Login:**
    Upon successful authentication, you will be redirected to the **Admin Dashboard**.

-   **Unsuccessful Login:**
    If the credentials are incorrect, a message "Invalid credentials" will be flashed on the login page.

## 2. Admin Dashboard

The Admin Dashboard provides an overview of the portal's data.

-   **Accessing the Dashboard:**
    You are automatically redirected here after a successful admin login. It can also be accessed via a "Dashboard" link in the admin navigation (typically `/admin/dashboard`).

-   **Information Displayed:**
    The dashboard shows key statistics:
    -   **Total Students:** The total number of registered student accounts.
    -   **Graduation Registrations:** The number of students who have registered for graduation.
    -   **Average Attendance:** The overall average attendance percentage across all students and classes.
    -   **Total Resources:** The total number of learning resources uploaded to the system.

## 3. Managing Students

This section allows administrators to manage student accounts and their details.

-   **Navigating to the Manage Students Page:**
    Access this page via a link in the admin navigation menu, typically labeled "Manage Students" or similar (URL: `/admin/students`).

-   **Adding a New Student:**
    Use the form provided on the "Manage Students" page.
    -   **Input Fields:**
        -   Name
        -   Email
        -   Phone
        -   Course (select from a predefined list)
        -   Cohort (e.g., JAN24, SEP23)
        -   Password (for the new student account)
        -   Fee Expected (total amount)
        -   Fee Paid (initial amount paid)
        -   Graduation Status (e.g., Active, Awaiting Graduation)
    -   **Admission Number:** This is automatically generated based on the course and cohort (e.g., CYBJAN24-001) when the student is added.
    -   **Confirmation:** A message like "Student [Name] added successfully" will be displayed.

-   **Viewing Students:**
    -   Students are listed in a table on the "Manage Students" page.
    -   The list is paginated, typically showing 5 students per page.
    -   **Information Displayed (for each student):** Name, Admission Number, Email, Course, Cohort, Fee Balance, and Graduation Status. Links to edit or delete the student are usually provided.

-   **Editing a Student:**
    -   **Access:** Click an "Edit" link or button associated with a student in the list. This will take you to a page like `/admin/student/edit/<id>`.
    -   **Editable Fields:** You can modify most of the student's details, including:
        -   Name, Email, Phone, Course, Cohort
        -   Fee Expected, Fee Paid
        -   Graduation Status
        -   Completion Date (format: YYYY-MM-DD)
    -   **Updating Password:** To change the student's password, enter a new password in the "Password" field. If left blank, the password remains unchanged.
    -   **Confirmation:** A message like "Student [Name] updated successfully" will appear.

-   **Deleting a Student:**
    -   **Access:** Click a "Delete" button or link, usually found next to each student in the list or on their edit page (route typically `/admin/student/delete/<id>`). This is a POST request.
    -   **Action:** Deleting a student will remove their account and all their associated attendance records from the system.
    -   **Confirmation:** A message such as "Student [Name] and their attendance records deleted successfully" will be displayed.

## 4. Managing Resources

Administrators can add, view, and delete learning resources for students.

-   **Navigating to the Manage Resources Page:**
    Find a "Manage Resources" or similar link in the admin navigation (URL: `/admin/resources`).

-   **Adding a New Resource:**
    Use the form available on the "Manage Resources" page.
    -   **Input Fields:**
        -   **Title:** Name of the resource (e.g., "Week 1 Lecture Slides").
        -   **Type:** Category of the resource (e.g., PDF, Video, Document, Link).
        -   **Link:** The URL or path to the resource.
        -   **Course:** Select the course this resource is for.
        -   **Cohort:** Specify the cohort this resource is intended for.
    -   **Confirmation:** A message "Resource added successfully" will be shown.

-   **Viewing Resources:**
    -   All existing resources are listed on the "Manage Resources" page.
    -   **Information Displayed (for each resource):** Title, Type, Link, Course, and Cohort. A delete button is usually available for each resource.

-   **Deleting a Resource:**
    -   **Access:** Click a "Delete" button next to the resource you wish to remove (route typically `/admin/resource/delete/<id>`). This is a POST request.
    -   **Confirmation:** A message "Resource deleted successfully" will be displayed.

## 5. Managing Attendance

This section allows for recording and updating student attendance.

-   **Navigating to the Attendance Management Page:**
    Access via an "Attendance Management" or similar link in the admin navigation (URL: `/admin/attendance`).

-   **Filtering Students:**
    -   To easily find students, you can filter the student list by:
        -   **Course:** Select a course from the dropdown.
        -   **Cohort:** Select a cohort from the dropdown (cohorts relevant to the selected course may be shown).
    -   The list of students will update based on your filter criteria.

-   **Adding/Updating Attendance Records:**
    This is typically done via a form on the page.
    -   **Select Student:** Choose the student from a dropdown list (which may be populated by the filters).
    -   **Input Fields:**
        -   **Date:** Select the date of the class (format: YYYY-MM-DD). This field is required.
        -   **Status:** Choose "Present" or "Absent".
    -   **Updating Next Class Schedule:** Optionally, you can set or update the student's "Next Class" date and time (format: YYYY-MM-DDTHH:MM).
    -   **Confirmation:** A message like "Attendance record added" or "Attendance record updated" will flash upon submission. If a student or date is not selected, an error message will be shown.

-   **Viewing Recent Attendance:**
    The page also displays a list of the most recent attendance records logged in the system (e.g., the last 20 records), showing student name, date, and status.

## 6. Managing Graduation

Administrators handle graduation processes, including marking students as graduated and managing graduation event information.

-   **Navigating to the Manage Graduation Page:**
    Access this section through a "Manage Graduation" or similar link in the admin navigation (URL: `/admin/graduation`).

-   **Marking Students as Graduated:**
    -   A list of students eligible for graduation (i.e., not already marked as 'Graduated') is displayed.
    -   **Action:** Select a student from this list and use the provided mechanism (e.g., a button or form submission associated with that student) to change their status.
    -   The student's `graduation_status` will be updated to "Graduated".
    -   **Completion Date:** If the student does not have a `completion_date` set, it will be automatically set to the current date when they are marked as graduated.
    -   **Confirmation:** A message like "[Student Name] marked as Graduated" will be displayed.

-   **Adding Graduation Event Information:**
    Use the form on the "Manage Graduation" page to add or update details about graduation ceremonies or related media.
    -   **Input Fields:**
        -   **Graduation Date:** Enter the date of a graduation event (format: YYYY-MM-DD).
        -   **Media Title:** A title for any graduation-related media (e.g., "Graduation Ceremony Photos Class of 2023").
        -   **Media Link:** A URL to the graduation media.
    -   **Confirmation:** A message like "Graduation details updated" will be shown if new information is successfully added. If no new information is provided or if the information already exists, an appropriate message will be displayed.

-   **Viewing Eligible Students and Graduation Information:**
    The "Manage Graduation" page also displays:
    -   A list of students currently eligible for graduation.
    -   A list of all recorded graduation event dates.
    -   A list of all added graduation media titles and their links.
