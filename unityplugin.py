import io
from os import listdir
import os
from subprocess import Popen

def is_unity_project_folder(path : str) -> bool:
    dirs = listdir(path)
    return "Assets" in dirs and "Packages" in dirs and "ProjectSettings" in dirs
        
def find_unity_project_folder(path : str) -> str:
    if is_unity_project_folder(path):
        return path
    for filename in listdir(path):
        filePath = os.path.join(path, filename)
        if os.path.isfile(filePath):
            continue
        if is_unity_project_folder(filePath):
            return filePath
        else:
            foundFolder = find_unity_project_folder(filePath)
            if foundFolder == None:
                continue
            else:
                return foundFolder 
    return None

def clear_logs_file_if_exists(logsPath : str):
    if os.path.exists(logsPath):
        logs = io.open(logsPath, mode="w")
        logs.close()

def write_logs_from_file(process : Popen, logsPath : str):
    clear_logs_file_if_exists()
    while not os.path.exists(logsPath):
        continue
    with io.open(logsPath, mode="+r") as logs:
        while process.returncode == None:
            process.poll()
            written = logs.readlines()
            if len(written) == 0:
                continue
            else:
                print(''.join(written))

def run_unity(buildFolderAbsolutePath: str, unityPath: str, password: str, username: str, logsPath: str, 
              projectPath: str):
    unityBuildMethod = "BuilderScript.Editor.Builder.BuildWebGl"
    unityLaunchArguments = [
        #"xvfb-run", "--auto-servernum", "--server-args=\'-screen 0 640x480x24\'",
        unityPath,
       "-batchmode", 
        "-nographics", 
        "-force-free",
        "-buildtarget", "webgl",
        "-username", username,
        "-password", password,
        "-logFile", logsPath,
        "-executeMethod", unityBuildMethod,
        "-quit",
        "-projectPath", projectPath,
        "-build-folder-path", buildFolderAbsolutePath,
    ]
    print(f"Unity launch command: {unityLaunchArguments}")
    process = Popen(unityLaunchArguments)
    write_logs_from_file(process)