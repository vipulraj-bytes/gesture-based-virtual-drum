"""
Playlist Manager Module
Manages playlist of recorded drum performances
"""

import json
import os
import datetime
import pygame

class PlaylistManager:
    def __init__(self):
        self.playlist_file = "data/playlist.json"
        self.current_track_index = 0
        self.playlist = self.load_playlist()
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
    
    def load_playlist(self):
        """Load playlist from JSON file"""
        if os.path.exists(self.playlist_file):
            try:
                with open(self.playlist_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_playlist(self):
        """Save playlist to JSON file"""
        try:
            with open(self.playlist_file, 'w') as f:
                json.dump(self.playlist, f, indent=2)
        except Exception as e:
            print(f"Error saving playlist: {e}")
    
    def add_track(self, filename, style):
        """Add a new track to playlist"""
        if filename and os.path.exists(filename):
            track = {
                "filename": filename,
                "style": style,
                "date_created": datetime.datetime.now().isoformat(),
                "title": os.path.basename(filename)
            }
            self.playlist.append(track)
            self.save_playlist()
    
    def play_next(self):
        """Play next track in playlist"""
        if not self.playlist:
            # Use audio engine from main system
            print("Playlist is empty")
            return
        
        if self.current_track_index >= len(self.playlist):
            self.current_track_index = 0
        
        track = self.playlist[self.current_track_index]
        self.play_track(track)
        self.current_track_index += 1
    
    def play_track(self, track):
        """Play a specific track"""
        try:
            if os.path.exists(track["filename"]):
                pygame.mixer.music.load(track["filename"])
                pygame.mixer.music.play()
                print(f"Playing: {track['title']} ({track['style']} style)")
            else:
                print(f"File not found: {track['filename']}")
        except Exception as e:
            print(f"Error playing track: {e}")
    
    def delete_current(self):
        """Delete current track from playlist"""
        if self.playlist and 0 <= self.current_track_index < len(self.playlist):
            track = self.playlist[self.current_track_index]
            
            # Remove from playlist
            self.playlist.pop(self.current_track_index)
            
            # Delete file
            try:
                if os.path.exists(track["filename"]):
                    os.remove(track["filename"])
            except Exception as e:
                print(f"Error deleting file: {e}")
            
            # Adjust index
            if self.current_track_index >= len(self.playlist):
                self.current_track_index = 0
            
            self.save_playlist()
            print(f"Deleted: {track['title']}")
    
    def get_playlist_info(self):
        """Get playlist information"""
        return {
            "total_tracks": len(self.playlist),
            "current_index": self.current_track_index,
            "tracks": self.playlist
        }