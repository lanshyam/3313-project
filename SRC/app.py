from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Your MySQL username
    'password': 'Ans19122004',  # Your MySQL password
    'database': 'expensetracker'
}

# Function to connect to MySQL database
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data.get("password", "")

    # Run C++ program to check password
    result = subprocess.run(['./Login'], input=password, capture_output=True, text=True)
    output = result.stdout.strip()

    if output == "success":
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail"})



@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        try:
            # Get the form data using request.form.get() to avoid KeyError
            category = request.form.get('category')
            date = request.form.get('date')
            expense_paid = request.form.get('expense_paid')
            total_expense = request.form.get('total_expense')
            user_id = request.form.get('user_id')

            # Print the data for debugging
            print(f"Category: {category}, Date: {date}, Paid: {expense_paid}, Total: {total_expense}, UserID: {user_id}")

            # Check if the required fields are present
            if not category or not date or not expense_paid or not total_expense or not user_id:
                return "Please fill in all fields."

            # Convert 'expense_paid' and 'total_expense' to float values
            expense_paid = float(expense_paid)
            total_expense = float(total_expense)

            # Create a database connection
            connection = get_db_connection()
            if connection is None:
                return "Error: Unable to connect to the database."

            cursor = connection.cursor()

            # Insert the expense data into the 'expense' table
            cursor.execute('''INSERT INTO expense (ExpenseCategory, DateOfExpense, ExpensePaid, TotalExpense, UserID)
                              VALUES (%s, %s, %s, %s, %s)''',
                           (category, date, expense_paid, total_expense, user_id))

            # Commit the transaction to the database
            connection.commit()

            # Close the database connection
            cursor.close()
            connection.close()

            # Redirect to the view_expenses page after successful insertion
            return redirect(url_for('view_expense'))

        except mysql.connector.Error as err:
            # Log MySQL error and return message
            print(f"Database Error: {err}")
            return f"Database Error: {err}"
        except Exception as e:
            # Log general error and return message
            print(f"Error occurred: {e}")
            return f"An error occurred: {e}"

    # Render the add_expense.html form if the method is GET
    return render_template('add_expense.html')

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        try:
            source = request.form['source']
            date = request.form['date']
            received = request.form['received']
            total = request.form['total']
            user_id = request.form['user_id']

            # Validate input (you can add more specific validation here)
            if not source or not date or not received or not total or not user_id:
                return "Please fill in all fields."

            connection = get_db_connection()
            if connection is None:
                return "Error: Unable to connect to the database."

            cursor = connection.cursor()

            # Insert data into the income table
            cursor.execute('''INSERT INTO income (IncomeSources, DateOfIncome, IncomeReceived, TotalIncome, UserID)
                              VALUES (%s, %s, %s, %s, %s)''', (source, date, received, total, user_id))

            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('view_income'))

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return f"Error: {err}"
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return f"Unexpected Error: {e}"

    return render_template('add_income.html')

@app.route('/add_report', methods=['GET', 'POST'])
def add_report():
    if request.method == 'POST':
        try:
            # Retrieve form data
            date = request.form.get('date')
            total_savings = request.form.get('total_savings')
            categories = request.form.get('categories')
            analysis_id = request.form.get('analysis_id')
            user_id = request.form.get('user_id')

            # Validate form data
            if not date or not total_savings or not categories or not user_id:
                return "Please fill in all required fields."

            total_savings = float(total_savings)

            # Database connection
            connection = get_db_connection()
            if connection is None:
                return "Error: Unable to connect to the database."

            cursor = connection.cursor()

            # Insert data into ExpenseReports table
            cursor.execute('''INSERT INTO ExpenseReports (Dates, TotalSavings, Categories, AnalysisID, UserID)
                              VALUES (%s, %s, %s, %s, %s)''',
                           (date, total_savings, categories, analysis_id, user_id))

            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('view_report'))

        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            return f"Database Error: {err}"
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return f"Unexpected Error: {e}"

    return render_template('add_report.html')

@app.route('/view_expense')
def view_expense():
    try:
        connection = get_db_connection()
        if connection is None:
            return "Error: Unable to connect to the database."

        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM expense')
        expenses = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('view_expense.html', expenses=expenses)
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return f"Database Error: {err}"
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return f"Unexpected Error: {e}"

@app.route('/view_income')
def view_income():
    try:
        connection = get_db_connection()
        if connection is None:
            return "Error: Unable to connect to the database."

        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM income')
        incomes = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('view_income.html', incomes=incomes)
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return f"Database Error: {err}"
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return f"Unexpected Error: {e}"


@app.route('/view_report')
def view_report():
    try:
        # Establish the database connection
        connection = get_db_connection()
        if connection is None:
            return "Error: Unable to connect to the database."

        # Create a cursor object to interact with the database
        cursor = connection.cursor(dictionary=True)

        # Execute the SQL query to fetch all records from ExpenseReports
        cursor.execute('SELECT * FROM ExpenseReports')
        reports = cursor.fetchall()

        # Close the cursor and database connection after query execution
        cursor.close()
        connection.close()

        # Render the template with the retrieved reports
        return render_template('view_report.html', reports=reports)

    except mysql.connector.Error as err:
        # Catch specific MySQL errors and log them
        print(f"Database Error: {err}")
        return f"Database Error: {err}"

    except Exception as e:
        # Catch any unexpected errors
        print(f"Unexpected Error: {e}")
        return f"Unexpected Error: {e}"
    
@app.route('/view_analysis')
def view_analysis():
    try:
        # Database connection
        connection = get_db_connection()
        if connection is None:
            return "Error: Unable to connect to the database."

        cursor = connection.cursor(dictionary=True)

        # Retrieve all rows from the Analysis table
        cursor.execute('SELECT * FROM Analysis')
        analyses = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('view_analysis.html', analyses=analyses)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return f"Database Error: {err}"
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return f"Unexpected Error: {e}"
    
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''INSERT INTO user (Username, Password, FirstName, LastName, PhoneNumber) 
                   VALUES (%s, %s, %s, %s, %s)'''
        cursor.execute(query, (username, password, first_name, last_name, phone_number))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('view_users'))

    return render_template('add_user.html')


# View Users Function
@app.route('/view_users')
def view_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_users.html', users=users)

@app.route('/view_incomesummary')
def view_incomesummary():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM incomesummary')
    income_summary = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_incomesummary.html', income_summary=income_summary)

@app.route('/view_range')
def view_range():
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL query to fetch all records from the 'search' table
    cursor.execute('SELECT * FROM search')
    search_results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_range.html', search_results=search_results)

@app.route('/view_transactiontime')
def view_transactiontime():
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL query to fetch all records from the 'transaction' table
    cursor.execute('SELECT * FROM transaction')
    transaction_results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_transactiontime.html', transaction_results=transaction_results)


@app.route('/view_user_expenses')
def view_user_expenses():
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL query to join the 'User' and 'Expense' tables
    query = '''
        SELECT User.Username, Expense.ExpenseCategory, Expense.DateOfExpense, Expense.ExpensePaid
        FROM User
        JOIN Expense ON User.UserID = Expense.UserID
    '''
    cursor.execute(query)
    user_expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_user_expenses.html', user_expenses=user_expenses)

if __name__ == '__main__':
    app.run(debug=True)