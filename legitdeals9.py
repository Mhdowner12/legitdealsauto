from pyrogram import Client
import asyncio
from colorama import Fore, Style, init
from pyfiglet import figlet_format

init(autoreset=True)

# Function to print the promotional message and your name in big blue letters
def print_big_name(name):
    # Print promotional message in red
    print(f"{Fore.RED}For Buy this Script tg : @LegitDeals9")
    # Print your name in big blue letters
    ascii_art = figlet_format(name)
    print(f"{Fore.BLUE}{ascii_art}")

# Print the promotional message and your name
print_big_name("@LegitDeals9")

async def get_chat_ids(app: Client):
    chat_ids = []
    chat_with_topic = {}
    async for dialog in app.get_dialogs():
        if hasattr(dialog.chat, 'is_forum') and dialog.chat.is_forum:
            try:
                chat_with_topic[dialog.chat.id] = dialog.top_message.topics.id
            except AttributeError:
                pass
        chat_ids.append(dialog.chat.id)
    chat_ids = [str(chat_id) for chat_id in chat_ids if str(chat_id).startswith('-')]
    chat_ids = [int(chat_id) for chat_id in chat_ids]
    return [chat_ids, chat_with_topic]

async def send_last_message_to_groups(apps, timee, numtime):
    async def send_last_message(app: Client):
        ac = await get_chat_ids(app)
        chat_ids = ac[0]
        chat_with_topic = ac[1]

        for _ in range(numtime):
            try:
                async for message in app.get_chat_history('me', limit=1):
                    last_message = message.id
                    break
            except Exception as e:
                print(f"{Fore.RED}Failed to fetch last message: {e}")
                last_message = None

            if last_message is not None:
                for chat_id in chat_with_topic.keys():
                    try:
                        await app.forward_messages(
                            chat_id=chat_id, 
                            from_chat_id="me", 
                            message_ids=last_message, 
                            message_thread_id=chat_with_topic[chat_id]
                        )
                    except Exception as e:
                        print(f"Failed to forward message to chat_id {chat_id}: {e}")
                    else:
                        print(f"{Fore.GREEN}Message sent to chat_id {chat_id}")
                    await asyncio.sleep(2)

                for chat_id in chat_ids:
                    try:
                        await app.forward_messages(chat_id, "me", last_message)
                        print(f"{Fore.GREEN}Message sent to chat_id {chat_id}")
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"{Fore.RED}Failed to send message to chat_id {chat_id}: {e}")
                    await asyncio.sleep(5)

            await asyncio.sleep(timee)

    await asyncio.gather(*(send_last_message(app) for app in apps))

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
