from apscheduler.schedulers.background import BackgroundScheduler
from qbittorrentapi import Client
from models import db, MediaRequest
import logging

# Function to update torrent progress
def update_torrent_progress():
    try:
        qbt_client = Client(
            host='192.168.68.67',
            port=8090,
            username='admin',
            password='P@ssword1'
        )
        qbt_client.auth_log_in()

        torrents = qbt_client.torrents_info()
        for torrent in torrents:
            # Match the torrent in the database
            request = MediaRequest.query.filter_by(torrent_link=torrent.magnet_uri).first()
            if request:
                request.progress = torrent.progress * 100
                request.save_path = torrent.save_path
                db.session.commit()
                logging.info(f"Updated progress for torrent '{request.title}' to {request.progress}%")
                
    except Exception as e:
        logging.error(f"Error updating torrent progress: {e}")

# Function to start the scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_torrent_progress, 'interval', seconds=10)
    scheduler.start()

