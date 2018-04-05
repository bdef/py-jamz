import filecmp
import os
import subprocess


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
        self._set_name()

    def _set_name(self):
        self.name = ''
        # use ID tag to set name

    @property
    def extinf(self):
        return '#EXTINF:,{}'.format(self.name)    

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