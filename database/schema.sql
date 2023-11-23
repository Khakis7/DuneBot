CREATE TABLE IF NOT EXISTS `user` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `discord_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  'name' varchar(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS `rating` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `user_id` int(11) NOT NULL,
  'rating' int(11) NOT NULL,
  'type' varchar(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS `match` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `played_timestamp` timestamp NOT NULL
);

CREATE TABLE IF NOT EXISTS `player` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `user_id` int(11) NOT NULL,
  `match_id` int(11) NOT NULL,
  `result` varchar(20) NOT NULL
);

