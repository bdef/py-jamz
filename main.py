from devices import MTPDevice
from playlists import Playlist


PLAYLISTS_DIR = '/home/billy/Music/jamz/Playlists/bak'

print("Starting PY JAMZ!")

# TODO:
# export playlists from Rhythmbox automatically?

print('Checking for USB connected devices...')
devices = MTPDevice.get_mtp_devices()

prompt = "Please enter the number of the MTP device to sync:\n"

for i, device in enumerate(devices):
    prompt += "{}.  {}\n".format(i, device)

device = devices[int(input(prompt))]
print("You chose {}".format(device))

if not device.is_mounted():
    device.prompt_mount()

device.choose_music_dir()

playlists = Playlist.get_playlists(playlist_dir=PLAYLISTS_DIR)
for pl in playlists:
    pl.cp_tracks(device.jamz_dir)
    pl.cp_playlist(device.playlist_dir)

print("DONEZO FUNZO")
