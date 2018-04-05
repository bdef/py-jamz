import filecmp
import os
import shutil
import subprocess
from settings import Settings


class NotATrackError(Exception):
    pass


class Track:
    def __init__(self, absolute_path):
        if absolute_path.startswith('#'):
            raise NotATrackError('This is a comment, not a track!')
        absolute_path = absolute_path.rstrip()
        self.absolute_path = absolute_path
        # we have to cast to upper case because Fat32 is case-insensitive, while Linux isn't,
        # and the SD card in my Android phone is Fat32.
        relative_path = self.absolute_path.split('/jamz/')[-1]
        relative_path, self.fname = os.path.split(relative_path)
        self.relative_path = os.path.join(relative_path.upper(), self.fname)

    @property
    def relative_path_dir(self):
        return os.path.split(self.relative_path)[0]

    def cp_track(self, dest_path):
        abs_track_dest_dir = os.path.join(dest_path, self.relative_path_dir)
        if self.is_same(abs_track_dest_dir):
            print("No changes to {}. Skipping...".format(self.fname))
            return
        if not os.path.isdir(abs_track_dest_dir):
            os.makedirs(abs_track_dest_dir, exist_ok=True)
        cmd = 'cp "{src}" "{dest}"'.format(
            src=self.absolute_path,
            dest=abs_track_dest_dir)
        print("Copying {}".format(self.fname))
        subprocess.check_call(cmd, universal_newlines=True, shell=True)

    def is_same(self, track_dest_dir):
        track_dest_path = os.path.join(track_dest_dir, self.fname)
        if os.path.isfile(track_dest_path):
            return filecmp.cmp(self.absolute_path, track_dest_path, shallow=True)
        return False


class Playlist:
    def __init__(self, path):
        self.src_abs_path = path
        self.src_abs_path_dir, self.fname = os.path.split(path)
        self._set_tracks()
        self.tmp_path = None
        print("Found playlist {}".format(self.fname))

    def _set_tracks(self):
        self.tracks = []
        with open(self.src_abs_path) as f:
            for line in f:
                try:
                    track = Track(line)
                    self.tracks.append(track)
                except NotATrackError:
                    pass

    @property
    def num_tracks(self):
        return len(self.tracks)

    def cp_tracks(self, dest_path):
        print('Copying tracks...')
        remaining = self.num_tracks
        for track in self.tracks:
            print("{} tracks left...".format(remaining))
            track.cp_track(dest_path)
            remaining -= 1

    def write_tmp_playlist(self):
        tmp_playlist_dir = os.path.join(Settings.LOCAL_PLAYLISTS_DIR, 'tmp')
        if not os.path.isdir(tmp_playlist_dir):
            os.makedirs(tmp_playlist_dir)
        tmp_playlist_path = os.path.join(tmp_playlist_dir, self.fname)
        print("Converting playlist {}...".format(tmp_playlist_path))
        with open(tmp_playlist_path, 'w') as f:
            f.write(self.file_header)
            f.write(self.relative_path_playlist())
            f.close()
        self.tmp_playlist_path = tmp_playlist_path
        shutil.copystat(self.src_abs_path, self.tmp_playlist_path)

    def cp_playlist(self, gvfs_dest):
        self.write_tmp_playlist()
        cmd = 'gvfs-copy "{}" "{}"'.format(self.tmp_playlist_path, gvfs_dest)
        print("Copying converted playlist to {}".format(gvfs_dest))
        subprocess.check_call(cmd, universal_newlines=True, shell=True)

    @classmethod
    def get_playlists(cls, playlist_dir):
        print('Checking {} for playlists...'.format(playlist_dir))
        playlists = []
        for f in os.listdir(playlist_dir):
            try:
                fpath = os.path.join(playlist_dir, f)
                fname, ext = f.split('.')
                if ext == 'm3u':
                    playlists.append(M3UPlaylist(fpath))
                else:
                    print("Extension {} not currently supported".format(ext))
            except ValueError as e:
                # if .split() failed, it's because the path split doens't have a . in
                # it, so it's probably a directory. so just skip it.
                pass
        return playlists

    @classmethod
    def jamz(cls, local_playlists_dir, device_jamz_dir, device_playlist_dir):
        playlists = cls.get_playlists(playlist_dir=local_playlists_dir)
        for pl in playlists:
            print("Found playlist {} with {} songs.".format(pl.src_abs_path, pl.num_tracks))
            pl.cp_tracks(device_jamz_dir)
            pl.cp_playlist(device_playlist_dir)
            print('Playlist {} sucessfully imported!\n'.format(pl.fname))


class M3UPlaylist(Playlist):
    file_header = '#EXTM3U\n'
    
    def __init__(self, playlist_dir):
        super(M3UPlaylist, self).__init__(playlist_dir)
        self.extension = 'm3u'

    def relative_path_playlist(self):
        playlist = ''
        for track in self.tracks:
            # print('.')
            playlist += '{}\n'.format(os.path.join('..', track.relative_path))
        return playlist