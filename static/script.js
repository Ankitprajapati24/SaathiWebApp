// Request browser notification permission
const requestNotificationPermission = async () => {
    if (!("Notification" in window)) {
        alert("This browser does not support notifications.");
        return;
    }
    if (Notification.permission !== "granted") {
        await Notification.requestPermission();
    }
};

// Show browser notification
const showBrowserNotification = (message) => {
    if (Notification.permission === "granted") {
        new Notification("Medicine Reminder", {
            body: message,
            icon: "/static/images/reminder-icon.png",
        });
    }
};

// Display notifications in-app
const showNotification = (message, type = 'info') => {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerText = message;
    container.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
};

// Load reminders
async function loadReminders() {
    const response = await fetch('/get_reminders');
    const data = await response.json();
    const remindersList = document.getElementById('remindersList');
    remindersList.innerHTML = data.reminders.map(r => `
        <div class="reminder">
            <strong>${r.medicine_name}</strong> on ${r.reminder_date} at ${r.reminder_time} 
            <button onclick="editReminder(${r.id})">Edit</button>
            <button onclick="deleteReminder(${r.id})">Delete</button>
        </div>
    `).join('');
}

// Add a new reminder
document.getElementById('scheduleReminder').addEventListener('click', async () => {
    const medicineName = document.getElementById('medicineName').value;
    const reminderDate = document.getElementById('reminderDate').value;
    const reminderTime = document.getElementById('reminderTime').value;

    if (!medicineName || !reminderDate || !reminderTime) {
        showNotification('All fields are required!', 'error');
        return;
    }

    await fetch('/add_reminder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ medicineName, reminderDate, reminderTime })
    });

    showNotification('Reminder scheduled successfully!', 'success');
    loadReminders();
});

// Edit a reminder
async function editReminder(id) {
    const newName = prompt("Enter new medicine name:");
    const newDate = prompt("Enter new reminder date (YYYY-MM-DD):");
    const newTime = prompt("Enter new reminder time (HH:MM):");

    if (!newName || !newDate || !newTime) {
        showNotification('All fields are required!', 'error');
        return;
    }

    await fetch(`/update_reminder/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ medicineName: newName, reminderDate: newDate, reminderTime: newTime })
    });

    showNotification('Reminder updated successfully!', 'success');
    loadReminders();
}

// Delete a reminder
async function deleteReminder(id) {
    if (!confirm('Are you sure?')) return;

    await fetch(`/delete_reminder/${id}`, {
        method: 'DELETE',
    });

    showNotification('Reminder deleted successfully!', 'success');
    loadReminders();
}

// Poll reminders for notifications
setInterval(async () => {
    const response = await fetch('/check_reminders');
    const data = await response.json();
    data.notifications.forEach(r => showBrowserNotification(`Time to take your medicine: ${r.medicine_name}`));
}, 30000);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    requestNotificationPermission();
    loadReminders();
});
