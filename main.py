from devices import MTPDevice
from playlists import Playlist
from settings import Settings


print("Starting PY JAMZ!")

try:
    device = MTPDevice.get_mtp_device(device_name=Settings.MTP_DEVICE_NAME)
    print("Using device `{}` based on your settings.".format(device.name))
except Exception as e:
    print('Checking for USB connected devices...')
    devices = MTPDevice.get_mtp_devices()

    while len(devices) == 0:
        prompt = "Please connect a USB device and hit ENTER...\n"
        input(prompt)
        devices = MTPDevice.get_mtp_devices()

    prompt = "Please enter the number of the MTP device to sync:\n"
    for i, device in enumerate(devices):
        prompt += "{}.  {}\n".format(i, device)
    device = devices[int(input(prompt))]
    print("You chose {}".format(device))
 
try:
    device.is_mounted()
except FileNotFoundError:
    device.prompt_mount()

prompt = "Please enter the number of the MTP device root path:\n"
mtp_root_paths = device.list_mtp_device_root_paths()
for i, path in enumerate(mtp_root_paths):
    prompt += "{}.  {}\n".format(i, path)
mtp_root_path = mtp_root_paths[int(input(prompt))]
print("You chose {}".format(mtp_root_path))
device._set_mtp_device_root_path(mtp_root_path)

if Settings.MTP_DEVICE_MUSIC_DIR:
    device.set_device_music_dir(Settings.MTP_DEVICE_MUSIC_DIR)
    print('Using device music dir `{}` based on your settings'.format(Settings.MTP_DEVICE_MUSIC_DIR))
else:
    device.choose_music_dir()

prompt = "Export playlists from Rhthymbox? y/n\n"
export = input(prompt)
export = True if 'y' in export else False


Playlist.jamz(
    Settings.LOCAL_PLAYLISTS_DIR,
    device.jamz_dir,
    device.playlist_dir,
    export_rb=export)

print("DONEZO FUNZO")
