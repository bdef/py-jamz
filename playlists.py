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
        # print("Found track {}".format(self.absolute_path))


class Playlist:
    def __init__(self, path):
        self.absolute_path = path
        self.fname = os.path.split(path)[-1]
        self._set_tracks()
        self.tmp_path = None
        print("Found playlist {}".format(self.fname))

    def _set_tracks(self):
        self.tracks = []
        with open(self.absolute_path) as f:
            for line in f:
                try:
                    track = Track(line)
                    self.tracks.append(track)
                except NotATrackError:
                    pass

    def cp_tracks(self, dest_path):
        for track in self.tracks:
            cmd = 'cp --parents "{src}" "{dest}"'.format(
                src=track.absolute_path,
                dest=os.path.join(dest_path, track.relative_path))
            print("Copying {}".format(os.path.split(track.relative_path)[-1]))
            # subprocess.check_call(cmd)

    def write_tmp_playlist(self):
        tmp_playlist_path = os.path.join('tmp', self.fname)
        print("Writing temporary playlist to {}".format(tmp_playlist_path))
        with open(tmp_playlist_path, 'w') as f:
            f.write(self.file_header)
            f.write(self.relative_path_playlist())
            f.close()
        self.tmp_playlist_path = tmp_playlist_path
        shutil.copystat(self.absolute_path, self.tmp_playlist_path)

    # def write_playlist(self, dest_dir):
    #     # write the str from relative_path_playlist to dest_dir
    #     if not os.path.isdir(dest_dir):
    #         os.mkdir(dest_dir)
    #     dest_path = os.path.join(dest_dir, self.fname)
    #     print("Writing playlist to {}".format(dest_path))
    #     with open(dest_path, 'w') as f:
    #         f.write(self.file_header)
    #         f.write(self.relative_path_playlist())
    #         f.close()        

    # def cp_playlist_gvfs(self, gvfs_dest):
    #     cmd = 'gvfs-copy "{}" "{}/Playlists"'.format(self.absolute_path, gvfs_dest)
    #     print(cmd)
    #     # gvfs-copy "/home/billy/Music/jamz/Playlists/bak/Girls Girl Girls.m3u" mtp://[usb:001,005]/Samsung%20SD%20card/Music/Playlists
    #     #                                                                       mtp://[usb:001,005]/Samsung%20SD%20card/Music/Playlists
    #     output = subprocess.check_output(cmd, universal_newlines=True)
    #     print(output)

    def cp_playlist(self, dest_dir):
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
        self.write_tmp_playlist()
        print('Copying playlist {} to {}'.format(self.fname, dest_dir))
        shutil.copy(self.tmp_playlist_path, dest_dir)


    @classmethod
    def get_playlists(cls, dir_path):
        print('Checking {} for playlists...'.format(dir_path))
        playlists = []
        for f in os.listdir(dir_path):
            fpath = os.path.join(dir_path, f)
            fname, ext = f.split('.')
            if ext == 'm3u':
                playlists.append(M3UPlaylist(fpath))
            else:
                print("Extension {} not currently supported".format(ext))
        return playlists


class M3UPlaylist(Playlist):
    file_header = '#EXTM3U\n'
    
    def __init__(self, path):
        super(M3UPlaylist, self).__init__(path)
        self.extension = 'm3u'

    def relative_path_playlist(self):
        playlist = ''
        for track in self.tracks:
            # print('.')
            playlist += '{}\n'.format(os.path.join('..', track.relative_path))
        return playlist