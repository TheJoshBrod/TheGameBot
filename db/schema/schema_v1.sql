PRAGMA foreign_keys = ON;

-- Servers Table
CREATE TABLE servers(
  ConversationID  INTEGER PRIMARY KEY AUTOINCREMENT,
  GuildID BIGINT,
  GuildName TEXT,
  ChannelID BIGINT,
  ChannelName TEXT,
  ChannelType BOOL NOT NULL,
  LastMessageTime INT,
  Status INT,
  LastMessageSent BIGINT,
  UNIQUE (GuildID, ChannelID)
);

-- Messages Table
CREATE TABLE messages(
  messageID INTEGER PRIMARY KEY NOT NULL,
  content TEXT,
  author_id INTEGER,
  timestamp INT,
  ConversationID INTEGER,
  FOREIGN KEY (ConversationID) REFERENCES servers(ConversationID) ON DELETE CASCADE
);
