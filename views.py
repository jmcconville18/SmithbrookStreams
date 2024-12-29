from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, MediaRequest
import qbittorrentapi
import time
import requests

views_bp = Blueprint('views', __name__)

# Home Page Route
@views_bp.route('/')
def index():
    # Check if the user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    username = session.get('username')
    role = session.get('role')
    code = session.get('code')

    # Debugging
    print(f"Accessing index page - Username: {username}, Role: {role}, Code: {code}")
    return render_template('index.html', username=username, role=role, code=code)

#pushover notifications
def send_pushover_notification(title, message):
    """Send a Pushover notification using requests"""
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": "agcv2yqx3hbduvwj7jhn8noaba71m3",
                "user": "uu9jwq6k97z6cqudv8izuczokguugo",
                "title": title,
                "message": message,
            },
            timeout=10
        )
        if response.status_code == 200:
            print(f"DEBUG: Pushover notification sent successfully: {response.json()}")
            return True
        else:
            print(f"ERROR: Failed to send Pushover notification. Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Exception while sending Pushover notification: {e}")
        return False

@views_bp.route('/media-requests', methods=['GET', 'POST'])
def media_requests():
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    # Debug session variables
    print(f"DEBUG: Logged in as: {session.get('username')}, Role: {session.get('role')}")

    if request.method == 'POST':
        # Handle new media request submission
        title = request.form.get('title')
        description = request.form.get('description')
        submitted_by = session.get('username')

        # Save to the database
        new_request = MediaRequest(
            title=title,
            description=description,
            submitted_by=submitted_by
        )
        db.session.add(new_request)
        db.session.commit()

        # Send Pushover notification
        notification_title = "New Media Request"
        notification_message = f"Title: {title}\nDescription: {description}\nSubmitted by: {submitted_by}"
        
        if send_pushover_notification(notification_title, notification_message):
            flash("Request submitted successfully and notification sent!", "success")
            print("DEBUG: Pushover notification sent successfully")
        else:
            flash("Request submitted successfully, but notification failed to send.", "warning")
        
        return redirect(url_for('views.media_requests'))

    # Fetch open and completed requests
    open_requests = MediaRequest.query.filter_by(status='Open').all()
    completed_requests = MediaRequest.query.filter_by(status='Completed').all()

    # Update torrent progress and status for open requests
    try:
        qbt_client = qbittorrentapi.Client(
            host='192.168.68.67',
            port=8090,
            username='admin',
            password='P@ssword1'
        )
        qbt_client.auth_log_in()
        torrents = qbt_client.torrents_info()

        for request_obj in open_requests:
            if request_obj.torrent_link:
                torrent_hash = request_obj.torrent_link.split('&btih=')[-1][:40]  # Extracting torrent hash
                matched_torrent = None

                # Match the torrent using hash or title
                for torrent in torrents:
                    if torrent.hash == torrent_hash or request_obj.title.lower() in torrent.name.lower():
                        matched_torrent = torrent
                        break

                # Update the database with torrent progress and other information
                if matched_torrent:
                    updated = False
                    if request_obj.progress != round(matched_torrent.progress * 100, 1):
                        request_obj.progress = round(matched_torrent.progress * 100, 1)
                        updated = True
                    if request_obj.save_path != matched_torrent.save_path:
                        request_obj.save_path = matched_torrent.save_path
                        updated = True
                    if request_obj.status != matched_torrent.state:
                        request_obj.status = matched_torrent.state
                        updated = True

                    if updated:
                        db.session.commit()
                        print(f"DEBUG: Updated request '{request_obj.title}' - Progress: {request_obj.progress}%, Status: {request_obj.status}")

    except qbittorrentapi.LoginFailed as e:
        flash("Failed to connect to qBittorrent. Check your credentials.", "danger")
        print(f"ERROR: {e}")
    except Exception as e:
        flash("An error occurred while fetching torrent progress.", "danger")
        print(f"ERROR: {e}")

    return render_template(
        'requests.html',
        open_requests=open_requests,
        completed_requests=completed_requests,
        role=session.get('role'),
        username=session.get('username')
    )
    
# PGA Scores Page Route
@views_bp.route('/pga')
def pga():
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    username = session.get('username')
    role = session.get('role')

    # Debugging
    print(f"Accessing PGA page - Username: {username}, Role: {role}")
    return render_template('pga.html', username=username, role=role)

@views_bp.route('/weather')
def weather():
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    username = session.get('username')
    role = session.get('role')

    # Debugging
    print(f"Accessing Weather page - Username: {username}, Role: {role}")
    return render_template('weather.html', username=username, role=role)

@views_bp.route('/stocks')
def stocks():
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    username = session.get('username')
    role = session.get('role')

    # Debugging
    print(f"Accessing Stocks page - Username: {username}, Role: {role}")
    return render_template('stocks.html', username=username, role=role)



# Add Torrent Link to Media Request (Admin Only)
# Configuration
QBT_HOST = '192.168.68.67'
QBT_PORT = 8090
QBT_USERNAME = 'jmcconville18'
QBT_PASSWORD = '7!BMiygE469W8K'
MEDIA_FOLDERS = {
    'movies': '/mnt/JoeDrive/Movies',
    'tv': '/mnt/JoeDrive/TV Shows'
}

def get_qbt_client():
    """Create and return an authenticated qBittorrent client"""
    try:
        qbt_client = qbittorrentapi.Client(
            host=QBT_HOST,
            port=QBT_PORT,
            username=QBT_USERNAME,
            password=QBT_PASSWORD,
            VERIFY_WEBUI_CERTIFICATE=False,
            REQUESTS_ARGS={'timeout': 15}
        )
        qbt_client.auth_log_in()
        return qbt_client
    except Exception as e:
        print(f"ERROR: Failed to create qBittorrent client: {e}")
        return None

