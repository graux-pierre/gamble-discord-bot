import discord
import os

bot = discord.Client()
bot.gambles = {}

LIST_EMOJI = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']
class Gamble:
    def __init__(self, gamble_id, admin_id, admin_name, title):
        self.gamble_id = gamble_id
        self.admin = admin_id
        self.admin_name = admin_name
        self.title = title
        self.bid_value = 0
        self.descr = " "
        self.bidders = {}
        self.choices = {}
        self.locked = False
        self.color = 0x00ff00
        self.winner = None

    def set_title(self, title):
        self.title = title

    def set_descr(self, descr):
        self.descr = descr

    def set_bid_value(self, bid_value):
        self.bid_value = bid_value

    def unlock(self):
        self.locked = False
        self.color = 0x00ff00

    def lock(self):
        self.locked = True
        self.color = 0xff0000

    def add_choice(self, choice):
        index = len(self.choices)
        if index < len(LIST_EMOJI):
            self.choices[LIST_EMOJI[index]] = (choice, set())
            return LIST_EMOJI[index]
        return None

    def set_choice(self, choice, choice_text):
        emoji = self.get_emoji_from_letter(choice)
        if emoji:
            (_, l) = self.choices[emoji]
            self.choices[emoji] = (choice_text, l)

    def emojis(self):
        return LIST_EMOJI[:len(self.choices)]

    def add_bid(self, emoji, bidder_id, bidder_name):
        if emoji in self.choices:
            if not bidder_id in self.bidders:
                (_, l) = self.choices[emoji]
                l.add(bidder_id)
                self.bidders[bidder_id] = bidder_name
                return True
        return False

    def remove_bid(self, emoji, bidder_id):
        if emoji in self.choices:
            (_, l) = self.choices[emoji]
            if bidder_id in l:
                l.remove(bidder_id)
                self.bidders.pop(bidder_id)

    def set_winner(self, choice):
        emoji = self.get_emoji_from_letter(choice)
        if emoji:
            self.lock()
            self.winner = emoji

    def compute_transactions(self):
        winners = []
        loosers = []
        for emoji in self.choices:
            (choice, users) = self.choices[emoji]
            for uid in users:
                user_display_name = self.bidders[uid]
                if emoji == self.winner:
                    winners.append(user_display_name)
                else:
                    loosers.append(user_display_name)

        if len(winners)>0:
            total_value = len(loosers) * self.bid_value
            value_per_winner = float(total_value) / len(winners)
            remaining_debt = {w: value_per_winner for w in winners}
            transactions = {l: [] for l in loosers}

            embedVar = None
            if len(loosers) > 0:
                if self.bid_value > 0:
                    while loosers:
                        l = loosers[0]
                        v = self.bid_value

                        for w in list(remaining_debt.keys()):
                            if v < remaining_debt[w]:
                                transactions[l].append((w, v))
                                remaining_debt[w] -= v
                                v = 0
                                break
                            elif v == remaining_debt[w]:
                                transactions[l].append((w, remaining_debt[w]))
                                remaining_debt[w] = 0
                                v -= remaining_debt[w]
                                remaining_debt.pop(w)
                                break
                            elif v > remaining_debt[w]:
                                transactions[l].append((w, remaining_debt[w]))
                                remaining_debt[w] = 0
                                v -= remaining_debt[w]
                                remaining_debt.pop(w)

                        loosers = loosers[1:]

                    embedVar = discord.Embed(title="[DEBT] " + self.title,
                                             description="You played, you loosed, you pay.\nEach winner win %s po" % str(value_per_winner),
                                             color=0xff0000)
                    descr = []
                    for l in transactions.keys():
                        text = l + " : "
                        temp_text = []
                        for (w, v) in transactions[l]:
                             temp_text.append("%s po  %s" % (str(v), w))
                        text += ", ".join(temp_text)
                        descr.append(text)
                    embedVar.add_field(name="List of transactions",
                                       value="\n".join(descr), inline=False)
                else:
                    embedVar = discord.Embed(title="[DEBT] " + self.title,
                                             description="No bid value set, no debt.",
                                             color=0x00ff00)
            else:
                embedVar = discord.Embed(title="[DEBT] " + self.title,
                                         description="No loosers, GG all!",
                                         color=0x00ff00)
        else:
            embedVar = discord.Embed(title="[DEBT] " + self.title,
                                     description="No Winners...",
                                     color=0x00ff00)

        return embedVar

    def get_emoji_from_letter(self, choice):
        choice = choice.lower()
        if len(choice) != 1:
            return None
        if not ('a' <= choice <= 'z'):
            return None
        emoji = LIST_EMOJI[ord(choice[0]) - ord('a')]
        if not emoji in self.choices:
            return None
        return emoji

    def createEmbed(self):

        title = self.title
        if self.locked:
            title = "[LOCKED] " + title

        descr = self.descr
        if self.bid_value:
            descr += "\n%i po/bid\nTotal bid: %ipo" % (self.bid_value,len(self.bidders)*self.bid_value)

        embedVar = discord.Embed(title=title,
                                 description=descr,
                                 color=self.color)

        footer = "id: %i, admin: %s" % (self.gamble_id, self.admin_name)
        embedVar.set_footer(text=footer)

        index = 0
        for emoji in self.choices:
            (choice, users) = self.choices[emoji]
            usernames = []
            for uid in users:
                user_display_name = self.bidders[uid]
                usernames.append(user_display_name)
            fieldValue = "Bid: " + ", ".join(usernames)
            embedVar.add_field(name=emoji + ' ' + choice,
                               value=fieldValue, inline=True)

        if self.winner:
            (_, users) = self.choices[self.winner]
            usernames = []
            for uid in users:
                user_display_name = self.bidders[uid]
                usernames.append(user_display_name)
            if len(usernames) == 0:
                fieldValue = "No winner"
            else :
                fieldValue = "Winner: " + " ".join(usernames)
            embedVar.add_field(name="Good choice: " + self.winner,
                               value=fieldValue, inline=False)

        return embedVar

