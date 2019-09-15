import errno
import os
import json

import vk_api
from pip._vendor.distlib._backport import shutil
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
# root_path = r'D:\vk\course\music\\' + name_dir
rootPath = os.path.join("D:\\vk\\course\\music", name_dir)
trackListFile = "tracklist.json"
login = '79282254991'  # Номер телефона
password = 'Vk*1478963'  # Пароль
# my_id = '553384473'  # Ваш id vk
my_id = '191842670'  # Ваш id vk

vk_session = vk_api.VkApi(login=login, password=password)
vk_session.auth()
vk = vk_session.get_api()  # Теперь можно обращаться к методам API как к обычным классам
vk_audio = audio.VkAudio(vk_session)

if not os.path.exists(rootPath):
    os.makedirs(rootPath)

trackListPath = os.path.join(rootPath, trackListFile)

os.chdir(rootPath)
list_dir = os.listdir(rootPath)
# ----------------------------------------------------------


def set_describe_track(track_list, title, path_file, status):
    if track_list.get(title):
        track_list[title].append({'path': path_file, 'status': status})
    else:
        track_list[title] = []
        track_list[title].append({'path': path_file, 'status': status})

    return track_list
# ----------------------------------------------------------


def gen_dict_extract(key, var):
    if hasattr(var, 'iteritems'):
        for k, v in var.iteritems():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result
# ----------------------------------------------------------


def check_file_in_track_list(file_name):
    global trackList
    if trackList.get(file_name):
        descriptions = trackList[file_name]
        for description in descriptions:
            if description.get('path'):
                print(description['path'])
                return description['path']
# ----------------------------------------------------------


def copy_file_to_dir(currentPath, fileName, dstPath):
    try:
        print("Copy file", fileName, "to", dstPath)
        shutil.move(os.path.join(currentPath, fileName), os.path.join(dstPath, fileName))
    except IOError as e:
        # ENOENT(2): file does not exist, raised also on missing dest parent dir
        if e.errno != errno.ENOENT:
            raise
        # try creating parent directories
        print("Directory", dstPath, "not found!")
        print("Create dir", dstPath)
        os.makedirs(dstPath, exist_ok=True)
        print("Copy file", fileName, "to", dstPath)
        shutil.move(os.path.join(currentPath, fileName), os.path.join(dstPath, fileName))

# ----------------------------------------------------------


class FileManager:
    trackList = {}
    userTrackMap = {}
    workingDir = ''
    trackListPath = ''

    @staticmethod
    def create_track_list_file():
        dst_data = {}
        with open(trackListPath, 'w+') as outfile:
            json.dump(dst_data, outfile)
        # ----------------------------------------------------------

    def get_track_list(self, current_path):
        files = [f for f in os.listdir(current_path) if os.path.isfile(f)]
        for f in files:
            fileName = f.title()

            if (fileName == 'tracklist.json'):
                continue

            #pathFileInTrackList = checkFileInTrackList(fileName)
            #if (pathFileInTrackList == current_path):
            #    continue

            #if (pathFileInTrackList is None):
            #    setDescribeTrack(fileName, current_path, 'relevant')
            #    continue

            #copyFileToDir(current_path, fileName, pathFileInTrackList)

            global trackList

            if fileName in self.trackList.keys():
                path_list = self.trackList.get(fileName)
                path_list.append(current_path)
                self.trackList[fileName] = path_list
                print(self.trackList)
            else:
                path_list = [current_path]
                self.trackList[fileName] = path_list

        dirs = [name for name in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, name))]
        for d in dirs:
            self.get_track_list(os.path.join(current_path, d))

    def read_users_track_map(self, track_list_path):
        if list_dir.count(trackListFile) == 0:
            self.create_track_list_file()

        global userTrackMap

        with open(track_list_path) as json_file:
            data = json.load(json_file)
            for p in data:
                print('Title: ' + p['title'])
                print('Path: ' + p['path'])
                #print('Status: ' + p['status'])
                print('')

                title = p['title']
                file_path = p['path']

                if title in self.userTrackMap.keys():
                    path_list = self.userTrackMap.get(title)
                    path_list.append(file_path)
                    self.userTrackMap[title] = path_list
                    print(self.userTrackMap)
                else:
                    path_list = [file_path]
                    self.userTrackMap[title] = path_list
    # ----------------------------------------------------------

    def update_users_track_map(self):

        global trackList
        global userTrackMap
        for track in self.trackList:
            if track in self.userTrackMap.keys():
                path_list = self.userTrackMap[track]
                #path_list.extend(self.userTrackMap[track])
                path_list.extend(x for x in self.trackList[track] if x not in path_list)
                self.userTrackMap[track] = path_list
            else:
                self.userTrackMap[track] = self.trackList[track]

        self.save_track_list()

    # ----------------------------------------------------------

    def __init__(self, root_path, trackListPath):
        self.workingDir = root_path
        self.trackListPath = trackListPath

        self.get_track_list(self.workingDir)
        self.read_users_track_map(self.trackListPath)
        self.update_users_track_map()

    def save_track_list(self):
        json_track_list = []
        global userTrackMap

        for track in self.userTrackMap:
            path_list = self.userTrackMap[track]
            for path in path_list:
                json_track_list.append({'title': track, 'path': path})

        with open(trackListPath, 'w') as outfile:
            json.dump(json_track_list, outfile)
    # ----------------------------------------------------------

    def check_if_file_exists(self, title):
        if title in self.userTrackMap.keys():
            return True
        else:
            return False
    # ----------------------------------------------------------

    def add_new_track_describe(self, title, path):
        global userTrackMap

        if title in self.userTrackMap.keys():
            path_list = self.userTrackMap[title]
            path_list.append(path)
            self.userTrackMap[title] = path_list
        else:
            path_list = [path]
            self.userTrackMap[title] = path_list

        self.save_track_list()
    # ----------------------------------------------------------


class MusicManager:
    workingDir = ''
    trackListPath = ''

    def __init__(self, root_path, track_list_path):
        self.workingDir = root_path
        self.trackListPath = track_list_path

    def download_iteration(self):
        time_start = time()
        global workingDir

        file_manager = FileManager(self.workingDir, trackListPath)

        count = 5
        for i in vk_audio.get(owner_id=my_id):
            title = i["artist"] + '-' + i["title"] + '.mp3'
            # if list_dir.count(title) > 0:
            if file_manager.check_if_file_exists(title):
                print(title + ' already exist')
                continue

            try:
                r = requests.get(i["url"])
                if r.status_code == REQUEST_STATUS_CODE:
                    with open(title, 'wb') as output_file:
                        print(title + ' download and save to file')
                        output_file.write(r.content)
                        file_manager.add_new_track_describe(title, self.workingDir)
                        if count <= 0:
                            break
                        count = count - 1

            except OSError:
                print(i["artist"] + '-' + i["title"])

        file_manager.save_track_list()

        time_finish = time()
        print("Time seconds:", time_finish - time_start)
        print("Download complete")
        # ----------------------------------------------------------


mus_man = MusicManager(rootPath, trackListPath)
mus_man.download_iteration()
