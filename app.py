from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
from pytz import timezone

app = Flask(__name__)
DATABASE = 'medicine_reminders.db'

# Initialize SQLite3 Database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name TEXT NOT NULL,
            reminder_date TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            notified BOOLEAN DEFAULT 0
        )''')

# Add a new reminder
@app.route('/add_reminder', methods=['POST'])
def add_reminder():
    try:
        data = request.json
        medicine_name = data['medicineName']
        reminder_date = data['reminderDate']
        reminder_time = data['reminderTime']
        with sqlite3.connect(DATABASE) as conn:
            conn.execute(
                "INSERT INTO reminders (medicine_name, reminder_date, reminder_time) VALUES (?, ?, ?)",
                (medicine_name, reminder_date, reminder_time)
            )
        return jsonify({'status': 'success', 'message': 'Reminder added successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Get all reminders
@app.route('/get_reminders', methods=['GET'])
def get_reminders():
    with sqlite3.connect(DATABASE) as conn:
        reminders = conn.execute(
            "SELECT id, medicine_name, reminder_date, reminder_time, notified FROM reminders"
        ).fetchall()
        formatted_reminders = [
            {'id': r[0], 'medicine_name': r[1], 'reminder_date': r[2], 'reminder_time': r[3], 'notified': r[4]} for r in reminders
        ]
    return jsonify({'status': 'success', 'reminders': formatted_reminders})

# Update a reminder
@app.route('/update_reminder/<int:id>', methods=['PUT'])
def update_reminder(id):
    try:
        data = request.json
        medicine_name = data['medicineName']
        reminder_date = data['reminderDate']
        reminder_time = data['reminderTime']
        with sqlite3.connect(DATABASE) as conn:
            conn.execute(
                "UPDATE reminders SET medicine_name = ?, reminder_date = ?, reminder_time = ? WHERE id = ?",
                (medicine_name, reminder_date, reminder_time, id)
            )
        return jsonify({'status': 'success', 'message': 'Reminder updated successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Delete a reminder
@app.route('/delete_reminder/<int:id>', methods=['DELETE'])
def delete_reminder(id):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute("DELETE FROM reminders WHERE id = ?", (id,))
        return jsonify({'status': 'success', 'message': 'Reminder deleted successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Check and notify reminders
@app.route('/check_reminders', methods=['GET'])
def check_reminders():
    try:
        tz = timezone('Your/Timezone')  # Replace with your timezone
        now = datetime.now(tz)
        now_date = now.strftime("%Y-%m-%d")
        now_time = now.strftime("%H:%M")

        with sqlite3.connect(DATABASE) as conn:
            reminders = conn.execute(
                "SELECT id, medicine_name FROM reminders WHERE reminder_date = ? AND reminder_time = ? AND notified = 0",
                (now_date, now_time)
            ).fetchall()

            # Mark reminders as notified
            for reminder in reminders:
                conn.execute(
                    "UPDATE reminders SET notified = 1 WHERE id = ?",
                    (reminder[0],)
                )

        return jsonify({'status': 'success', 'notifications': [{'id': r[0], 'medicine_name': r[1]} for r in reminders]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Render the main page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
