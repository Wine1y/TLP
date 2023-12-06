# Treasure of a Lonely Planet (TLP)
Telegram bot-game where you can explore a randomly generated map using the energy of the sun, look for treasures buried by other players, and burry your own treasures!

Originally, this bot was created as a freelance task but the employer disappeared in the middle of the project, so **many mechanics were not finished**.
# Commands
  - **/start** - Adds a new player and sends the game rules
  - **/map** - Sends full current map as a .png image
  - **/random_map** - Sends randomly generated map as a .png image
  - **/play** - Sends a playing field and controller-buttons
  - **/tp** - Teleports a specified player to a specified coordinates
  - **/energy** - Sets a specified amount of energy to a specified player
# Configuration
  Edit "config.env" to configure your bot
  - **BOT_TOKEN** - Telegram bot token
  - **DATABASE_URL** - Url to the database
  - **MAP_SIZE** - Size of the bot map in tiles
  - **SECTION_SIZE** - Size of the section which will be used as a playing field
  - **TILE_SIZE** - Size of one tile in pixels
  - **STARTING_CORDS** - coordinates where new users will be placed. Format - `x,y`

  Textures can be configured by editing png images at *assets/textures*
# Field screenshot
<image src="screenshots/field.png"/>