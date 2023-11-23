import re

from utils.constants import RESULT_TYPE, RATING_CHANGE_DEFAULTS, MMR_DIFFERENTIAL_DEFAULTS

MENTION = re.compile(r"<@!?(\d+)>\s*([^<]*)")

def _calculate_difference(a):
    b = a - 100
    count = 1
    if b <= 0:
        return b
    else:
        return _calculate_difference(b)


async def report_match(message, database):
    match = await database.create_match(message.created_at)
    print(match)
    winners_mmr = []
    losers_mmr = []
    all_players = []

    for line in message.content.split('\n'):
        line = line.strip()
        result = RESULT_TYPE.LOSE

        if line.startswith(RESULT_TYPE.WIN):
            result = RESULT_TYPE.WIN

        players = [discord_id for discord_id, _ in MENTION.findall(line)]

        for discord_id in players:
            user_profile = await database.get_user_profile(discord_id)
            await database.record_players_in_match(user_profile['id'], match, result)
            rating = await database.get_or_create_rating(user_profile['id'])

            if result == RESULT_TYPE.WIN:
                winners_mmr.append(rating['rating'])
            else:
                losers_mmr.append(rating['rating'])

            all_players.append({
                'user_profile': user_profile,
                'rating': rating,
                'result': result
            })
    
    average_winner_mmr = sum(winners_mmr)/len(winners_mmr)
    average_loser_mmr = sum(losers_mmr)/len(losers_mmr)

    mmr_difference = average_winner_mmr - average_loser_mmr

    difference_multipler = _calculate_difference(abs(mmr_difference))

    winner_rating_change = (difference_multipler * MMR_DIFFERENTIAL_DEFAULTS.WINNER)
    winner_rating_change = winner_rating_change + RATING_CHANGE_DEFAULTS.WINNER if average_winner_mmr > average_loser_mmr else  winner_rating_change - RATING_CHANGE_DEFAULTS.WINNER 
    
    loser_rating_change = (difference_multipler * MMR_DIFFERENTIAL_DEFAULTS.LOSER)
    loser_rating_change = loser_rating_change + RATING_CHANGE_DEFAULTS.LOSER if loser_rating_change > winner_rating_change else  loser_rating_change - RATING_CHANGE_DEFAULTS.LOSER 

    bot_message = 'Report Registered - Estimated Change in MMR\n'
    for idx, player in enumerate(all_players):
        if player['result'] == RESULT_TYPE.WIN:
            user_profile = player['user_profile']
            await database.update_rating(user_profile['id'], winner_rating_change, player['result'])
            bot_message = bot_message + f"{user_profile['user_name']}: Current Rating = {player['rating']['rating']}. Rating Change = {winner_rating_change}\n"
        else:
            await database.update_rating(user_profile['id'], loser_rating_change, player['result'])
            bot_message = bot_message + f"{user_profile['user_name']}: Current Rating = {player['rating']['rating']}. Rating Change = {loser_rating_change}\n"

    return all_players, bot_message