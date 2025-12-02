"""
Seed script for Toonify database
Populates database with test data
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.config import SessionLocal, init_db, drop_db, test_connection
from database.models import User, Playlist, Song, PlaylistSong
from datetime import datetime, date


def seed_database():
    """
    Seed the database with test data
    """
    print("Starting database seed...\n")

    # Test connection
    if not test_connection():
        print("✗ Cannot proceed without database connection")
        return False

    # Drop and recreate tables
    print("\n--- Resetting Database ---")
    drop_db()
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Seed Users
        print("\n--- Seeding Users ---")
        users = [
            User(
                spotify_id='spotify_user_001',
                email='john.doe@example.com',
                display_name='John Doe',
                profile_image='https://i.pravatar.cc/150?img=1',
                country='US',
                spotify_uri='spotify:user:johndoe',
                spotify_access_token='mock_access_token_001',
                spotify_refresh_token='mock_refresh_token_001'
            ),
            User(
                spotify_id='spotify_user_002',
                email='jane.smith@example.com',
                display_name='Jane Smith',
                profile_image='https://i.pravatar.cc/150?img=2',
                country='GB',
                spotify_uri='spotify:user:janesmith',
                spotify_access_token='mock_access_token_002',
                spotify_refresh_token='mock_refresh_token_002'
            ),
            User(
                spotify_id='spotify_user_003',
                email='mike.wilson@example.com',
                display_name='Mike Wilson',
                profile_image='https://i.pravatar.cc/150?img=3',
                country='CA',
                spotify_uri='spotify:user:mikewilson',
                spotify_access_token='mock_access_token_003',
                spotify_refresh_token='mock_refresh_token_003'
            ),
            User(
                spotify_id='spotify_user_004',
                email='sarah.johnson@example.com',
                display_name='Sarah Johnson',
                profile_image='https://i.pravatar.cc/150?img=4',
                country='AU',
                spotify_uri='spotify:user:sarahjohnson',
                spotify_access_token='mock_access_token_004',
                spotify_refresh_token='mock_refresh_token_004'
            ),
            User(
                spotify_id='spotify_user_005',
                email='david.brown@example.com',
                display_name='David Brown',
                profile_image='https://i.pravatar.cc/150?img=5',
                country='US',
                spotify_uri='spotify:user:davidbrown',
                spotify_access_token='mock_access_token_005',
                spotify_refresh_token='mock_refresh_token_005'
            )
        ]
        db.add_all(users)
        db.commit()
        print(f"✓ Created {len(users)} users")

        # Seed Songs
        print("\n--- Seeding Songs ---")
        songs = [
            Song(title='Blinding Lights', artist='The Weeknd', album='After Hours', duration=200, genre='Pop',
                 audio_url='spotify:track:0VjIjW4GlUZAMYd2vXMi3b', spotify_track_id='spotify_track_001',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36',
                 release_date=date(2020, 3, 20), preview_url='https://p.scdn.co/mp3-preview/preview001'),

            Song(title='Shape of You', artist='Ed Sheeran', album='÷ (Divide)', duration=233, genre='Pop',
                 audio_url='spotify:track:7qiZfU4dY1lWllzX7mPBI', spotify_track_id='spotify_track_002',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273ba5db46f4b838ef6027e6f96',
                 release_date=date(2017, 1, 6), preview_url='https://p.scdn.co/mp3-preview/preview002'),

            Song(title='Levitating', artist='Dua Lipa', album='Future Nostalgia', duration=203, genre='Pop',
                 audio_url='spotify:track:39LLxExYz6ewLAcYrzQQyP', spotify_track_id='spotify_track_003',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b2739b8a3e2ed91c7b99b2cd7d75',
                 release_date=date(2020, 10, 1), preview_url='https://p.scdn.co/mp3-preview/preview003'),

            Song(title='Bad Guy', artist='Billie Eilish', album='When We All Fall Asleep, Where Do We Go?',
                 duration=194, genre='Alternative', audio_url='spotify:track:2Fxmhks0bxGSBdJ92vM42m',
                 spotify_track_id='spotify_track_004',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b27350a3147b4edd7701a876c6ce',
                 release_date=date(2019, 3, 29), preview_url='https://p.scdn.co/mp3-preview/preview004'),

            Song(title='Bohemian Rhapsody', artist='Queen', album='A Night at the Opera', duration=354, genre='Rock',
                 audio_url='spotify:track:3z8h0TU7ReDPLIbEnYhWZb', spotify_track_id='spotify_track_005',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273ce4f1737bc8a646c8c4bd25a',
                 release_date=date(1975, 10, 31), preview_url='https://p.scdn.co/mp3-preview/preview005'),

            Song(title='Smells Like Teen Spirit', artist='Nirvana', album='Nevermind', duration=301, genre='Rock',
                 audio_url='spotify:track:4CeeEOM32jQcH3eN9Q2dGj', spotify_track_id='spotify_track_006',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273e175a19e530c898d167d39bf',
                 release_date=date(1991, 9, 10), preview_url='https://p.scdn.co/mp3-preview/preview006'),

            Song(title='Lose Yourself', artist='Eminem', album='8 Mile Soundtrack', duration=326, genre='Hip-Hop',
                 audio_url='spotify:track:1v7L65Lzy0j0vdpRjJewt1', spotify_track_id='spotify_track_007',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b2732f44aec83b20e40f3baef73c',
                 release_date=date(2002, 10, 28), preview_url='https://p.scdn.co/mp3-preview/preview007'),

            Song(title='Rolling in the Deep', artist='Adele', album='21', duration=228, genre='Soul',
                 audio_url='spotify:track:4OSBTYCNNnJUWcEp5saPdP', spotify_track_id='spotify_track_008',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273ff5429125128b43572dbdccd',
                 release_date=date(2010, 11, 29), preview_url='https://p.scdn.co/mp3-preview/preview008'),

            Song(title='Hotel California', artist='Eagles', album='Hotel California', duration=391, genre='Rock',
                 audio_url='spotify:track:40riOy7x9W7GXjyGp4pjAv', spotify_track_id='spotify_track_009',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273c8a11e48c91a982d086afc69',
                 release_date=date(1976, 12, 8), preview_url='https://p.scdn.co/mp3-preview/preview009'),

            Song(title='Uptown Funk', artist='Mark Ronson ft. Bruno Mars', album='Uptown Special', duration=269,
                 genre='Funk', audio_url='spotify:track:32OlwWuMpZ6b0aN2RZOeMS', spotify_track_id='spotify_track_010',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b27371c5c4cea0bbe8de33b0d8ab',
                 release_date=date(2014, 11, 10), preview_url='https://p.scdn.co/mp3-preview/preview010'),

            Song(title='Thriller', artist='Michael Jackson', album='Thriller', duration=357, genre='Pop',
                 audio_url='spotify:track:2LlQb7Uoj1kKyGhlkBf9aC', spotify_track_id='spotify_track_011',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b2732b62e8947172a42f1fe84489',
                 release_date=date(1982, 11, 30), preview_url='https://p.scdn.co/mp3-preview/preview011'),

            Song(title='Wonderwall', artist='Oasis', album="(What's the Story) Morning Glory?", duration=258,
                 genre='Rock', audio_url='spotify:track:5qqabIl2vWzo9ApSC317sa', spotify_track_id='spotify_track_012',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273b86d16749a5d1f86800e9a5a',
                 release_date=date(1995, 10, 2), preview_url='https://p.scdn.co/mp3-preview/preview012'),

            Song(title='Sweet Child O Mine', artist="Guns N' Roses", album='Appetite for Destruction', duration=356,
                 genre='Rock', audio_url='spotify:track:7o2CTH4ctstm8TNelqjb51', spotify_track_id='spotify_track_013',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273ac2853f7c42fa8f2bd00b87d',
                 release_date=date(1987, 7, 21), preview_url='https://p.scdn.co/mp3-preview/preview013'),

            Song(title='Billie Jean', artist='Michael Jackson', album='Thriller', duration=294, genre='Pop',
                 audio_url='spotify:track:5ChkMS8OtdzJeqyybCc9R5', spotify_track_id='spotify_track_014',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b2732b62e8947172a42f1fe84489',
                 release_date=date(1982, 11, 30), preview_url='https://p.scdn.co/mp3-preview/preview014'),

            Song(title='Stairway to Heaven', artist='Led Zeppelin', album='Led Zeppelin IV', duration=482,
                 genre='Rock', audio_url='spotify:track:5CQ30WqJwcep0pYcV4AMNc', spotify_track_id='spotify_track_015',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b2732f20d55c6e0d7c0f1a06b7a1',
                 release_date=date(1971, 11, 8), preview_url='https://p.scdn.co/mp3-preview/preview015'),

            Song(title='Someone Like You', artist='Adele', album='21', duration=285, genre='Soul',
                 audio_url='spotify:track:1zwMYTA5nlNjZxYrvBB2pV', spotify_track_id='spotify_track_016',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273ff5429125128b43572dbdccd',
                 release_date=date(2011, 1, 24), preview_url='https://p.scdn.co/mp3-preview/preview016'),

            Song(title='Hey Jude', artist='The Beatles', album='Hey Jude', duration=431, genre='Rock',
                 audio_url='spotify:track:0aym2LBJBk9DAYuHHutrIl', spotify_track_id='spotify_track_017',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273582d56ce20fe0146ffa0e5cf',
                 release_date=date(1968, 8, 26), preview_url='https://p.scdn.co/mp3-preview/preview017'),

            Song(title='One Dance', artist='Drake ft. Wizkid & Kyla', album='Views', duration=173, genre='Hip-Hop',
                 audio_url='spotify:track:1xznGGDReH1oQq0xzbwXa3', spotify_track_id='spotify_track_018',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b2739416ed64daf84936d89e671c',
                 release_date=date(2016, 4, 5), preview_url='https://p.scdn.co/mp3-preview/preview018'),

            Song(title='Radioactive', artist='Imagine Dragons', album='Night Visions', duration=187,
                 genre='Alternative', audio_url='spotify:track:2R0OlgJRhaSCFxYYiTbJ3',
                 spotify_track_id='spotify_track_019',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273b83b5c1707162cbb19c39b0a',
                 release_date=date(2012, 9, 4), preview_url='https://p.scdn.co/mp3-preview/preview019'),

            Song(title='Take On Me', artist='a-ha', album='Hunting High and Low', duration=225, genre='Pop',
                 audio_url='spotify:track:2WfaOiMkCvy7F5fcp2zZ8L', spotify_track_id='spotify_track_020',
                 thumbnail_url='https://i.scdn.co/image/ab67616d0000b273e8dd4db47e7177c63b0b7d53',
                 release_date=date(1984, 10, 19), preview_url='https://p.scdn.co/mp3-preview/preview020'),
        ]
        db.add_all(songs)
        db.commit()
        print(f"✓ Created {len(songs)} songs")

        # Seed Playlists
        print("\n--- Seeding Playlists ---")
        playlists = [
            Playlist(name='My Workout Mix',
                     description='High energy tracks to keep me motivated during workouts',
                     is_public=True, cover_image='https://picsum.photos/seed/workout/400/400',
                     user_id=users[0].id),
            Playlist(name='Chill Vibes', description='Relaxing songs for a lazy Sunday afternoon',
                     is_public=True, cover_image='https://picsum.photos/seed/chill/400/400', user_id=users[0].id),
            Playlist(name='Rock Classics', description='The best rock songs of all time',
                     is_public=True, cover_image='https://picsum.photos/seed/rock/400/400', user_id=users[1].id),
            Playlist(name='Road Trip Anthems', description='Perfect songs for long drives',
                     is_public=True, cover_image='https://picsum.photos/seed/roadtrip/400/400',
                     user_id=users[1].id),
            Playlist(name='Study Focus', description='Instrumental and calm tracks for concentration',
                     is_public=False, cover_image='https://picsum.photos/seed/study/400/400', user_id=users[2].id),
            Playlist(name='90s Nostalgia', description='Taking it back to the 90s',
                     is_public=True, cover_image='https://picsum.photos/seed/90s/400/400', user_id=users[2].id),
            Playlist(name='Party Hits', description='Get the party started with these bangers',
                     is_public=True, cover_image='https://picsum.photos/seed/party/400/400', user_id=users[3].id),
            Playlist(name='Late Night Feels', description='Moody tracks for late night vibes',
                     is_public=False, cover_image='https://picsum.photos/seed/latenight/400/400',
                     user_id=users[3].id),
            Playlist(name='Summer Hits 2024', description='The hottest tracks of the summer',
                     is_public=True, cover_image='https://picsum.photos/seed/summer/400/400', user_id=users[4].id),
            Playlist(name='Throwback Jams', description='Classic hits from the past decades',
                     is_public=True, cover_image='https://picsum.photos/seed/throwback/400/400',
                     user_id=users[4].id),
        ]
        db.add_all(playlists)
        db.commit()
        print(f"✓ Created {len(playlists)} playlists")

        # Seed Playlist-Song relationships
        print("\n--- Creating Playlist-Song Relationships ---")
        playlist_songs = [
            # Workout Mix (playlist 0)
            PlaylistSong(playlist_id=playlists[0].id, song_id=songs[0].id, order=0),
            PlaylistSong(playlist_id=playlists[0].id, song_id=songs[2].id, order=1),
            PlaylistSong(playlist_id=playlists[0].id, song_id=songs[9].id, order=2),
            PlaylistSong(playlist_id=playlists[0].id, song_id=songs[6].id, order=3),

            # Chill Vibes (playlist 1)
            PlaylistSong(playlist_id=playlists[1].id, song_id=songs[1].id, order=0),
            PlaylistSong(playlist_id=playlists[1].id, song_id=songs[15].id, order=1),
            PlaylistSong(playlist_id=playlists[1].id, song_id=songs[7].id, order=2),

            # Rock Classics (playlist 2)
            PlaylistSong(playlist_id=playlists[2].id, song_id=songs[4].id, order=0),
            PlaylistSong(playlist_id=playlists[2].id, song_id=songs[5].id, order=1),
            PlaylistSong(playlist_id=playlists[2].id, song_id=songs[8].id, order=2),
            PlaylistSong(playlist_id=playlists[2].id, song_id=songs[12].id, order=3),
            PlaylistSong(playlist_id=playlists[2].id, song_id=songs[14].id, order=4),

            # Road Trip Anthems (playlist 3)
            PlaylistSong(playlist_id=playlists[3].id, song_id=songs[8].id, order=0),
            PlaylistSong(playlist_id=playlists[3].id, song_id=songs[16].id, order=1),
            PlaylistSong(playlist_id=playlists[3].id, song_id=songs[9].id, order=2),
            PlaylistSong(playlist_id=playlists[3].id, song_id=songs[19].id, order=3),

            # Study Focus (playlist 4)
            PlaylistSong(playlist_id=playlists[4].id, song_id=songs[1].id, order=0),
            PlaylistSong(playlist_id=playlists[4].id, song_id=songs[15].id, order=1),

            # 90s Nostalgia (playlist 5)
            PlaylistSong(playlist_id=playlists[5].id, song_id=songs[5].id, order=0),
            PlaylistSong(playlist_id=playlists[5].id, song_id=songs[11].id, order=1),
            PlaylistSong(playlist_id=playlists[5].id, song_id=songs[12].id, order=2),

            # Party Hits (playlist 6)
            PlaylistSong(playlist_id=playlists[6].id, song_id=songs[9].id, order=0),
            PlaylistSong(playlist_id=playlists[6].id, song_id=songs[10].id, order=1),
            PlaylistSong(playlist_id=playlists[6].id, song_id=songs[2].id, order=2),
            PlaylistSong(playlist_id=playlists[6].id, song_id=songs[17].id, order=3),

            # Late Night Feels (playlist 7)
            PlaylistSong(playlist_id=playlists[7].id, song_id=songs[3].id, order=0),
            PlaylistSong(playlist_id=playlists[7].id, song_id=songs[7].id, order=1),
            PlaylistSong(playlist_id=playlists[7].id, song_id=songs[15].id, order=2),

            # Summer Hits 2024 (playlist 8)
            PlaylistSong(playlist_id=playlists[8].id, song_id=songs[0].id, order=0),
            PlaylistSong(playlist_id=playlists[8].id, song_id=songs[2].id, order=1),
            PlaylistSong(playlist_id=playlists[8].id, song_id=songs[17].id, order=2),

            # Throwback Jams (playlist 9)
            PlaylistSong(playlist_id=playlists[9].id, song_id=songs[10].id, order=0),
            PlaylistSong(playlist_id=playlists[9].id, song_id=songs[13].id, order=1),
            PlaylistSong(playlist_id=playlists[9].id, song_id=songs[16].id, order=2),
            PlaylistSong(playlist_id=playlists[9].id, song_id=songs[19].id, order=3),
        ]
        db.add_all(playlist_songs)
        db.commit()
        print(f"✓ Created {len(playlist_songs)} playlist-song relationships")

        print("\n=== Seed Summary ===")
        print(f"Users: {len(users)}")
        print(f"Songs: {len(songs)}")
        print(f"Playlists: {len(playlists)}")
        print(f"Playlist-Song Relationships: {len(playlist_songs)}")
        print("\n✓ Database seeded successfully!\n")

        return True

    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        db.rollback()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
