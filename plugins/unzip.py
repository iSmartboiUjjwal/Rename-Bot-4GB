import zipfile
import rarfile
import os
from pyrogram import Client, filters
from pyrogram.types import Message

CMD = ["/"]

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

        await message.reply_text(f"Files successfully zipped into {zip_filename}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Client.on_message(filters.command("unzip", CMD))
async def unzip_files(client: Client, message: Message):
    try:
        # Check if the user sent a .zip file
        if message.document and message.document.file_name.endswith(".zip"):
            zip_file = await message.download()  # Download the file to local
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                zipf.extractall("extracted_files")
            
            await message.reply_text(f"Files extracted to 'extracted_files' folder.")
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

        await message.reply_text(f"Files successfully rarred into {rar_filename}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Client.on_message(filters.command("unrar", CMD))
async def unrar_files(client: Client, message: Message):
    try:
        # Check if the user sent a .rar file
        if message.document and message.document.file_name.endswith(".rar"):
            rar_file = await message.download()  # Download the file to local
            with rarfile.RarFile(rar_file, 'r') as rarf:
                rarf.extractall("extracted_rar_files")
            
            await message.reply_text(f"Files extracted to 'extracted_rar_files' folder.")
        else:
            await message.reply_text("Please send a valid .rar file to extract.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Client.on_message(filters.document)
async def handle_file(client: Client, message: Message):
    try:
        # Check if the file is a .zip or .rar file and handle extraction
        if message.document.file_name.endswith(".zip"):
            zip_file = await message.download()  # Download the file to local
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                zipf.extractall("extracted_files")
            
            await message.reply_text(f"Files extracted from {message.document.file_name} to 'extracted_files' folder.")
        
        elif message.document.file_name.endswith(".rar"):
            rar_file = await message.download()  # Download the file to local
            with rarfile.RarFile(rar_file, 'r') as rarf:
                rarf.extractall("extracted_rar_files")
            
            await message.reply_text(f"Files extracted from {message.document.file_name} to 'extracted_rar_files' folder.")
        else:
            await message.reply_text("Please send a valid .zip or .rar file to extract.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
