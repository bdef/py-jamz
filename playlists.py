import os
import shutil
import subprocess


class NotATrackError(Exception):
    pass


class Track:
    def __init__(self, absolute_path):
        if absolute_path.startswith('#'):
            raise NotATrackError('This is a comment, not a track!')
        absolute_path = absolute_path.rstrip()
        self.absolute_path = absolute_path
        self.relative_path = self.absolute_path.split('/jamz/')[-1]
        self.fname = os.path.split(self.relative_path)[1]

    @property
    def relative_path_dir(self):
        return os.path.split(self.relative_path)[0]

    def cp_track(self, dest_path):
        abs_track_dest_dir = os.path.join(dest_path, self.relative_path_dir)
        if not os.path.isdir(abs_track_dest_dir):
            os.makedirs(abs_track_dest_dir)
        cmd = 'cp "{src}" "{dest}"'.format(
            src=self.absolute_path,
            dest=abs_track_dest_dir)
        print("Copying {}".format(self.fname))
        subprocess.check_call(cmd, universal_newlines=True, shell=True)


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

    def cp_tracks(self, dest_path):
        for track in self.tracks:
            track.cp_track(dest_path)

    def write_tmp_playlist(self):
        tmp_playlist_path = os.path.join('tmp', self.fname)
        print("Writing temporary playlist to {}".format(tmp_playlist_path))
        with open(tmp_playlist_path, 'w') as f:
            f.write(self.file_header)
            f.write(self.relative_path_playlist())
            f.close()
        self.tmp_playlist_path = tmp_playlist_path
        shutil.copystat(self.src_abs_path, self.tmp_playlist_path)

    def cp_playlist(self, gvfs_dest):
        self.write_tmp_playlist()
        cmd = 'gvfs-copy "{}" "{}"'.format(self.tmp_playlist_path, gvfs_dest)
        print("Copying playlist {}".format(self.fname))
        subprocess.check_call(cmd, universal_newlines=True, shell=True)

    @classmethod
    def get_playlists(cls, playlist_dir):
        print('Checking {} for playlists...'.format(playlist_dir))
        playlists = []
        for f in os.listdir(playlist_dir):
            fpath = os.path.join(playlist_dir, f)
            fname, ext = f.split('.')
            if ext == 'm3u':
                playlists.append(M3UPlaylist(fpath))
            else:
                print("Extension {} not currently supported".format(ext))
        return playlists


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