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
        if dialog.chat.type in ["group", "supergroup"]:  # Ensure you're only adding groups
            chat_ids.append(dialog.chat.id)
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
                        print(f"{Fore.GREEN}Message sent to chat_id {chat_id} (with topic)")
                    except Exception as e:
                        if "CHANNEL_PRIVATE" in str(e):
                            print(f"{Fore.RED}Cannot access chat_id {chat_id} (private or restricted). Skipping.")
                        else:
                            print(f"{Fore.RED}Failed to forward message to chat_id {chat_id}: {e}")
                    await asyncio.sleep(2)

                for chat_id in chat_ids:
                    try:
                        await app.forward_messages(chat_id, "me", last_message)
                        print(f"{Fore.GREEN}Message sent to chat_id {chat_id}")
                        await asyncio.sleep(2)
                    except Exception as e:
                        if "CHANNEL_PRIVATE" in str(e):
                            print(f"{Fore.RED}Cannot access chat_id {chat_id} (private or restricted). Skipping.")
                        else:
                            print(f"{Fore.RED}Failed to send message to chat_id {chat_id}: {e}")
                    await asyncio.sleep(5)

            await asyncio.sleep(timee)

    await asyncio.gather(*(send_last_message(app
