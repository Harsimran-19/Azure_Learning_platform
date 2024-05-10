from flask import Flask, request, jsonify,render_template
import pymssql
import os
from engine import analyze_text

app = Flask(__name__)

# Azure SQL Database connection details
server = 'contentsev1918.database.windows.net'
database = 'contentdb'
username = 'db-root'
password = 'U9jcjzui35#'
driver = "{ODBC Driver 17 for SQL Server}"

# Initialize Azure Content Safety API (replace with actual API details)
# content_safety_api_key = os.environ.get("CONTENT_SAFETY_API_KEY")

# Connect to Azure SQL Database
def connect_to_database():
    try:
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        cursor = conn.cursor()
        print("Connection Successfull!")
        return conn, cursor
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None, None

# Create tables if they don't exist
def create_tables():
    conn, cursor = connect_to_database()
    if conn:
        try:
            # Check if normal_messages table exists
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'normal_messages')
                BEGIN
                    CREATE TABLE normal_messages (
                        id INT PRIMARY KEY IDENTITY(1, 1),
                        message TEXT
                    )
                END
            """)

            # Check if harmful_messages table exists
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'harmful_messages')
                BEGIN
                    CREATE TABLE harmful_messages (
                        id INT PRIMARY KEY IDENTITY(1, 1),
                        message TEXT
                    )
                END
            """)

            conn.commit()
            print("Tables created successfully!")
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
        finally:
            conn.close()
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/upload_form',methods=['GET'])
def form():
    return render_template('upload.html')
# Route to upload a message
@app.route('/upload', methods=['POST'])
def upload_message():
    try:
        # data = request.get_json()
        # message = data.get("message")
        message = request.form.get("message")
        print(message)
        # Check if message is safe using Azure Content Safety API (replace with actual implementation)
        is_safe = analyze_text(message)

        conn, cursor = connect_to_database()
        if conn:
            if is_safe:
                cursor.execute("INSERT INTO normal_messages (message) VALUES (%s)", (message,))
            else:
                cursor.execute("INSERT INTO harmful_messages (message) VALUES (%s)", (message,))
            conn.commit()
            conn.close()
            return jsonify({"message": "Message uploaded successfully."})
        else:
            return jsonify({"error": "Error connecting to database."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get normal messages
@app.route('/normal', methods=['GET'])
def get_normal_messages():
    conn, cursor = connect_to_database()
    if conn:
        cursor.execute("SELECT message FROM normal_messages")
        messages = [row[0] for row in cursor.fetchall()]
        conn.close()
        return render_template('normal.html', normal_messages=messages)
        # return jsonify({"normal_messages": messages})
    else:
        return jsonify({"error": "Error connecting to database."}), 500

# Route to get harmful messages
@app.route('/harmful', methods=['GET'])
def get_harmful_messages():
    conn, cursor = connect_to_database()
    if conn:
        cursor.execute("SELECT message FROM harmful_messages")
        messages = [row[0] for row in cursor.fetchall()]
        conn.close()
        return render_template('harmful.html', harmful_messages=messages)
        # return jsonify({"harmful_messages": messages})
    else:
        return jsonify({"error": "Error connecting to database."}), 500

if __name__ == '__main__':
    app.run()