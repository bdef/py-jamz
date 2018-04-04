from devices import MTPDevice
from playlists import Playlist
from settings import Settings


print("Starting PY JAMZ!")

# TODO:
# export playlists from Rhythmbox automatically?

if Settings.MTP_DEVICE_NAME:
    device = MTPDevice.get_mtp_device(device_name=Settings.MTP_DEVICE_NAME)
    print("Using device `{}` based on your settings.".format(device.name))
else:
    print('Checking for USB connected devices...')
    devices = MTPDevice.get_mtp_devices()
    prompt = "Please enter the number of the MTP device to sync:\n"
    for i, device in enumerate(devices):
        prompt += "{}.  {}\n".format(i, device)
    device = devices[int(input(prompt))]
    print("You chose {}".format(device))

if not device.is_mounted():
    device.prompt_mount()

if Settings.MTP_DEVICE_MUSIC_DIR:
    device.set_device_music_dir(Settings.MTP_DEVICE_MUSIC_DIR)
    print('Using device music dir `{}` based on your settings'.format(Settings.MTP_DEVICE_MUSIC_DIR))
else:
    device.choose_music_dir()

Playlist.jamz(Settings.LOCAL_PLAYLISTS_DIR, device.jamz_dir, device.playlist_dir)

print("DONEZO FUNZO")
