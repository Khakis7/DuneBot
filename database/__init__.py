import aiosqlite

from utils.constants import RATING_TYPE, RESULT_TYPE

class DatabaseManager:
    def __init__(self, *, connection: aiosqlite.Connection) -> None:
        self.connection = connection

    async def register_user(self, discord_id, server_id, user_name):
        await self.connection.execute(
            "insert into user (discord_id, server_id, name) VALUES (?, ?, ?)",
            (
                str(discord_id),
                str(server_id),
                str(user_name),
            ),
        )
        await self.connection.commit()
        
        return {
            'discord_id': discord_id,
            'server_id': server_id,
            'user_name': user_name
        }

    async def get_user_profile(self, discord_id):
        rows = await self.connection.execute(
            "SELECT * FROM user where discord_id = ?",
            (str(discord_id),)
        )
        async with rows as cursor:
            result = await cursor.fetchone()

            if not result:
                return None

            return {
                'id': result[0],
                'discord_id': result[1],
                'server_id': result[2],
                'user_name': result[3]
            }

    async def create_match(self, played_timestamp):
        await self.connection.execute(
            "insert into match (played_timestamp) VALUES (?)",
            (
                played_timestamp,
            ),
        )
        await self.connection.commit()
        
        rows = await self.connection.execute(
            "select id from match where played_timestamp = ?",
            (played_timestamp,)
        )
        async with rows as cursor:
            result = await cursor.fetchone()

            return {
                'id': result[0],
                'played_timestamp': played_timestamp
            }
 
    async def record_players_in_match(self, user_id, match, result):
        await self.connection.execute(
            """
            insert into player (user_id, match_id, result) VALUES (?, ?, ?)
            """,
            (
                int(user_id),
                int(match['id']),
                str(result)
            ),
        )
        await self.connection.commit()
    
        return

    async def get_or_create_rating(self, user_id):
        rows = await self.connection.execute(
            """
            select * from rating where user_id = ?
            """,
            (user_id,)
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'user_id': result[1],
                    'rating': result[2],
                    'type': result[3]
                }
            else:
                await self.connection.execute(
                    "insert into rating (user_id, rating, type) VALUES (?, ?, ?)",
                    (
                        int(user_id),
                        200,
                        RATING_TYPE.FFA
                    ),
                )
                await self.connection.commit()
                
                return {
                    'user_id': user_id,
                    'rating': 200,
                    'type': RATING_TYPE.FFA
                }

    async def update_rating(self, user_id, rating_change, result):
        if result == RESULT_TYPE.WIN:
            sql = "update rating set rating = rating + ? where user_id = ?"
        else:
            sql = "update rating set rating = rating - ? where user_id = ?"

        operator = '+' if result == RESULT_TYPE.WIN else '-'
        await self.connection.execute(
            sql,
            (int(rating_change),int(user_id)),
        )
        await self.connection.commit()
        
        return