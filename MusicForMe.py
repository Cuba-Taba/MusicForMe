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
root_path = os.path.join("D:\\vk\\course\\music", name_dir)
trackListFile = "tracklist.json"
login = '79282254991'  # Номер телефона
password = 'Vk*1478963'  # Пароль
# my_id = '553384473'  # Ваш id vk
my_id = '191842670'  # Ваш id vk

vk_session = vk_api.VkApi(login=login, password=password)
vk_session.auth()
vk = vk_session.get_api()  # Теперь можно обращаться к методам API как к обычным классам
vk_audio = audio.VkAudio(vk_session)

if not os.path.exists(root_path):
    os.makedirs(root_path)

trackListPath = os.path.join(root_path, trackListFile)

os.chdir(root_path)
list_dir = os.listdir(root_path)
# ----------------------------------------------------------

def setDescribeTrack(track_list, title, path_file, status):
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

def checkFileInTrackList(file_name):
    global trackList
    if trackList.get(file_name):
        descriptions = trackList[file_name]
        for description in descriptions:
            if description.get('path'):
                print(description['path'])
                return description['path']
# ----------------------------------------------------------


def copyFileToDir(currentPath, fileName, dstPath):
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

    def createTrackListFile(self):
        dst_data = {}
        with open(trackListPath, 'w+') as outfile:
            json.dump(dst_data, outfile)
        # ----------------------------------------------------------

    def getTrackList(self, current_path):
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
            self.getTrackList(os.path.join(current_path, d))

    def readUsersTrackMap(self, trackListPath):
        if list_dir.count(trackListFile) == 0:
            self.createTrackListFile()

        global userTrackMap

        with open(trackListPath) as json_file:
            data = json.load(json_file)
            for p in data:
                print('Title: ' + p['title'])
                print('Path: ' + p['path'])
                #print('Status: ' + p['status'])
                print('')

                title = p['title']
                filePath = p['path']

                if title in self.userTrackMap.keys():
                    path_list = self.userTrackMap.get(title)
                    path_list.append(filePath)
                    self.userTrackMap[title] = path_list
                    print(self.userTrackMap)
                else:
                    path_list = [filePath]
                    self.userTrackMap[title] = path_list
    # ----------------------------------------------------------

    def updateUsersTrackMap(self):

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

        self.saveTrackList()

    # ----------------------------------------------------------

    def __init__(self, root_path, trackListPath):
        self.workingDir = root_path
        self.trackListPath = trackListPath

        self.getTrackList(self.workingDir)
        self.readUsersTrackMap(self.trackListPath)
        self.updateUsersTrackMap()

    def saveTrackList(self):
        json_track_list = []
        global userTrackMap

        for track in self.userTrackMap:
            path_list = self.userTrackMap[track]
            for path in path_list:
                json_track_list.append({'title': track, 'path': path})

        with open(trackListPath, 'w') as outfile:
            json.dump(json_track_list, outfile)
    # ----------------------------------------------------------

    def checkIfFileExists(self, title):
        if title in self.userTrackMap.keys():
            return True
        else:
            return False
    # ----------------------------------------------------------

    def addNewTrackDescribe(self, title, path):
        global userTrackMap

        if title in self.userTrackMap.keys():
            path_list = self.userTrackMap[title]
            path_list.append(root_path)
            self.userTrackMap[title] = path_list
        else:
            path_list = [path]
            self.userTrackMap[title] = path_list

        self.saveTrackList()

class MusicManager:
    workingDir = ''
    trackListPath = ''
    def __init__(self, root_path, trackListPath):
        self.workingDir = root_path
        self.trackListPath = trackListPath

    def downloadIteration(self):
        time_start = time()

        fileManager = FileManager(root_path, trackListPath)

        count = 50
        for i in vk_audio.get(owner_id=my_id):
            title = i["artist"] + '-' + i["title"] + '.mp3'
            # if list_dir.count(title) > 0:
            if fileManager.checkIfFileExists(title):
                print(title + ' already exist')
                continue

            try:
                r = requests.get(i["url"])
                if r.status_code == REQUEST_STATUS_CODE:
                    with open(title, 'wb') as output_file:
                        print(title + ' download and save to file')
                        output_file.write(r.content)
                        fileManager.addNewTrackDescribe(title, root_path)
                        if count <= 0:
                            break
                        count = count - 1

            except OSError:
                print(i["artist"] + '-' + i["title"])

        fileManager.saveTrackList()

        time_finish = time()
        print("Time seconds:", time_finish - time_start)
        print("Download complete")
        # ----------------------------------------------------------

mus_man = MusicManager(root_path, trackListPath)
mus_man.downloadIteration()