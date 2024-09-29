from pyrogram import Client, errors
import asyncio
from colorama import Fore, Style, init
from pyfiglet import figlet_format

# Initialize colorama
init(autoreset=True)

# Function to print the promotional message and your name in big blue letters
def print_big_name(name):
    print(f"{Fore.RED}For Buy this Script tg : @LegitDeals9")
    ascii_art = figlet_format(name)
    print(f"{Fore.BLUE}{ascii_art}")

# Print the promotional message and your name
print_big_name("@LegitDeals9")

# Function to get group chat IDs using Pyrogram (skip channels and private chats)
async def get_group_chat_ids(app: Client):
    chat_ids = []
    async for dialog in app.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                # Test if the user can send a message by sending a simple message (to check permissions)
                await app.send_message(dialog.chat.id, ".")
                await asyncio.sleep(1)  # Avoid hitting flood limits
                chat_ids.append(dialog.chat.id)
                print(f"{Fore.GREEN}Added group {dialog.chat.title} (id: {dialog.chat.id})")
            except errors.ChatWriteForbidden:
                print(f"{Fore.YELLOW}Skipping group {dialog.chat.title} (id: {dialog.chat.id}) - No permission to send messages.")
            except Exception as e:
                print(f"{Fore.YELLOW}Skipping group {dialog.chat.title} (id: {dialog.chat.id}) - {e}")
    return chat_ids

# Function to send the last message to groups
async def send_last_message_to_groups(apps, timee, numtime):
    async def send_last_message(app: Client):
        chat_ids = await get_group_chat_ids(app)

        for _ in range(numtime):
            try:
                # Fetch the last message from 'me' (Saved Messages)
                async for message in app.get_chat_history('me', limit=1):
                    last_message = message.id
                    break
            except Exception as e:
                print(f"{Fore.RED}Failed to fetch last message: {e}")
                last_message = None

            if last_message is not None:
                for chat_id in chat_ids:
                    try:
                        # Forward the last message to the group
                        await app.forward_messages(chat_id, "me", last_message)
                        print(f"{Fore.GREEN}Message sent to chat_id {chat_id}")
                        await asyncio.sleep(2)  # Delay to avoid spamming
                    except errors.FloodWait as e:
                        print(f"{Fore.YELLOW}Flood wait error: Waiting for {e.x} seconds.")
                        await asyncio.sleep(e.x)
                    except Exception as e:
                        # Handle and skip any errors without stopping the script
                        print(f"{Fore.YELLOW}Skipping chat_id {chat_id} - Error: {e}")
            await asyncio.sleep(timee)

    await asyncio.gather(*(send_last_message(app) for app in apps))

# Main function to initialize Pyrogram sessions
async def main():
    num_sessions = int(input("Enter the number of sessions: "))
    apps = []

    # Prompt for API ID and API Hash
    api_id = int(input("Enter your API ID: "))
    api_hash = input("Enter your API Hash: ")

    for i in range(num_sessions):
        session_name = f"my_account{i + 1}"
        try:
            app = Client(session_name)
            await app.start()
        except Exception as e:
            print(f"{Fore.RED}Failed to start session {session_name}: {e}")
            app = Client(session_name, api_id=api_id, api_hash=api_hash)
            await app.start()
        apps.append(app)

    while True:
        a = int(input(
            f"{Style.BRIGHT}{Fore.YELLOW}1. AutoSender\n6. Exit\nEnter the choice: {Style.RESET_ALL}"
        ))

        if a == 1:
            numtime = int(input("How many times do you want to send the message: "))
            timee = int(input("Enter the time delay (in seconds): "))
            try:
                await send_last_message_to_groups(apps, timee, numtime)
            except Exception as e:
                print(f"{Fore.RED}Error in AutoSender: {e}")

        elif a == 6:
            for app in apps:
                await app.stop()
            break

if __name__ == "__main__":
    asyncio.run(main())
