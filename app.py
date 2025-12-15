from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = '@Pandu2006' 

# --- Database Configuration ---
DB_CONFIG = {
    'user': 'root',         
    'password': '@Shannu2006', 
    'host': '127.0.0.1',    
    'database': 'hostel_management' 
}

# --- Database Connection Helper ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# --- Routes ---
@app.route('/')
def home():
    return render_template('HomePage.html')

@app.route('/student_login_page')
def student_login_page():
    return render_template('StudentLogin.html')

@app.route('/admin_login_page')
def admin_login_page():
    return render_template('AdminLogin.html')

@app.route('/warden_login_page')
def warden_login_page():
    return render_template('WardenLogin.html')

@app.route('/admin_login', methods=['POST'])
def admin_login():
    """
    Handles the form submission.
    Authenticates the user against Admin_id and Password columns.
    """
    if request.method == 'POST':
        # Get data from the HTML form's name attributes
        admin_id = request.form['admin_username']  # Input is treated as Admin_id
        password = request.form['admin_password']  # Input is treated as Password

        conn = get_db_connection()
        if conn is None:
            # Handle database connection failure
            return "Database connection failed. Please check your DB_CONFIG settings and MySQL server status.", 500

        cursor = conn.cursor(dictionary=True)

        try:
            # SQL Query: Check Admin_id and Password against the 'admin' table.
            # We fetch Admin_name to use for personalization on AdminPage.html.
            query = "SELECT Admin_name FROM admin WHERE Admin_id = %s AND Password = %s"
            
            # Execute the query safely using parameterization
            cursor.execute(query, (admin_id, password))
            admin_user = cursor.fetchone()

            if admin_user:
                # Authentication successful: Store admin name in session
                session['admin_name'] = admin_user['Admin_name']
                # Redirect to the admin home page route
                return redirect(url_for('admin_home'))
            else:
                # Authentication failed: Display error message
                return render_template('AdminLogin.html', error="Invalid Username or Password")

        except mysql.connector.Error as err:
            print(f"Database query error: {err}")
            return "An internal server error occurred during login verification.", 500
        finally:
            # Always close the cursor and connection
            cursor.close()
            conn.close()

@app.route('/warden_login', methods=['POST'])
def warden_login():
    if request.method == 'POST':
        warden_username = request.form['warden_username']
        warden_password = request.form['warden_password']
        
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed. Please check your DB_CONFIG settings and MySQL server status.", 500
        
        cursor = conn.cursor(dictionary=True)

        try:
            query = "SELECT Warden_id, Warden_name FROM warden WHERE Warden_id = %s AND Password = %s"
            cursor.execute(query, (warden_username, warden_password))
            warden_user = cursor.fetchone()

            if warden_user:
                session['warden_name'] = warden_user['Warden_name']
                session['warden_id'] = warden_user['Warden_id']
                return redirect(url_for('warden_home'))
            else:
                return render_template('WardenLogin.html', error="Invalid Username or Password")
        except mysql.connector.Error as err:
            print(f"Database query error: {err}")
            return "An internal server error occurred during login verification.", 500
        finally:
            # Always close the cursor and connection
            cursor.close()
            conn.close()