async def check_gamble_id(gamble_id, channel):
    try:
        gamble_id=int(gamble_id)
        if gamble_id in bot.gambles:
            try:
                gamble_msg = await channel.fetch_message(gamble_id)
                if gamble_msg:
                    return True
            except:
                pass
    except:
        pass
    return False

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!create_gamble'):
        await message.delete()

        title = message.content[len('!create_gamble'):].lstrip()

        gamble_msg = await message.channel.send("Gamble in construction.")
        gamble = Gamble(gamble_msg.id, message.author.id, message.author.display_name, title)
        await gamble_msg.edit(content=None, embed=gamble.createEmbed())
        bot.gambles[gamble_msg.id] = gamble

    elif message.content.startswith('!set_descr'):
        await message.delete()

        splits = message.content.split(' ')
        if len(splits) < 3:
            await message.author.send("Wrong format:\n!set_descr <id> <descr>")
        else:
            if not await check_gamble_id(splits[1], message.channel):
                await message.author.send("Incorrect ID: '%s'" % splits[1])
            else:
                gamble_id = int(splits[1])
                gamble = bot.gambles[gamble_id]
                if message.author.id != gamble.admin:
                    await message.author.send("You're not admin of this gamble.")
                    return

                gamble_msg = await message.channel.fetch_message(gamble_id)
                descr = " ".join(splits[2:])
                gamble.set_descr(descr)
                await gamble_msg.edit(content=None, embed=gamble.createEmbed())

    elif message.content.startswith('!set_bid_value'):
        await message.delete()

        splits = message.content.split(' ')
        if len(splits) != 3:
            await message.author.send("Wrong format:\n!set_bid_value <id> <value>")
        else:
            if not await check_gamble_id(splits[1], message.channel):
                await message.author.send("Incorrect ID: '%s'" % splits[1])
            else:
                gamble_id = int(splits[1])
                gamble = bot.gambles[gamble_id]
                if message.author.id != gamble.admin:
                    await message.author.send("You're not admin of this gamble.")
                    return
                gamble_msg = await message.channel.fetch_message(gamble_id)

                value = 0
                try:
                    value = int(splits[2])
                except:
                    await message.author.send("Incorrect value: '%s'" % splits[2])
                    return

                gamble.set_bid_value(value)
                await gamble_msg.edit(content=None, embed=gamble.createEmbed())

    elif message.content.startswith('!add_choice'):
        await message.delete()

        splits = message.content.split(' ')
        if len(splits) < 3:
            await message.author.send("Wrong format:\n!add_choice <id> <choice>")
        else:
            if not await check_gamble_id(splits[1], message.channel):
                await message.author.send("Incorrect ID: '%s'" % splits[1])
            else:
                gamble_id = int(splits[1])
                gamble = bot.gambles[gamble_id]
                if message.author.id != gamble.admin:
                    await message.author.send("You're not admin of this gamble.")
                    return
                gamble_msg = await message.channel.fetch_message(gamble_id)

                choice = " ".join(splits[2:])
                emoji = gamble.add_choice(choice)
                await gamble_msg.edit(content=None, embed=gamble.createEmbed())
                await gamble_msg.add_reaction(emoji)

    elif message.content.startswith('!lock'):
        await message.delete()

        splits = message.content.split(' ')
        if len(splits) != 2:
            await message.author.send("Wrong format:\n!lock <id>")
        else:
            if not await check_gamble_id(splits[1], message.channel):
                await message.author.send("Incorrect ID: '%s'" % splits[1])
            else:
                gamble_id = int(splits[1])
                gamble = bot.gambles[gamble_id]
                if message.author.id != gamble.admin:
                    await message.author.send("You're not admin of this gamble.")
                    return

                gamble.lock()
                gamble_msg = await message.channel.fetch_message(gamble_id)
                await gamble_msg.edit(content=None, embed=gamble.createEmbed())

    elif message.content.startswith('!unlock'):
        await message.delete()

        splits = message.content.split(' ')
        if len(splits) != 2:
            await message.author.send("Wrong format:\n!unlock <id>")
        else:
            if not await check_gamble_id(splits[1], message.channel):
                await message.author.send("Incorrect ID: '%s'" % splits[1])
            else:
                gamble_id = int(splits[1])
                gamble = bot.gambles[gamble_id]
                if message.author.id != gamble.admin:
                    await message.author.send("You're not admin of this gamble.")
                    return

                gamble.unlock()
                gamble_msg = await message.channel.fetch_message(gamble_id)
                await gamble_msg.edit(content=None, embed=gamble.createEmbed())

    elif message.content.startswith('!winner'):
        await message.delete()

        splits = message.content.split(' ')
        if len(splits) != 3:
            await message.author.send("Wrong format:\n!winner <id> <choice_letter>")
        else:
            if not await check_gamble_id(splits[1], message.channel):
                await message.author.send("Incorrect ID: '%s'" % splits[1])
            else:
                gamble_id = int(splits[1])
                gamble = bot.gambles[gamble_id]
                if message.author.id != gamble.admin:
                    await message.author.send("You're not admin of this gamble.")
                    return

                if not gamble.get_emoji_from_letter(splits[2]):
                    await message.author.send("Incorrect letter: '%s'" % splits[2])
                else:
                    gamble.set_winner(splits[2])
                    gamble_msg = await message.channel.fetch_message(gamble_id)
                    await gamble_msg.edit(content=None, embed=gamble.createEmbed())

                    await gamble_msg.channel.send(embed=gamble.compute_transactions())

                    bot.gambles.pop(gamble_id, None)

    elif message.content.startswith('!set_title'):
        await message.delete()

        splits = message.content.split(' ')
        if len(splits) < 3:
            await message.author.send("Wrong format:\n!set_title <id> <new_gamble>")
        else:
            if not await check_gamble_id(splits[1], message.channel):
                await message.author.send("Incorrect ID: '%s'" % splits[1])
            else:
                gamble_id = int(splits[1])
                gamble = bot.gambles[gamble_id]
                if message.author.id != gamble.admin:
                    await message.author.send("You're not admin of this gamble.")
                    return

                gamble.set_title(" ".join(splits[2:]))
                gamble_msg = await message.channel.fetch_message(gamble_id)
                await gamble_msg.edit(content=None, embed=gamble.createEmbed())

    elif message.content.startswith('!edit_choice'):
        await message.delete()

        splits = message.content.split(' ')
        if len(splits) < 4:
            await message.author.send("Wrong format:\n!edit_choice <id> <choice_letter> <new_choice>")
        else:
            if not await check_gamble_id(splits[1], message.channel):
                await message.author.send("Incorrect ID: '%s'" % splits[1])
            else:
                gamble_id = int(splits[1])
                gamble = bot.gambles[gamble_id]
                if message.author.id != gamble.admin:
                    await message.author.send("You're not admin of this gamble.")
                    return

                if not gamble.get_emoji_from_letter(splits[2]):
                    await message.author.send("Incorrect letter: '%s'" % splits[2])
                else:
                    gamble.set_choice(splits[2], " ".join(splits[3:]))
                    gamble_msg = await message.channel.fetch_message(gamble_id)
                    await gamble_msg.edit(content=None, embed=gamble.createEmbed())


@bot.event
async def on_reaction_add(reaction, user):
    if not user.bot:
        msg = reaction.message
        if msg.id in bot.gambles:
            gamble = bot.gambles[msg.id]
            emoji = reaction.emoji
            if emoji in gamble.emojis():
                if not gamble.locked:
                    if gamble.add_bid(emoji, user.id, user.display_name):
                        gamble_msg = await msg.channel.fetch_message(msg.id)
                        await gamble_msg.edit(content=None, embed=gamble.createEmbed())
                        return
            await reaction.remove(user)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id in bot.gambles:
        gamble = bot.gambles[payload.message_id]
        emoji = str(payload.emoji)
        if emoji in gamble.emojis():
            if not gamble.locked:
                gamble.remove_bid(emoji, payload.user_id)
                channel = await bot.fetch_channel(payload.channel_id)
                gamble_msg = await channel.fetch_message(payload.message_id)
                await gamble_msg.edit(content=None, embed=gamble.createEmbed())

bot.run(os.getenv("DISCORD_BOT_PRIVATE_TOKEN"))