@views_bp.route('/add_torrent/<int:id>', methods=['POST'])
def add_torrent(id):
    """Handle torrent addition with folder selection"""
    if 'username' not in session or session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('views.media_requests'))

    request_to_update = MediaRequest.query.get_or_404(id)
    torrent_link = request.form.get('torrent_link')
    save_path = request.form.get('save_path')

    if not torrent_link or not save_path:
        flash("Both torrent link and save path are required!", "danger")
        return redirect(url_for('views.media_requests'))

    try:
        qbt_client = get_qbt_client()
        if not qbt_client:
            flash("Failed to connect to qBittorrent!", "danger")
            return redirect(url_for('views.media_requests'))

        # Add the torrent
        qbt_client.torrents_add(
            urls=torrent_link,
            save_path=save_path,
            use_auto_torrent_management=False
        )

        time.sleep(2)  # Wait for torrent to be added

        # Find the added torrent
        torrents = qbt_client.torrents_info()
        for torrent in torrents:
            if torrent.magnet_uri == torrent_link or request_to_update.title.lower() in torrent.name.lower():
                request_to_update.torrent_link = torrent_link
                request_to_update.save_path = save_path
                request_to_update.progress = round(torrent.progress * 100, 1)
                request_to_update.status = torrent.state
                request_to_update.torrent_hash = torrent.hash
                db.session.commit()

                flash(f"Torrent added. Downloading to: {save_path}", "success")
                break
        else:
            flash("Torrent added but unable to find it in client", "warning")

    except Exception as e:
        flash(f"Error adding torrent: {str(e)}", "danger")
        print(f"ERROR: {e}")

    return redirect(url_for('views.media_requests'))

@views_bp.route('/refresh_torrent/<int:id>')
def refresh_torrent(id):
    """AJAX endpoint to refresh torrent status"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    request_obj = MediaRequest.query.get_or_404(id)
    if not request_obj.torrent_hash:
        return jsonify({'error': 'No torrent hash found'}), 404

    try:
        qbt_client = get_qbt_client()
        if not qbt_client:
            return jsonify({'error': 'Failed to connect to qBittorrent'}), 500

        torrent = qbt_client.torrents_info(hash=request_obj.torrent_hash)[0]
        
        # Update database
        request_obj.progress = round(torrent.progress * 100, 1)
        request_obj.status = torrent.state
        db.session.commit()

        return jsonify({
            'progress': request_obj.progress,
            'status': torrent.state,
            'eta': torrent.eta if hasattr(torrent, 'eta') else None,
            'download_speed': torrent.dlspeed if hasattr(torrent, 'dlspeed') else 0
        })

    except Exception as e:
        print(f"ERROR: Failed to refresh torrent status: {e}")
        return jsonify({'error': str(e)}), 500
        
# Delete Media Request (Admin or Owner Only)
@views_bp.route('/delete-request/<int:id>', methods=['POST'])
def delete_request(id):
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('auth.login'))

    # Fetch the request to delete
    request_to_delete = MediaRequest.query.get_or_404(id)
    username = session.get('username')
    role = session.get('role')

    # Check if the user is authorized to delete the request
    if role != 'admin' and request_to_delete.submitted_by != username:
        flash("You are not authorized to delete this request.", "danger")
        return redirect(url_for('views.media_requests'))

    # Delete the request
    db.session.delete(request_to_delete)
    db.session.commit()
    flash("Request deleted successfully.", "success")
    return redirect(url_for('views.media_requests'))

# Update Media Request (Admin Only)
@views_bp.route('/update_request/<int:id>', methods=['POST'])
def update_request(id):
    # Ensure user is logged in and is an admin
    if 'username' not in session or session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('views.media_requests'))

    # Get the request to update
    request_to_update = MediaRequest.query.get_or_404(id)

    # Update status to 'Completed' manually
    request_to_update.status = 'Completed'
    db.session.commit()
    flash("Request marked as completed.", "success")
    return redirect(url_for('views.media_requests'))

# Automatic Completion if Progress is 100%
def auto_complete_requests():
    try:
        # Fetch open requests
        open_requests = MediaRequest.query.filter_by(status='Open').all()

        # Connect to qBittorrent Web UI
        qbt_client = qbittorrentapi.Client(
            host='192.168.68.67',
            port=8090,
            username='admin',  # Update with your username
            password='P@ssword1'  # Update with your password
        )
        qbt_client.auth_log_in()

        torrents = qbt_client.torrents_info()

        for request_obj in open_requests:
            if request_obj.torrent_link:
                # Extract the torrent hash for matching purposes
                torrent_hash = request_obj.torrent_link.split('&btih=')[-1][:40]
                matched_torrent = None

                # Match the torrent using hash or title
                for torrent in torrents:
                    if torrent.hash == torrent_hash or request_obj.title.lower() in torrent.name.lower():
                        matched_torrent = torrent
                        break

                # If progress is 100%, mark as completed
                if matched_torrent and matched_torrent.progress == 1.0:
                    request_obj.status = 'Completed'
                    request_obj.progress = 100.0
                    db.session.commit()
                    print(f"DEBUG: Request '{request_obj.title}' marked as completed automatically.")
                    flash(f"Request '{request_obj.title}' marked as completed automatically.", "success")

    except qbittorrentapi.LoginFailed as e:
        flash("Failed to connect to qBittorrent. Check your credentials.", "danger")
        print(f"ERROR: {e}")

    except Exception as e:
        flash("An error occurred while checking torrent progress.", "danger")
        print(f"ERROR: {e}")

# You can use a scheduler to call `auto_complete_requests` periodically.

