import os
import time
import shutil
import zipfile
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import rarfile
import subprocess

# Function to display progress
async def progress(current, total, message: Message, start_time: float):
    progress_percentage = current / total * 100
    elapsed_time = time.time() - start_time
    speed = current / elapsed_time if elapsed_time > 0 else 0
    speed_str = f"{speed / 1024:.2f} KB/s" if speed < 1024 * 1024 else f"{speed / (1024 * 1024):.2f} MB/s"
    
    await message.edit_text(f"Progress: {progress_percentage:.2f}%\nSpeed: {speed_str}")


CMD = ["/"]
active_tasks = {}

# Handle file upload and extraction
@Client.on_message(filters.document)
async def handle_file(client, message):
    user_id = message.from_user.id
    document = message.document

    if document.mime_type == 'application/zip':
        download_message = None
        file_path = None
        unzip_dir = None
        try:
            download_message = await message.reply("⏳ Downloading the ZIP file...")
            start = time.time()

            # Download the zip file
            file_path = await message.download(
                file_name=document.file_name,
                progress=progress,
                progress_args=("⬇️ Downloading...", download_message, start)
            )

            await download_message.edit("⏳ Extracting the ZIP file...")

            unzip_dir = os.path.join(tempfile.gettempdir(), f'unzipped_{user_id}')
            os.makedirs(unzip_dir, exist_ok=True)

            # Extract files asynchronously
            task = asyncio.create_task(extract_and_send_files(client, message, file_path, unzip_dir, download_message, start))
            active_tasks[user_id] = task

            await task

        except zipfile.BadZipFile:
            await download_message.edit("❌ The file you sent is not a valid ZIP file.")
        except asyncio.CancelledError:
            await download_message.edit("❌ Unzipping has been cancelled.")
        except Exception as e:
            await download_message.edit(f"❌ An error occurred: {e}")
        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            if unzip_dir and os.path.exists(unzip_dir):
                shutil.rmtree(unzip_dir)
            active_tasks.pop(user_id, None)

    elif document.mime_type == 'application/x-rar-compressed':
        download_message = None
        file_path = None
        unrar_dir = None
        try:
            download_message = await message.reply("⏳ Downloading the RAR file...")
            start = time.time()

            # Download the rar file
            file_path = await message.download(
                file_name=document.file_name,
                progress=progress,
                progress_args=("⬇️ Downloading...", download_message, start)
            )

            await download_message.edit("⏳ Extracting the RAR file...")

            unrar_dir = os.path.join(tempfile.gettempdir(), f'unrarred_{user_id}')
            os.makedirs(unrar_dir, exist_ok=True)

            # Extract RAR files
            task = asyncio.create_task(extract_and_send_rar_files(client, message, file_path, unrar_dir, download_message, start))
            active_tasks[user_id] = task

            await task

        except rarfile.Error:
            await download_message.edit("❌ The file you sent is not a valid RAR file.")
        except asyncio.CancelledError:
            await download_message.edit("❌ Unraring has been cancelled.")
        except Exception as e:
            await download_message.edit(f"❌ An error occurred: {e}")
        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            if unrar_dir and os.path.exists(unrar_dir):
                shutil.rmtree(unrar_dir)
            active_tasks.pop(user_id, None)

    else:
        await message.reply("⚠️ Please send a valid ZIP or RAR file.")


# Extract and send ZIP files
async def extract_and_send_files(client, message, file_path, unzip_dir, download_message, start):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)

    await download_message.edit("⬆️ Sending the extracted files...")

    for root, _, files in os.walk(unzip_dir):
        for file_name in files:
            extracted_file_path = os.path.join(root, file_name)
            await client.send_document(
                chat_id=message.chat.id,
                document=extracted_file_path,
                progress=progress,
                progress_args=("⬆️ Uploading...", download_message, start)
            )

    await download_message.edit("✅ All files have been extracted and sent successfully.")


# Extract and send RAR files
async def extract_and_send_rar_files(client, message, file_path, unrar_dir, download_message, start):
    with rarfile.RarFile(file_path, 'r') as rarf:
        rarf.extractall(unrar_dir)

    await download_message.edit("⬆️ Sending the extracted files...")

    for root, _, files in os.walk(unrar_dir):
        for file_name in files:
            extracted_file_path = os.path.join(root, file_name)
            await client.send_document(
                chat_id=message.chat.id,
                document=extracted_file_path,
                progress=progress,
                progress_args=("⬆️ Uploading...", download_message, start)
            )

    await download_message.edit("✅ All files have been extracted and sent successfully.")


# Command to create a .zip file
@Client.on_message(filters.command("zip", CMD))
async def zip_files(client: Client, message: Message):
    try:
        file_paths = message.text.split()[1:]
        if not file_paths:
            await message.reply_text("Please provide file paths to zip. Example: /zip file1.txt file2.txt")
            return
        
        zip_filename = "archive.zip"
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in file_paths:
                zipf.write(file, os.path.basename(file))

        start_time = time.time()
        await message.reply_document(zip_filename, progress=progress, progress_args=(message, start_time))
        os.remove(zip_filename)
    except Exception as e:
        await message.reply_text(f"Error: {e}")


# Command to extract .zip file
@Client.on_message(filters.command("unzip", CMD))
async def unzip_files(client: Client, message: Message):
    try:
        if message.document and message.document.file_name.endswith(".zip"):
            zip_file = await message.download(progress=progress, progress_args=(message, time.time()))
            extracted_folder = "extracted_files"
            os.makedirs(extracted_folder, exist_ok=True)
            
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                zipf.extractall(extracted_folder)

            for root, _, files in os.walk(extracted_folder):
                for file in files:
                    start_time = time.time()
                    await message.reply_document(os.path.join(root, file), progress=progress, progress_args=(message, start_time))

            for root, _, files in os.walk(extracted_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                os.rmdir(root)

            os.remove(zip_file)
        else:
            await message.reply_text("Please send a valid .zip file to extract.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


# Command to create a .rar file (requires external `rar` utility)
@Client.on_message(filters.command("rar", CMD))
async def rar_files(client: Client, message: Message):
    try:
        file_paths = message.text.split()[1:]
        if not file_paths:
            await message.reply_text("Please provide file paths to create rar. Example: /rar file1.txt file2.txt")
            return
        
        rar_filename = "archive.rar"
        command = ['rar', 'a', rar_filename] + file_paths
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            await message.reply_text(f"Error creating .rar file: {result.stderr}")
            return
        
        start_time = time.time()
        await message.reply_document(rar_filename, progress=progress, progress_args=(message, start_time))
        os.remove(rar_filename)
    except Exception as e:
        await message.reply_text(f"Error: {e}")


# Command to extract .rar file
@Client.on_message(filters.command("unrar", CMD))
async def unrar_files(client: Client, message: Message):
    try:
        if message.document and message.document.file_name.endswith(".rar"):
            rar_file = await message.download(progress=progress, progress_args=(message, time.time()))
            extracted_folder = "extracted_rar_files"
            os.makedirs(extracted_folder, exist_ok=True)
            
            with rarfile.RarFile(rar_file, 'r') as rarf:
                rarf.extractall(extracted_folder)

            for root, _, files in os.walk(extracted_folder):
                for file in files:
                    start_time = time.time()
                    await message.reply_document(os.path.join(root, file), progress=progress, progress_args=(message, start_time))

            for root, _, files in os.walk(extracted_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                os.rmdir(root)

            os.remove(rar_file)
        else:
            await message.reply_text("Please send a valid .rar file to extract.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
