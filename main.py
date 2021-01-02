"""
Copyright 2020 ibx34

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import aiohttp
import aioredis
import asyncpg
import discord
from discord.ext import commands

import textwrap
import config
import pymongo

class owo(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_pre,
            case_insensitive=True,
            reconnect=True,
            status=discord.Status.idle,
            intents=discord.Intents(
                messages=True,
                guilds=True,
                members=True,
                guild_messages=True,
                dm_messages=True,
                reactions=True,
                guild_reactions=True,
                dm_reactions=True,
                voice_states=True,
                presences=True,
            ),
        )
        self.config = config
        self.session = None
        self.pool = None
        self.redis = None
        self.used = 0
        self.chains = {}

    async def get_pre(self, bot, message):

        return commands.when_mentioned_or(*config.prefix)(bot, message)

    async def start(self):
        self.session = aiohttp.ClientSession(loop=self.loop)

        await super().start(config.token)

    async def on_ready(self):

        self.guild = self.get_guild(config.home_guild)

        print(f"(!) Bot started. Guilds: {len(self.guilds)} Users: {len(self.users)}")

    async def on_message(self, message):

        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if ctx.command:
            await self.process_commands(message, ctx)

        if message.channel.id != config.chain_channel:
            return

        if not self.chains:
            self.chains = {"author": message.author.id, "channel": message.channel.id, "phrase": message.content.lower(), "count": 0}
        elif message.content.lower() != self.chains['phrase'] and message.channel.id == self.chains["channel"] and self.chains['count'] > 2: 
            await message.channel.send(textwrap.dedent(f"""
            **Wow!** {message.author.mention} just ruined a chain!

            Message: ```{self.chains['phrase']}```
            Author: {self.chains['author']}
            """))
            self.chains.clear()
        else: #
            if message.content.lower() == self.chains['phrase'] and message.channel.id == self.chains["channel"]:
                self.chains['count'] += 1

    async def process_commands(self, message, ctx):

        if ctx.command is None:
            return

        self.used += 1
        await self.invoke(ctx)
        print(f"[I] Command ran. User: {ctx.author} ({ctx.author.id}). Channel: {ctx.channel} ({ctx.channel.id}). Guild: {ctx.guild} ({ctx.guild.id}). Content: {message.content}")


if __name__ == "__main__":
    owo().run()