@app.route('/student_login', methods=['POST'])
def student_login():
    if request.method == 'POST':
        # User entered Student_id as username
        student_id = request.form['student_username'] 
        password = request.form['student_password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if Student_id and Password match
            query = "SELECT * FROM student WHERE Student_id = %s AND Password = %s"
            cursor.execute(query, (student_id, password))
            student = cursor.fetchone()

            if student:
                # Login Successful: Save Student_id in session
                session['student_id'] = student['Student_id']
                return redirect(url_for('student_home'))
            else:
                return render_template('StudentLogin.html', error="Invalid Username or Password")
        
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cursor.close()
            conn.close()

@app.route('/admin_home')
def admin_home():
    """Serves the Admin Home Page (AdminPage.html) only if the user is logged in."""
    # Check for the 'admin_name' in the session to ensure login
    if 'admin_name' in session:
        # Render the template, passing the admin_name for display
        return render_template('AdminPage.html', admin_name=session['admin_name'])
    else:
        # If not logged in, redirect to the login page
        return redirect(url_for('admin_login_page'))

@app.route('/student_signup_page')
def student_signup_page():
    # Only allow access if admin is logged in
    if 'admin_name' in session:
        return render_template('Student_SignUp.html')
    else:
        return redirect(url_for('admin_login_page'))

@app.route('/register_student', methods=['POST'])
def register_student():
    if request.method == 'POST':
        # 1. Fetch data from the form
        name = request.form['name']
        email = request.form['email']
        gender = request.form['select_gender']
        ph_no = request.form['phno']
        dob = request.form['dob']
        address = request.form['address']
        branch = request.form['branch']
        year = request.form['year_of_study']
        student_id = request.form['Student_id']
        hostel_name = request.form['hostel'] # This gives "Freshers Block", not "H001"
        room_no = request.form['room_no']
        password = request.form['password'] # Note: In production, hash this password!

        # 2. Map Hostel Name to Hostel_id
        # Based on your database image, we must map the names to IDs manually or via query.
        # Simple mapping approach:
        hostel_map = {
            "Freshers Block": "H001",
            "Aryabatta Block": "H002",
            "Ratan Tata Block": "H003",
            "MSR Gowramma": "H004"
        }
        
        hostel_id = hostel_map.get(hostel_name)

        if not hostel_id:
            return "Error: Invalid Hostel Name selected."

        conn = get_db_connection()
        if conn is None:
            return "Database connection error", 500
        
        cursor = conn.cursor()

        try:
            # 3. Check Hostel Availability First
            check_query = "SELECT Avail_capacity FROM hostel WHERE Hostel_id = %s"
            cursor.execute(check_query, (hostel_id,))
            result = cursor.fetchone() # returns a tuple, e.g., (6,) or dictionary depending on config
            
            # Handle fetchone returning tuple or dict based on your cursor setup
            current_capacity = result[0] if isinstance(result, tuple) else result['Avail_capacity']

            if current_capacity <= 0:
                return f"Error: {hostel_name} is fully occupied!"

            # 4. Insert Student Data
            insert_student_query = """
                INSERT INTO student 
                (Student_id, Student_name, Email, Gender, Ph_no, DOB, Addrs, Branch, Year, Hostel_id, Room_no, Password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            student_values = (student_id, name, email, gender, ph_no, dob, address, branch, year, hostel_id, room_no, password)
            cursor.execute(insert_student_query, student_values)

            # 5. Decrease Hostel Capacity
            update_hostel_query = "UPDATE hostel SET Avail_capacity = Avail_capacity - 1 WHERE Hostel_id = %s"
            cursor.execute(update_hostel_query, (hostel_id,))

            # 6. Commit the transaction (Save changes)
            conn.commit()
            
            # 7. Success - Redirect back to Admin Home or show success message
            return f"""
                <script>
                    alert('Student Registered Successfully and Capacity Updated!');
                    window.location.href = '{url_for('admin_home')}';
                </script>
            """

        except mysql.connector.Error as err:
            conn.rollback() # Undo changes if error occurs
            print(f"Error: {err}")
            return f"Error adding student: {err}"
            
        finally:
            cursor.close()
            conn.close()

@app.route('/warden_signup_page')
def warden_signup_page():
    # Security check: Ensure admin is logged in
    if 'admin_name' in session:
        return render_template('Warden_SignUp.html')
    else:
        return redirect(url_for('admin_login_page'))

# In app.py, replace the 'register_warden' function with this updated version:

@app.route('/register_warden', methods=['POST'])
def register_warden():
    if request.method == 'POST':
        # 1. Fetch data from the form
        name = request.form['name']
        email = request.form['email']
        gender = request.form['select_gender']
        ph_no = request.form['phno']
        age = request.form['age']
        dob = request.form['dob']
        address = request.form['address']
        salary = request.form['salary']  # <--- NEW: Get salary from the form
        warden_id = request.form['warden_id']
        hostel_name = request.form['hostel_name']
        username = request.form['username']
        password = request.form['password']

        # 2. Map Hostel Name to Hostel_id
        hostel_map = {
            "Freshers Block": "H001",
            "Aryabatta Block": "H002",
            "Ratan Tata Block": "H003",
            "MSR Gowramma": "H004"
        }
        
        hostel_id = hostel_map.get(hostel_name)

        if not hostel_id:
            return "Error: Invalid Hostel Name selected."

        conn = get_db_connection()
        if conn is None:
            return "Database connection error", 500
        
        cursor = conn.cursor()

        try:
            # 3. Insert Warden Data
            insert_query = """
                INSERT INTO warden 
                (Warden_id, Warden_name, Email, Gender, Ph_no, Age, DOB, Addrs, Salary, Hostel_id, Password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # We now pass the 'salary' variable instead of the hardcoded default
            values = (warden_id, name, email, gender, ph_no, age, dob, address, salary, hostel_id, password)
            
            cursor.execute(insert_query, values)
            conn.commit()

            return f"""
                <script>
                    alert('Warden Registered Successfully!');
                    window.location.href = '{url_for('admin_home')}';
                </script>
            """

        except mysql.connector.Error as err:
            conn.rollback()
            print(f"Error: {err}")
            return f"Error adding warden: {err}"
            
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

# --- Update Hostel Logic ---

@app.route('/update_hostel_page')
def update_hostel_page():
    if 'admin_name' in session:
        return render_template('Update_hostel.html')
    else:
        return redirect(url_for('admin_login_page'))

@app.route('/perform_hostel_update', methods=['POST'])
def perform_hostel_update():
    if 'admin_name' not in session:
        return redirect(url_for('admin_login_page'))

    if request.method == 'POST':
        hostel_name = request.form['hostel']
        # Treat 'new_capacity' as the AMOUNT TO ADD (e.g., 3, 6, 9)
        added_capacity = int(request.form['new_capacity'])

        # 1. Validation: Capacity must be divisible by 3
        if added_capacity % 3 != 0:
            return "Error: Capacity must be a multiple of 3 (e.g., 3, 6, 9) because 1 room = 3 members."

        # Calculate number of new rooms to create
        num_new_rooms = added_capacity // 3

        # 2. Map Hostel Name to ID
        hostel_map = {
            "Freshers Block": "H001",
            "Aryabatta Block": "H002",
            "Ratan Tata Block": "H003",
            "MSR Gowramma": "H004"
        }
        hostel_id = hostel_map.get(hostel_name)
        if not hostel_id:
            return "Error: Invalid Hostel Name."

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 3. Find the current highest room number for this hostel
            cursor.execute("SELECT MAX(Room_no) FROM rooms WHERE Hostel_id = %s", (hostel_id,))
            result = cursor.fetchone()
            max_room_no = result[0]

            # If no rooms exist yet, define a starting point based on Hostel ID
            # H001 -> starts at 100, H002 -> 200, etc.
            if max_room_no is None:
                if hostel_id == 'H001': max_room_no = 100
                elif hostel_id == 'H002': max_room_no = 200
                elif hostel_id == 'H003': max_room_no = 300
                elif hostel_id == 'H004': max_room_no = 400

            # 4. Create the new rooms in a loop
            current_room_num = max_room_no
            
            for _ in range(num_new_rooms):
                current_room_num += 1 # Increment room number (e.g., 102 -> 103)
                
                # Insert new room with capacity 3
                insert_room_query = """
                    INSERT INTO rooms (Hostel_id, Room_no, total_capacity, avail_capacity)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_room_query, (hostel_id, current_room_num, 3, 3))

            # 5. Update the Main Hostel Table (Total and Available)
            update_hostel_query = """
                UPDATE hostel 
                SET Total_capacity = Total_capacity + %s, 
                    Avail_capacity = Avail_capacity + %s 
                WHERE Hostel_id = %s
            """
            cursor.execute(update_hostel_query, (added_capacity, added_capacity, hostel_id))

            conn.commit()

            return f"""
                <script>
                    alert('Successfully added {num_new_rooms} new room(s) and increased capacity by {added_capacity}!');
                    window.location.href = '{url_for('admin_home')}';
                </script>
            """

        except mysql.connector.Error as err:
            conn.rollback()
            return f"Database Error: {err}"
        finally:
            cursor.close()
            conn.close()

@app.route('/update_warden_salary_page')
def update_warden_salary_page():
    # Security: Only allow if admin is logged in
    if 'admin_name' in session:
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed", 500
        
        cursor = conn.cursor(dictionary=True)
        try:
            # Fetch all wardens to populate the dropdown
            cursor.execute("SELECT Warden_id, Warden_name, Salary FROM warden")
            wardens = cursor.fetchall()
            
            # Pass the list of wardens to the template
            return render_template('Update_warden-salary.html', wardens=wardens)
            
        except mysql.connector.Error as err:
            return f"Database Error: {err}"
        finally:
            cursor.close()
            conn.close()
    else:
        return redirect(url_for('admin_login_page'))

@app.route('/get_warden_details', methods=['GET'])
def get_warden_details():
    # Get the ID sent by the JavaScript
    warden_id = request.args.get('warden_id')
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch Name and Salary for this ID
        query = "SELECT Warden_name, Salary FROM warden WHERE Warden_id = %s"
        cursor.execute(query, (warden_id,))
        result = cursor.fetchone()
        
        if result:
            # Send back the data as JSON (JavaScript Object Notation)
            return jsonify({'name': result['Warden_name'], 'salary': result['Salary']})
        else:
            return jsonify({'error': 'Warden not found'}), 404
            
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/perform_warden_salary_update', methods=['POST'])
def perform_warden_salary_update():
    if 'admin_name' not in session:
        return redirect(url_for('admin_login_page'))

    if request.method == 'POST':
        warden_id = request.form['warden_id']
        new_salary = request.form['new_salary']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            update_query = "UPDATE warden SET Salary = %s WHERE Warden_id = %s"
            cursor.execute(update_query, (new_salary, warden_id))
            conn.commit()
            
            return f"""
                <script>
                    alert('Salary updated successfully!');
                    window.location.href = '{url_for('admin_home')}';
                </script>
            """
        except mysql.connector.Error as err:
            conn.rollback()
            return f"Error: {err}"
        finally:
            cursor.close()
            conn.close()

# ----------Warden Options----------

@app.route('/warden_home')
def warden_home():
    """Serves the Warden Home Page (WardenPage.html) only if the user is logged in."""
    if 'warden_name' in session:
        return render_template('WardenPage.html', warden_name=session['warden_name'], warden_id=session['warden_id'])
    else:
        return redirect(url_for('warden_login_page'))

# --- Warden Outpass Logic ---

@app.route('/outpass_approval_page')
def outpass_approval_page():
    # 1. Security Check
    if 'warden_id' not in session:
        return redirect(url_for('warden_login_page'))

    warden_id = session['warden_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 2. Find out which Hostel this Warden manages
        cursor.execute("SELECT Hostel_id FROM warden WHERE Warden_id = %s", (warden_id,))
        warden_data = cursor.fetchone()

        if not warden_data:
            return "Error: Warden details not found."
        
        warden_hostel_id = warden_data['Hostel_id']

        # 3. Fetch ONLY 'Pending' requests for this specific Hostel
        # We JOIN with the student table to get the Student's Name
        query = """
            SELECT o.*, s.Student_name 
            FROM outpass o
            JOIN student s ON o.Student_id = s.Student_id
            WHERE o.Hostel_id = %s AND o.status = 'Pending'
        """
        cursor.execute(query, (warden_hostel_id,))
        pending_requests = cursor.fetchall()

        return render_template('Outpass_approval.html', requests=pending_requests)

    except mysql.connector.Error as err:
        return f"Database Error: {err}"
    finally:
        cursor.close()
        conn.close()

@app.route('/update_outpass_status', methods=['POST'])
def update_outpass_status():
    if 'warden_id' not in session:
        return redirect(url_for('warden_login_page'))

    # Get data from the hidden form inputs
    outpass_id = request.form['outpass_id']
    action = request.form['action'] # Will be 'approve' or 'reject'

    new_status = "Approved" if action == "approve" else "Rejected"

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the status in the database
        query = "UPDATE outpass SET status = %s WHERE Outpass_id = %s"
        cursor.execute(query, (new_status, outpass_id))
        conn.commit()
        
        return redirect(url_for('outpass_approval_page'))
        
    except mysql.connector.Error as err:
        return f"Error updating status: {err}"
    finally:
        cursor.close()
        conn.close()

# --- Warden Room Change Logic ---

@app.route('/room_change_approval_page')
def room_change_approval_page():
    if 'warden_id' not in session:
        return redirect(url_for('warden_login_page'))
        
    warden_id = session['warden_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Get Warden's Hostel ID
        cursor.execute("SELECT Hostel_id FROM warden WHERE Warden_id = %s", (warden_id,))
        warden_data = cursor.fetchone()
        
        if not warden_data:
            return "Error: Warden data not found."
            
        hostel_id = warden_data['Hostel_id']
        
        # 2. Fetch Pending Requests for THIS Hostel
        # JOIN with student table to show the name
        query = """
            SELECT c.*, s.Student_name 
            FROM change_room c
            JOIN student s ON c.Student_id = s.Student_id
            WHERE c.hostel_id = %s AND c.status = 'Pending'
        """
        cursor.execute(query, (hostel_id,))
        requests = cursor.fetchall()
        
        return render_template('hostel_room_change_approval.html', requests=requests)
        
    except mysql.connector.Error as err:
        return f"Database Error: {err}"
    finally:
        cursor.close()
        conn.close()

@app.route('/perform_room_change_action', methods=['POST'])
def perform_room_change_action():
    if 'warden_id' not in session:
        return redirect(url_for('warden_login_page'))

    # Get Form Data
    change_id = request.form['change_id']
    action = request.form['action'] # 'approve' or 'reject'
    student_id = request.form['student_id']
    current_room = request.form['current_room']
    new_room = request.form['new_room']
    hostel_id = request.form['hostel_id'] # Passed hidden from form
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if action == 'reject':
            # Simple Status Update
            cursor.execute("UPDATE change_room SET status = 'Rejected' WHERE Change_id = %s", (change_id,))
            msg = "Request Rejected."
            
        elif action == 'approve':
            # --- COMPLEX LOGIC: Check Capacity & Swap Rooms ---
            
            # 1. Check if New Room has space
            cursor.execute("SELECT avail_capacity FROM rooms WHERE Hostel_id = %s AND Room_no = %s", (hostel_id, new_room))
            room_data = cursor.fetchone()
            
            # Handle if room doesn't exist or is full
            if not room_data:
                return "Error: Target room does not exist."
            
            avail = room_data[0] # Tuple index 0
            
            if avail <= 0:
                return f"""<script>alert('Cannot Approve: Room {new_room} is FULL!'); window.location.href='/room_change_approval_page';</script>"""

            # 2. Update Old Room (Increase Capacity)
            cursor.execute("UPDATE rooms SET avail_capacity = avail_capacity + 1 WHERE Hostel_id = %s AND Room_no = %s", (hostel_id, current_room))

            # 3. Update New Room (Decrease Capacity)
            cursor.execute("UPDATE rooms SET avail_capacity = avail_capacity - 1 WHERE Hostel_id = %s AND Room_no = %s", (hostel_id, new_room))

            # 4. Update Student Table (Assign new room)
            cursor.execute("UPDATE student SET Room_no = %s WHERE Student_id = %s", (new_room, student_id))

            # 5. Mark Request as Approved
            cursor.execute("UPDATE change_room SET status = 'Approved' WHERE Change_id = %s", (change_id,))
            msg = "Request Approved and Room Swapped Successfully."

        conn.commit()
        return redirect(url_for('room_change_approval_page'))

    except mysql.connector.Error as err:
        conn.rollback()
        return f"Database Error: {err}"
    finally:
        cursor.close()
        conn.close()
#---------- Student Options ----------

@app.route('/student_home')
def student_home():
    # Check if student is logged in
    if 'student_id' in session:
        student_id = session['student_id']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Query 1: Get Student Details
            query_student = """
                SELECT s.*, h.Hostel_name 
                FROM student s 
                JOIN hostel h ON s.Hostel_id = h.Hostel_id 
                WHERE s.Student_id = %s
            """
            cursor.execute(query_student, (student_id,))
            student_data = cursor.fetchone()

            # Query 2: Get Outpass History
            query_outpass = "SELECT * FROM outpass WHERE Student_id = %s ORDER BY Outpass_id DESC"
            cursor.execute(query_outpass, (student_id,))
            outpass_data = cursor.fetchall() 
            
            # --- NEW: Query 3: Get Room Change Requests ---
            query_changes = "SELECT * FROM change_room WHERE Student_id = %s ORDER BY Change_id DESC"
            cursor.execute(query_changes, (student_id,))
            change_data = cursor.fetchall()
            
            # Pass ALL three datasets to the template
            return render_template('StudentPage.html', 
                                   student=student_data, 
                                   outpasses=outpass_data, 
                                   room_changes=change_data) # <--- Added this
            
        except mysql.connector.Error as err:
            return f"Error fetching data: {err}"
        finally:
            cursor.close()
            conn.close()
    else:
        return redirect(url_for('student_login_page'))

@app.route('/outpass_generation')
def outpass_generation():
    if 'student_id' in session:
        student_id = session['student_id']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # JOIN query to get Student details AND Hostel Name
            query = """
                SELECT s.Student_id, s.Student_name, s.Room_no, h.Hostel_name 
                FROM student s 
                JOIN hostel h ON s.Hostel_id = h.Hostel_id 
                WHERE s.Student_id = %s
            """
            cursor.execute(query, (student_id,))
            student_data = cursor.fetchone()
            
            # Pass the student_data to the HTML page
            return render_template('Generate_outpass.html', student=student_data)
            
        except mysql.connector.Error as err:
            return f"Error fetching data: {err}"
        finally:
            cursor.close()
            conn.close()
    else:
        return redirect(url_for('student_login_page'))

@app.route('/submit_outpass', methods=['POST'])
def submit_outpass():
    # Security check: User must be logged in
    if 'student_id' not in session:
        return redirect(url_for('student_login_page'))

    if request.method == 'POST':
        # 1. Get data from the form (These keys must match HTML name attributes)
        student_id = session['student_id']
        hostel_name = request.form['hostel']      # HTML name="hostel"
        room_no = request.form['roomNumber']      # HTML name="roomNumber"
        reason = request.form['reason']           # HTML name="reason"
        from_date = request.form['fromDate']      # HTML name="fromDate"
        to_date = request.form['toDate']          # HTML name="toDate"
        
        # 2. Map Hostel Name to Hostel_id
        hostel_map = {
            "Freshers Block": "H001",
            "Aryabatta Block": "H002",
            "Ratan Tata Block": "H003",
            "MSR Gowramma": "H004"
        }
        hostel_id = hostel_map.get(hostel_name)

        if not hostel_id:
            return "Error: Invalid Hostel Name selected."

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 3. Logic to Auto-Increment ID (Integer)
            # Find the highest ID currently in the table
            cursor.execute("SELECT MAX(Outpass_id) FROM outpass")
            result = cursor.fetchone()
            max_id = result[0]

            if max_id is not None:
                # If IDs exist (e.g., 5), the new ID is 6
                outpass_id = max_id + 1
            else:
                # If table is empty, start with 1
                outpass_id = 1
            
            status = "Pending"

            # 4. Insert into outpass table
            # Columns must match your database exactly: room_no is included here
            query = """
                INSERT INTO outpass 
                (Outpass_id, Student_id, Hostel_id, room_no, from_date, to_date, reason, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (outpass_id, student_id, hostel_id, room_no, from_date, to_date, reason, status)
            
            cursor.execute(query, values)
            conn.commit()

            # 5. Success - Redirect to student home
            return f"""
                <script>
                    alert('Outpass Request Submitted Successfully! ID: {outpass_id}');
                    window.location.href = '{url_for('student_home')}';
                </script>
            """

        except mysql.connector.Error as err:
            conn.rollback()
            return f"Error submitting outpass: {err}"
        
        finally:
            cursor.close()
            conn.close()

# --- Change Room Logic ---

@app.route('/change_room_page')
def change_room_page():
    if 'student_id' in session:
        student_id = session['student_id']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Fetch Student Details + Hostel Name dynamically
            query = """
                SELECT s.Student_id, s.Student_name, s.Room_no, h.Hostel_name 
                FROM student s 
                JOIN hostel h ON s.Hostel_id = h.Hostel_id 
                WHERE s.Student_id = %s
            """
            cursor.execute(query, (student_id,))
            student_data = cursor.fetchone()
            
            if student_data:
                # Pass the data to the HTML template
                return render_template('ChangeRoom_request.html', student=student_data)
            else:
                return "Error: Student data not found."
                
        except mysql.connector.Error as err:
            return f"Database Error: {err}"
        finally:
            cursor.close()
            conn.close()
    else:
        return redirect(url_for('student_login_page'))

@app.route('/submit_change_room', methods=['POST'])
def submit_change_room():
    if 'student_id' not in session:
        return redirect(url_for('student_login_page'))

    if request.method == 'POST':
        # 1. Get Data from Form
        student_id_form = request.form['student_id'] # From input field
        current_room = request.form['current_room']
        new_room = request.form['requested_room']
        reason = request.form['reason']
        
        # Security: Prefer session ID over form ID, or validate they match
        logged_in_id = session['student_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 2. Get the Hostel_id for this student (Required for the table)
            # We need to know which hostel the student is currently in
            cursor.execute("SELECT Hostel_id FROM student WHERE Student_id = %s", (logged_in_id,))
            result = cursor.fetchone()
            
            if not result:
                return "Error: Student record not found."
            
            # Handle tuple vs dictionary cursor depending on your config
            # Your get_db_connection uses default cursor here, so it returns tuple
            hostel_id = result[0] 

            # 3. Generate Change_id (Auto-increment logic)
            cursor.execute("SELECT MAX(Change_id) FROM change_room")
            max_id_result = cursor.fetchone()
            max_id = max_id_result[0]

            if max_id is not None:
                change_id = max_id + 1
            else:
                change_id = 1
            
            status = "Pending"

            # 4. Insert into change_room table
            query = """
                INSERT INTO change_room 
                (Change_id, Student_id, hostel_id, current_room, new_room, reason, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            # Note: Using logged_in_id ensures the request is filed for the actual user
            values = (change_id, logged_in_id, hostel_id, current_room, new_room, reason, status)
            
            cursor.execute(query, values)
            conn.commit()

            return f"""
                <script>
                    alert('Room Change Request Submitted Successfully! Request ID: {change_id}');
                    window.location.href = '{url_for('student_home')}';
                </script>
            """

        except mysql.connector.Error as err:
            conn.rollback()
            return f"Database Error: {err}"
        finally:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    # Run the application. Use debug=False in a production environment.
    app.run(debug=True)