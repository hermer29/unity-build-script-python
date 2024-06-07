from telethon import TelegramClient
import sys, io, shutil, unityplugin
from os import path
from git import Repo
from CLI import CLI

artifactsFolderPath = "./artifacts"

cli = CLI()

def create_build_folder_name():
    from datetime import datetime
    projectName = cli.get("Project_Name")
    time = datetime.now()
    datePart = now.strftime("%d.%m.%Y")
    timePart = now.strftime("%H.%M")
    return f"{datePart}_{projectName}_{timePart}"

buildFolderName = create_build_folder_name()
buildFolderRelativePath = path.join(artifactsFolderPath, buildFolderName)
buildFolderAbsolutePath = path.abspath(buildFolderRelativePath)

def create_client() -> TelegramClient:
    sessionFilePath = cli.get("Telegram_SessionPath")
    apiId = cli.get("Telegram_ApiId")
    apiHash = cli.get("Telegram_ApiHash")
    return TelegramClient(sessionFilePath, 
                          api_id=apiId, 
                          api_hash=apiHash, 
                          system_lang_code='ru', 
                          device_model="Huawei MateBook D 53013YDN",
                          lang_code='ru',
                          system_version='Windows 22H2'
                          )

async def send_message(message: str):
    chatId = cli.get("Telegram_ChatId")
    await Client.send_message(await Client.get_entity(chatId), message)

async def send_message_with_file(message: str, file: str):
    chatId = cli.get("Telegram_ChatId")
    uploadHandle = await Client.upload_file(file)
    await Client.send_file(await Client.get_entity(chatId), caption=message, file=uploadHandle, force_document=True)
    
async def send_beginning_message():
    projectName = cli.get("Project_Name")
    lastCommitMessage = Repo(".").head.commit.message
    message = f"❗❗❗Начат билд по проекту {projectName}!\nПроизошедшие изменения: {lastCommitMessage}\n"
    await send_message(message)

async def send_unity_error_message(exitCode, logsPath):
    projectName = cli.get("Project_Name")
    lastCommitMessage = Repo(".").head.commit.message
    #Демонстрационная ссылка: https://immgames.ru/Games/Wolf/{projectName}.Внимание! После следующего обновления эта версия игры \"сгорит\" из ссылки.#
    message = f"""❌ CD для проекта {projectName} завершился с ошибкой: 
    unity отдал exit code: {exitCode}
    Билд для коммита с сообщением: {lastCommitMessage}
    Прилагаются логи сборки"""
    await send_message_with_file(message, logsPath)

async def send_ending_message():
    projectName = cli.get("Project_Name")
    lastCommitMessage = Repo(".").head.commit.message
    #Демонстрационная ссылка: https://immgames.ru/Games/Wolf/{projectName}.Внимание! После следующего обновления эта версия игры \"сгорит\" из ссылки.#
    message = f"""✅ Новый билд по проекту {projectName}! 
    Произошедшие изменения: {lastCommitMessage}
    Прилагается архив с билдом:"""
    await send_message_with_file(message, buildArchivePath)

Client = create_client()

def get_logs_file_path():
    return f"{artifactsFolderPath}/unity.log"

async def main():
    global buildFolderAbsolutePath
    #await send_beginning_message()
    unityPath = cli.get("Unity_Path")
    unityPassword = cli.get("Unity_Password")
    unityUsername = cli.get("Unity_Username")
    logsPath = get_logs_file_path()
    projectPath = unityplugin.find_unity_project_folder(".")
    exitCode = unityplugin.run_unity(
        buildFolderAbsolutePath = buildFolderAbsolutePath, 
        unityPath = unityPath, 
        password = unityPassword, 
        username = unityUsername,
        logsPath = logsPath,
        projectPath = projectPath
        )
    global buildArchivePath
    if exitCode == 0:
        buildArchivePath = buildFolderAbsolutePath
        print(f"Preparing folder {buildFolderAbsolutePath} to compression into {buildArchivePath}")
        buildArchivePath = compress_folder_contents_into_folder(fromFolder=buildFolderAbsolutePath,
                                                                toArchive=buildArchivePath)
        print(f"Compression result: {buildArchivePath}")
        await send_ending_message()
    elif exitCode != 0:
        await send_unity_error_message(exitCode, logsPath)
        raise Exception("Build error occured. ExitCode: {exitCode}")
        

def compress_folder_contents_into_folder(fromFolder, toArchive):
    return shutil.make_archive(
        base_name=toArchive, 
        format='zip', 
        root_dir=fromFolder)

with Client:
    Client.loop.run_until_complete(main())
