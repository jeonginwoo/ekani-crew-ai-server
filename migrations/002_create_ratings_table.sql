CREATE TABLE ratings (
    id VARCHAR(36) PRIMARY KEY,
    rater_id VARCHAR(255) NOT NULL,
    rated_user_id VARCHAR(255) NOT NULL,
    room_id VARCHAR(36) NOT NULL,
    score INTEGER NOT NULL,
    feedback TEXT,
    created_at DATETIME NOT NULL,
    INDEX idx_rater (rater_id),
    INDEX idx_rated_user (rated_user_id),
    INDEX idx_room (room_id),
    FOREIGN KEY (rater_id) REFERENCES users(id),
    FOREIGN KEY (rated_user_id) REFERENCES users(id),
    FOREIGN KEY (room_id) REFERENCES chat_rooms(id)
);
