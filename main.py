from telethon import TelegramClient
import sys, io, shutil, subprocess
from os import path
from git import Repo

commandLineArguments = {}
artifactsFolderPath = "./artifacts"


def process_command_line_arguments():
    sliceObj = slice(1, len(sys.argv))
    sliced = sys.argv[sliceObj]
    print(sliced)
    for arg in sliced:
        keyValue = arg.split('=')
        keyValue[0] = keyValue[0].removeprefix('--')
        commandLineArguments[keyValue[0]] = keyValue[1]

process_command_line_arguments()

def create_build_folder_name():
    from datetime import datetime
    projectName = commandLineArguments["Project_Name"]
    time = datetime.now()
    datePart = f"{time.day}.{time.month}.{time.year}"
    timePart = f"{time.hour}.{time.month}"
    return f"{datePart}_{projectName}_{timePart}"

buildFolderName = create_build_folder_name()
buildFolderRelativePath = path.join(artifactsFolderPath, buildFolderName)
buildFolderAbsolutePath = path.abspath(buildFolderRelativePath)
global buildArchivePath

def create_client() -> TelegramClient:
    sessionFilePath = commandLineArguments["Telegram_SessionPath"]
    apiId = commandLineArguments["Telegram_ApiId"]
    apiHash = commandLineArguments["Telegram_ApiHash"]
    return TelegramClient(sessionFilePath, 
                          api_id=apiId, 
                          api_hash=apiHash, 
                          system_lang_code='ru', 
                          device_model="Huawei MateBook D 53013YDN",
                          lang_code='ru',
                          system_version='Windows 22H2'
                          )

async def send_message(message: str):
    chatId = commandLineArguments["Telegram_ChatId"]
    await Client.send_message(await Client.get_entity(chatId), message)

async def send_message_with_file(message: str, file: str):
    chatId = commandLineArguments["Telegram_ChatId"]
    uploadHandle = await Client.upload_file(file)
    await Client.send_file(await Client.get_entity(chatId), caption=message, file=uploadHandle, force_document=True)
    
async def send_beginning_message():
    projectName = commandLineArguments["Project_Name"]
    lastCommitMessage = Repo(".").head.commit.message
    message = f"❗❗❗Начат билд по проекту {projectName}!\nПроизошедшие изменения: {lastCommitMessage}\n"
    await send_message(message)

async def send_ending_message():
    projectName = commandLineArguments["Project_Name"]
    lastCommitMessage = Repo(".").head.commit.message
    #Демонстрационная ссылка: https://immgames.ru/Games/Wolf/{projectName}.Внимание! После следующего обновления эта версия игры \"сгорит\" из ссылки.#
    message = f"""❗❗❗Новый билд по проекту {projectName}! 
    Произошедшие изменения: {lastCommitMessage}
    Прилагается архив с билдом:"""
    await send_message_with_file(message, buildArchivePath)

Client = create_client()

def get_project_folder_path():
    projectName = commandLineArguments["Project_Name"]
    if path.exists("./src"):
        return f"./src/{projectName}"
    else:
        return "."

def get_logs_file_path():
    return f"{artifactsFolderPath}/unity.log"

def run_unity(): 
    unityPath = commandLineArguments["Unity_Path"]
    password = commandLineArguments["Unity_Password"]
    username = commandLineArguments["Unity_Username"]
    unityBuildMethod = "BuilderScript.Editor.Builder.BuildWebGl"
    unityLaunchArguments = [
        "xvfb-run", "--auto-servernum", "--server-args=\'-screen 0 640x480x24\'",
        unityPath,
       # "-batchmode", 
        "-nographics", 
        "-force-free",
        "-buildtarget", "webgl",
        "-username", username,
        "-password", password,
        "-logFile", get_logs_file_path(),
        "-executeMethod", unityBuildMethod,
        "-quit",
        "-projectPath", get_project_folder_path(),
        "-buildFolderPath", path.abspath(buildFolderName),
    ]
    print(f"Unity launch command: {unityLaunchArguments}")
    process = subprocess.Popen(unityLaunchArguments)
    write_logs_from_file(process)

def clear_logs_file_if_exists():
    if path.exists(get_logs_file_path()):
        logs = io.open(get_logs_file_path(), mode="w")
        logs.close()

def write_logs_from_file(process : subprocess.Popen):
    clear_logs_file_if_exists()
    while not path.exists(get_logs_file_path()):
        continue
    with io.open(get_logs_file_path(), mode="+r") as logs:
        while process.returncode == None:
            process.poll()
            written = logs.readlines()
            if len(written) == 0:
                continue
            else:
                print(''.join(written))

async def main():
    await send_beginning_message()
    run_unity()
    global buildArchivePath
    buildArchivePath = buildFolderAbsolutePath
    print(f"Preparing folder {buildFolderAbsolutePath} to compression into {buildArchivePath}")
    buildArchivePath = shutil.make_archive(
        base_name=buildArchivePath, 
        format='zip', 
        root_dir=buildFolderAbsolutePath)
    print(f"Compression result: {buildArchivePath}")
    await send_ending_message()

with Client:
    Client.loop.run_until_complete(main())