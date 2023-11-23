async def register_user(message, database):
    user = await database.get_user_profile(message.author.id)

    if user:
        return user, f"User is already successfully registered for ranked games!"
    else:
        user = await database.register_user(
            message.author.id, 
            message.guild.id, 
            message.author.name
        )
        
        bot_message = f"Registration Successful! User: {user['user_name']} has successfully registered for ranked matches."

        return user, bot_message