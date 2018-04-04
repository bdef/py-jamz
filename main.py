from devices import MTPDevice
from playlists import Playlist


PLAYLISTS_DIR = '/home/billy/Music/jamz/Playlists/bak'

print("Starting PY JAMZ!")

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

playlists = Playlist.get_playlists(dir_path=PLAYLISTS_DIR)
for pl in playlists:
    pl.cp_tracks(device.jamz_target_dir)
    pl.cp_playlist_gvfs(device.jamz_gvfs_target_dir)

print("DONEZO FUNZO")
# TODO:
# export playlists from Rhythmbox automatically?

# for each, move pc path to device with cp --parent
# https://stackoverflow.com/a/8722754/1422305
# cp --parents scratch/test.txt /run/user/1000/gvfs/mtp\:host\=%5Busb%3A001%2C007%5D/Samsung\ SD\ card/

# create device versin of playlist w/ relative paths
# finally, move playlists to device Playlist dir

# cp --parents "/storage/jamz/Neko Case/Fox Confessor Brings The Flood/02 Star Witness.mp3" "/run/user/1000/gvfs/mtp:host=%5Busb%3A001%2C010%5D/Samsung SD card/Music/Neko Case/Fox Confessor Brings The Flood"
