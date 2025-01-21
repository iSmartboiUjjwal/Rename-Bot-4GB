import zipfile
import rarfile
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import time

CMD = ["/"]

# Function to display progress
async def progress(current, total, message: Message, start_time: float):
    # Calculate the progress percentage
    progress_percentage = current / total * 100
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    # Calculate speed (bytes per second)
    speed = current / elapsed_time if elapsed_time > 0 else 0
    speed_str = f"{speed/1024:.2f} KB/s" if speed < 1024 * 1024 else f"{speed / (1024 * 1024):.2f} MB/s"
    
    # Display progress
    await message.edit_text(f"Progress: {progress_percentage:.2f}%\nSpeed: {speed_str}")
    
@Client.on_message(filters.command("zip", CMD))
async def zip_files(client: Client, message: Message):
    try:
        # Check if the user provided any file paths after the command
        file_paths = message.text.split()[1:]  # Extract file paths after the command
        if not file_paths:
            await message.reply_text("Please provide file paths to zip. Example: /zip file1.txt file2.txt")
            return
        
        zip_filename = "archive.zip"  # Name of the output zip file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in file_paths:
                zipf.write(file, os.path.basename(file))  # Add files to the zip

        # Send the zipped file to the user with progress
        start_time = time.time()
        await message.reply_document(zip_filename, progress=progress, progress_args=(message, start_time))
        os.remove(zip_filename)  # Clean up the generated zip file
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Client.on_message(filters.command("unzip", CMD))
async def unzip_files(client: Client, message: Message):
    try:
        # Check if the user sent a .zip file
        if message.document and message.document.file_name.endswith(".zip"):
            zip_file = await message.download(progress=progress, progress_args=(message, time.time()))  # Download the file with progress
            extracted_folder = "extracted_files"
            os.makedirs(extracted_folder, exist_ok=True)
            
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                zipf.extractall(extracted_folder)

            # Send the extracted files to the user with progress
            for root, _, files in os.walk(extracted_folder):
                for file in files:
                    start_time = time.time()
                    await message.reply_document(os.path.join(root, file), progress=progress, progress_args=(message, start_time))

            # Clean up the extracted folder
            for root, _, files in os.walk(extracted_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                os.rmdir(root)

            os.remove(zip_file)  # Clean up the zip file
        else:
            await message.reply_text("Please send a valid .zip file to extract.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Client.on_message(filters.command("rar", CMD))
async def rar_files(client: Client, message: Message):
    try:
        # Check if the user provided any file paths after the command
        file_paths = message.text.split()[1:]  # Extract file paths after the command
        if not file_paths:
            await message.reply_text("Please provide file paths to create rar. Example: /rar file1.txt file2.txt")
            return
        
        rar_filename = "archive.rar"  # Name of the output rar file
        with rarfile.RarFile(rar_filename, 'w') as rarf:
            for file in file_paths:
                rarf.add(file)  # Add files to the rar

        # Send the rarred file to the user with progress
        start_time = time.time()
        await message.reply_document(rar_filename, progress=progress, progress_args=(message, start_time))
        os.remove(rar_filename)  # Clean up the generated rar file
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Client.on_message(filters.command("unrar", CMD))
async def unrar_files(client: Client, message: Message):
    try:
        # Check if the user sent a .rar file
        if message.document and message.document.file_name.endswith(".rar"):
            rar_file = await message.download(progress=progress, progress_args=(message, time.time()))  # Download the file with progress
            extracted_folder = "extracted_rar_files"
            os.makedirs(extracted_folder, exist_ok=True)
            
            with rarfile.RarFile(rar_file, 'r') as rarf:
                rarf.extractall(extracted_folder)

            # Send the extracted files to the user with progress
            for root, _, files in os.walk(extracted_folder):
                for file in files:
                    start_time = time.time()
                    await message.reply_document(os.path.join(root, file), progress=progress, progress_args=(message, start_time))

            # Clean up the extracted folder
            for root, _, files in os.walk(extracted_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                os.rmdir(root)

            os.remove(rar_file)  # Clean up the rar file
        else:
            await message.reply_text("Please send a valid .rar file to extract.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Client.on_message(filters.document)
async def handle_file(client: Client, message: Message):
    try:
        # Check if the file is a .zip or .rar file and handle extraction
        if message.document.file_name.endswith(".zip"):
            zip_file = await message.download(progress=progress, progress_args=(message, time.time()))  # Download the file with progress
            extracted_folder = "extracted_files"
            os.makedirs(extracted_folder, exist_ok=True)
            
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                zipf.extractall(extracted_folder)

            # Send the extracted files to the user with progress
            for root, _, files in os.walk(extracted_folder):
                for file in files:
                    start_time = time.time()
                    await message.reply_document(os.path.join(root, file), progress=progress, progress_args=(message, start_time))

            # Clean up the extracted folder
            for root, _, files in os.walk(extracted_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                os.rmdir(root)

            os.remove(zip_file)  # Clean up the zip file
        
        elif message.document.file_name.endswith(".rar"):
            rar_file = await message.download(progress=progress, progress_args=(message, time.time()))  # Download the file with progress
            extracted_folder = "extracted_rar_files"
            os.makedirs(extracted_folder, exist_ok=True)
            
            with rarfile.RarFile(rar_file, 'r') as rarf:
                rarf.extractall(extracted_folder)

            # Send the extracted files to the user with progress
            for root, _, files in os.walk(extracted_folder):
                for file in files:
                    start_time = time.time()
                    await message.reply_document(os.path.join(root, file), progress=progress, progress_args=(message, start_time))

            # Clean up the extracted folder
            for root, _, files in os.walk(extracted_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                os.rmdir(root)

            os.remove(rar_file)  # Clean up the rar file
        else:
            await message.reply_text("Please send a valid .zip or .rar file to extract.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
