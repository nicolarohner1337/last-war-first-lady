# Last War First Lady Bot
This is a bot for the game Last War. It helps to manage the buffs queue. And appoints the buffs to the users. It navigates with visual recognition.
It's a bit crappy but it works.

# Bot Commands
- `/status` - Shows global waitig time per buff.
- `/queue` - Shows the current queue of the user.
- `/buff training` - Adds the buff to training queue.
- `/buff heal` - Adds the buff to heal queue.
- `/buff research` - Adds the buff to research queue.
- `/buff construction` - Adds the buff to construction queue.

# Installation
- `poetry install`
- Run Last War in BlueStacks with 1600x900 resolution.
- - If you have another game language, you need to retake the screenshots.
- `poetry run python main.py`
- Now press top-left corner and bottom-right corner of the BlueStacks Window. So the bot can calculate the screen size.
- Than press on chat input box. So the bot can calculate the chat input box position.
- Than press on the return button. So the bot can calculate the return button position.
- Than navigate to the buffs page.
- - Now Click on the position of the buffs to calculate the positions.
- Navigate to the chat page.
- Bot is ready to use.
- If positions are not calculated correctly, you can delete the `positions_saetting.json` file and try again. On next run, it will ask for the positions again.
- The current waiting times are stored in the `waiting_list.json` file. You can update them manually if you want.
- - #TODO: If you start bot and there are waiting times, it will try to appoint the buffs without respecting the current cooldowns. 
