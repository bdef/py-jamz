import filecmp
import os
import subprocess

import eyed3
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
        self._set_tag_info()

    def _set_tag_info(self):
        self.artist = None
        self.title = None
        audiofile = eyed3.load(self.absolute_path)
        try:
            self.artist = audiofile.tag.artist
            self.title = audiofile.tag.title
        except AttributeError:
            # the tag info failed!
            pass

    @property
    def extinf(self):
        if self.title is not None:
            return '#EXTINF:,{} - {}'.format(self.artist, self.title)    
        return '#EXTINF:,{}'.format(self.fname)

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
        try:
            subprocess.check_call(cmd, universal_newlines=True, shell=True)
        except Exception as ex:
            print("cmd failed:")
            print(cmd)
            raise ex

    def is_same(self, track_dest_dir):
        track_dest_path = os.path.join(track_dest_dir, self.fname)
        if os.path.isfile(track_dest_path):
            if Settings.QUICK_FILE_CHECK:
                return True
            return filecmp.cmp(self.absolute_path, track_dest_path, shallow=True)
        return False