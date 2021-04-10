This repository contains the code of a small discord bot that allows to create questions. Members of the server can *bid* on the write answer. Finally, when the winning answer is designed, the bot computes the transactions needed to give to the winners their gains. The *bid value* is set by the question creator.

Logo come from : https://pixabay.com/fr/photos/casino-cartes-blackjack-1030852/

# Installation

Bot private token should be written in "private_token.txt" file.
Then run "run.sh"

## Bot required permissions :

- Send messages
- Manage messages
- Read message history
- Add reactions

# Bot usage

- `!create_gamble <title>`
- `!set_title <id> <title>`
- `!set_descr <id> <descr>`
- `!set_bid_value <id> <value>`
- `!add_choice <id> <choice>`
- `!edit_choice <id> <choice_letter> <new_choice>`
- `!lock <id>`
- `!unlock <id>`
- `!winner <id> <choice_letter>`

# TODO

- Save current gambles to disk when bot is shutdown