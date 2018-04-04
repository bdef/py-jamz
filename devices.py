import os
import subprocess
from urllib.parse import unquote, quote

class DeviceNotConnectedError(Exception):
    pass


class MTPDevice:

    def __init__(self, device_str):
        self.bus = device_str[4:7]
        self.device_num = device_str[15:18]
        self.id = device_str[23:31]
        self.name = device_str[33:]
        self._set_mtp_device_root_path()
        # for key in self.__dict__.keys():
            # print('{}:    {}'.format(key, self.__dict__[key]))

    # def _set_gvfs_path(self):
    #     self.gvfs_path = 'mtp://[usb:{},{}]/{}'.format(self.bus, self.device_num, quote(self.device_music_dir))
    #     print(self.gvfs_path)

    def _set_mtp_device_root_path(self):
        self.mtp_device_root_path = None
        mtp_devices_path = '/run/user/1000/gvfs/'
        device_list = os.listdir(mtp_devices_path)
        check_str = '{},{}'.format(self.bus, self.device_num)
        for device in device_list:
            bus_device_num = unquote(device)[14:21]
            if check_str == bus_device_num:
                self.mtp_device_root_path = mtp_devices_path + device
                break
        
    def is_mounted(self):
        if self.dirs():
            return True
        return False

    def prompt_mount(self):
        prompt = "Mount {} as an MTP Device, then press ENTER to continue...".format(self.name)
        input(prompt)
        self._reconnect()
    
    def _reconnect(self):
        # now we need to re-init the object since device_nums have changed
        devices = self.get_mtp_devices()
        for device in devices:
            if device.name == self.name:
                self.bus, self.device_num = device.bus, device.device_num
                self._set_mtp_device_root_path()
                # self._set_gvfs_path()
                break

    def dirs(self):
        if self.mtp_device_root_path is not None:
            return os.listdir(self.mtp_device_root_path)
        return False

    def choose_music_dir(self):
        prompt = "Where shall we put your jamz on your {}?\n".format(self.name)
        for i, dir in enumerate(self.dirs()):
            prompt += "{}. {}/Music\n".format(i, dir)
        user_choice = int(input(prompt))
        self.device_music_dir = os.path.join(self.dirs()[user_choice], 'Music')
        self.jamz_target_dir = os.path.join(self.mtp_device_root_path, self.device_music_dir)
        self._set_mtp_device_root_path()
        # self._set_gvfs_path()

    @property
    def playlist_dir(self):
        return os.path.join(self.jamz_target_dir, 'Playlists')

    def __str__(self):
        return self.name

    @classmethod
    def get_mtp_devices(cls):
        cmd = 'lsusb'
        output = subprocess.check_output(cmd, universal_newlines=True)
        devices = []
        for line in output.split('\n')[:-1]:
            device = MTPDevice(line)
            if device.mtp_device_root_path:
                # it's connected, so add it to the list!
                devices.append(device)
        return devices
