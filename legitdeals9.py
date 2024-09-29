from pyrogram import Client
import asyncio
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

async def get_chat_ids(app: Client):
    """Retrieve chat IDs for groups and supergroups."""
    chat_ids = []
    chat_with_topic = {}
    async for dialog in app.get_dialogs():
        if hasattr(dialog.chat, 'is_forum') and dialog.chat.is_forum:
            try:
                chat_with_topic[dialog.chat.id] = dialog.top_message.topics.id
            except AttributeError:
                pass
        chat_ids.append(dialog.chat.id)
    # Filter out non-supergroup IDs
    chat_ids = [chat_id for chat_id in chat_ids if str(chat_id).startswith('-')]
    return [chat_ids, chat_with_topic]

async def send_last_message_to_groups(apps, timee, numtime):
    """Send the last message to all groups and supergroups."""
    async def send_last_message(app: Client):
        ac = await get_chat_ids(app)
        chat_ids = ac[0]
        chat_with_topic = ac[1]

        for i in range(numtime):
            try:
                async for message in app.get_chat_history('me', limit=1):
                    last_message = message.id
                    break  # Break the loop after fetching the last message
            except Exception as e:
                print(f"{Fore.RED}Failed to fetch last message: {e}")
                last_message = None

            if last_message is not None:
                for chat_id, topic_id in chat_with_topic.items():
                    try:
                        await app.forward_messages(chat_id=chat_id, from_chat_id="me", message_ids=last_message, message_thread_id=topic_id)
                        print(f"{Fore.GREEN}Message sent to chat_id {chat_id} with topic")
                    except Exception as e:
                        if "CHANNEL_PRIVATE" in str(e):
                            print(f"{Fore.YELLOW}Skipped chat_id {chat_id} - Inaccessible (private channel)")
                        else:
                            print(f"{Fore.RED}Failed to send message to chat_id {chat_id} with topic due to: {e}")
                    await asyncio.sleep(2)

                for chat_id in chat_ids:
                    try:
                        await app.forward_messages(chat_id, "me", last_message)
                        print(f"{Fore.GREEN}Message sent to chat_id {chat_id}")
                    except Exception as e:
                        if "CHANNEL_PRIVATE" in str(e):
                            print(f"{Fore.YELLOW}Skipped chat_id {chat_id} - Inaccessible (private channel)")
                        else:
                            print(f"{Fore.RED}Failed to send message to chat_id {chat_id}: {e}")
                    await asyncio.sleep(5)

            await asyncio.sleep(timee)

    await asyncio.gather(*(send_last_message(app) for app in apps))

async def leave_chats(app, chat_ids):
    """Leave all chats in the provided list."""
    for chat_id in chat_ids:
        try:
            await app.leave_chat(chat_id)
            print(f"{Fore.CYAN}Left chat_id {chat_id}")
        except Exception as e:
            print(f"{Fore.RED}Failed to leave chat_id {chat_id}: {e}")

async def join_group(app, chat_id):
    """Join a specific group by its ID."""
    try:
        await app.join_chat(chat_id)
        print(f"{Fore.MAGENTA}Joined chat_id {chat_id}")
    except Exception as e:
        print(f"{Fore.RED}Failed to join chat_id {chat_id}: {e}")

async def main():
    num_sessions = int(input("Enter the number of sessions: "))
    apps = []

    for i in range(num_sessions):
        session_name = f"my_account{i + 1}"
        try:
            # Try loading the existing session
            app = Client(session_name)
            await app.start()
        except:
            # If the session file doesn't exist, ask for API credentials
            api_id = int(input(f"Enter API ID for {session_name}: "))
            api_hash = input(f"Enter API Hash for {session_name}: ")
            app = Client(session_name, api_id=api_id, api_hash=api_hash)
            await app.start()
        apps.append(app)

    while True:
        a = int(input(
            f"{Style.BRIGHT}{Fore.YELLOW}2. AutoSender\n3. Auto Group Joiner\n4. Leave all groups\n5. Add user to all groups (will only work with one login)\n6. Exit\nEnter the choice: {Style.RESET_ALL}"
        ))

        if a == 2:
            numtime = int(input("How many times do you want to send the message: "))
            timee = int(input("Enter the time delay (in seconds): "))
            try:
                await send_last_message_to_groups(apps, timee, numtime)
            except Exception as e:
                print(f"{Fore.RED}Error in AutoSender: {e}")

        elif a == 3:
            for app in apps:
                chat_id = input("Enter the Chat ID to join: ")
                await join_group(app, chat_id)

        elif a == 4:
            for app in apps:
                chat_ids = await get_chat_ids(app)
                await leave_chats(app, chat_ids)

        elif a == 5:
            user_id = input("Enter the user ID to add to all groups: ")
            chat_ids = await get_chat_ids(app)
            for chat_id in chat_ids:
                for app in apps:
                    await app.add_chat_members(chat_id, user_id)

        elif a == 6:
            for app in apps:
                await app.stop()
            break

if __name__ == "__main__":
    asyncio.run(main())
