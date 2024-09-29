from pyrogram import Client
import asyncio
from colorama import Fore, Style, init
from pyfiglet import figlet_format

init(autoreset=True)

# Function to print the promotional message and your name in big blue letters
def print_big_name(name):
    print(f"{Fore.RED}For Buy this Script tg : @LegitDeals9")
    ascii_art = figlet_format(name)
    print(f"{Fore.BLUE}{ascii_art}")

# Print the promotional message and your name
print_big_name("@LegitDeals9")

async def get_chat_ids(app: Client):
    chat_ids = []
    async for dialog in app.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            chat_ids.append(dialog.chat.id)
    return chat_ids

async def send_last_message_to_groups(apps, timee, numtime):
    async def send_last_message(app: Client):
        # Fetch the last message from your own chat history
        try:
            async for message in app.get_chat_history('me', limit=1):
                last_message = message.id
                break
        except Exception as e:
            print(f"{Fore.RED}Failed to fetch last message: {e}")
            return  # Exit if last message cannot be fetched

        if last_message is not None:
            chat_ids = await get_chat_ids(app)

            for chat_id in chat_ids:
                try:
                    await app.get_chat(chat_id)  # Check if the chat is accessible
                    await app.forward_messages(chat_id, "me", last_message)
                    print(f"{Fore.GREEN}Message sent to chat_id {chat_id}")
                except Exception as e:
                    handle_error(e, chat_id)  # Handle errors through a dedicated function
                await asyncio.sleep(2)  # Sleep between sends to avoid rate limiting

            await asyncio.sleep(timee)  # Delay before sending again

    # Run the function for all active sessions
    await asyncio.gather(*(send_last_message(app) for app in apps))

def handle_error(e, chat_id):
    """Handle errors for sending messages."""
    if "CHANNEL_PRIVATE" in str(e):
        print(f"{Fore.YELLOW}Skipping chat_id {chat_id}. Reason: This channel is private.")
    elif "USER_NOT_PARTICIPANT" in str(e):
        print(f"{Fore.YELLOW}Skipping chat_id {chat_id}. Reason: You are not a participant.")
    elif "CHAT_ADMIN_REQUIRED" in str(e):
        print(f"{Fore.RED}Cannot send message to chat_id {chat_id}. Reason: Admin privileges required.")
    elif "FLOOD_WAIT" in str(e):
        print(f"{Fore.RED}Rate limit exceeded. Sleeping before retrying.")
        # Implement a retry after a delay if flood wait is encountered
        await asyncio.sleep(5)  # Increase the wait time as necessary
    else:
        print(f"{Fore.RED}Failed to send to chat_id {chat_id}. Reason: {str(e)}")

async def main():
    num_sessions = int(input("Enter the number of sessions: "))
    apps = []

    for i in range(num_sessions):
        session_name = f"my_account{i+1}"
        try:
            app = Client(session_name)
            await app.start()
        except Exception as e:
            print(f"{Fore.RED}Failed to start session {session_name}: {e}")
            api_id = int(input(f"Enter API ID for {session_name}: "))
            api_hash = input(f"Enter API hash for {session_name}: ")
            app = Client(session_name, api_id=api_id, api_hash=api_hash)
            await app.start()
        apps.append(app)

    while True:
        a = int(input(
            f"{Style.BRIGHT}{Fore.YELLOW}2. AutoSender\n6. Exit\nEnter the choice: {Style.RESET_ALL}"
        ))

        if a == 2:
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
