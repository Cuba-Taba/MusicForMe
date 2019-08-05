import os
import json

import vk_api
from vk_api import audio
import requests
from time import time

# ---------------------старый тест через get запросы-----------------------------------
# token = 'ac3ac9f3ac3ac9f3ac3ac9f302ac6e25e1aac3aac3ac9f3f7aafb88f2179a640b4c6ee4'
# ver = 5.92
# domain = 'neoclassicaru'
# vk = 'https://vk.com/'
# response = requests.get('https://api.vk.com/method/wall.get', params={'access_token':token, 'v':ver, 'domain': domain})
# data = response.json()
# ---------------------старый тест через get запросы-----------------------------------


REQUEST_STATUS_CODE = 200
name_dir = 'music_vk'
# path = r'D:\vk\course\music\\' + name_dir
path = os.path.join("D:\\vk\\course\\music",name_dir)
trackListFile = "tracklist.json"
login = '79282254991'  # Номер телефона
password = 'Vk*1478963'  # Пароль
# my_id = '553384473'  # Ваш id vk
my_id = '191842670'  # Ваш id vk

vk_session = vk_api.VkApi(login=login, password=password)
vk_session.auth()
vk = vk_session.get_api()  # Теперь можно обращаться к методам API как к обычным классам
vk_audio = audio.VkAudio(vk_session)

if not os.path.exists(path):
    os.makedirs(path)

trackListPath = os.path.join(path, trackListFile)

os.chdir(path)
list_dir = os.listdir(path)
# ----------------------------------------------------------


def createTrackList():
    dst_data = {}
    dst_data['tracks'] = []

    with open(trackListPath, 'w+') as outfile:
        json.dump(dst_data, outfile)
# ----------------------------------------------------------


def loadTrackList():
    with open(trackListPath) as json_file:
        src_data = json.load(json_file)
        if src_data.get('tracks'):
            for p in src_data['tracks']:
                print('Title: ' + p['title'])
                print('Path: ' + p['path'])
                print('Status: ' + p['status'])
                print('')

    return src_data
# ----------------------------------------------------------


if list_dir.count(trackListFile) == 0:
    createTrackList()

trackList = loadTrackList()
print(trackList)


def saveTrackList():
    with open(trackListPath, 'w') as outfile:
        json.dump(trackList, outfile)
# ----------------------------------------------------------


def setDescribeTrack(title, path_file, status):
    if not trackList.get('tracks'):
        trackList['tracks'] = []

    trackList['tracks'].append({
        'title': title,
        'path': path_file,
        'status': status
    })
# ----------------------------------------------------------


def updateTrackList(current_pass):
    files = [f for f in os.listdir(current_pass) if os.path.isfile(f)]
    for f in files:
        fileName = f.title()
        setDescribeTrack(fileName, current_pass, 'relevant')

    dirs = [name for name in os.listdir(current_pass) if os.path.isdir(os.path.join(current_pass, name))]
    for d in dirs:
        updateTrackList(os.path.join(current_pass, d))


# ----------------------------------------------------------

updateTrackList(path)

def downloadAllMusic():
    time_start = time()

    count = 2
    for i in vk_audio.get(owner_id=my_id):
        title = i["artist"] + '_' + i["title"] + '.mp3'
        if list_dir.count(title) > 0:
            print(title + ' already exist')
            continue

        try:
            r = requests.get(i["url"])
            if r.status_code == REQUEST_STATUS_CODE:
                with open(title, 'wb') as output_file:
                    print(title + ' download and save to file')
                    output_file.write(r.content)
                    setDescribeTrack(title, path, 'relevant')
                    if count <= 0:
                        break
                    count = count - 1

        except OSError:
            print(i["artist"] + '_' + i["title"])

    print(trackList)

    saveTrackList()

    time_finish = time()
    print("Time seconds:", time_finish - time_start)
# ----------------------------------------------------------


downloadAllMusic()
