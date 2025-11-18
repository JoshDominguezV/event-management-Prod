-- Crear base de datos
CREATE DATABASE IF NOT EXISTS event_management;
USE event_management;

-- Tablas
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE social_auth (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    provider VARCHAR(50) NOT NULL,
    provider_id VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_provider (provider, provider_id)
);

CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    date DATETIME NOT NULL,
    location VARCHAR(200) NOT NULL,
    max_participants INT,
    organizer_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (organizer_id) REFERENCES users(id)
);

CREATE TABLE event_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    attended BOOLEAN DEFAULT FALSE,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    UNIQUE KEY unique_attendance (user_id, event_id)
);

CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    content TEXT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);

CREATE TABLE event_shares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    share_type ENUM('social_media', 'email') NOT NULL,
    recipient VARCHAR(255),
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id)
);

-- PROCEDIMIENTOS ALMACENADOS

-- Usuarios
DELIMITER //

CREATE PROCEDURE CreateUser(
    IN p_username VARCHAR(50),
    IN p_email VARCHAR(100),
    IN p_full_name VARCHAR(100),
    IN p_password_hash VARCHAR(255)
)
BEGIN
    INSERT INTO users (username, email, full_name, password_hash)
    VALUES (p_username, p_email, p_full_name, p_password_hash);
    SELECT LAST_INSERT_ID() as user_id;
END //

CREATE PROCEDURE GetUserByUsername(IN p_username VARCHAR(50))
BEGIN
    SELECT id, username, email, full_name, password_hash, created_at
    FROM users
    WHERE username = p_username AND is_active = TRUE;
END //

CREATE PROCEDURE GetUserById(IN p_user_id INT)
BEGIN
    SELECT id, username, email, full_name, created_at
    FROM users
    WHERE id = p_user_id AND is_active = TRUE;
END //

-- Eventos
CREATE PROCEDURE CreateEvent(
    IN p_title VARCHAR(200),
    IN p_description TEXT,
    IN p_date DATETIME,
    IN p_location VARCHAR(200),
    IN p_max_participants INT,
    IN p_organizer_id INT
)
BEGIN
    INSERT INTO events (title, description, date, location, max_participants, organizer_id)
    VALUES (p_title, p_description, p_date, p_location, p_max_participants, p_organizer_id);
    SELECT LAST_INSERT_ID() as event_id;
END //

CREATE PROCEDURE GetEventById(IN p_event_id INT)
BEGIN
    SELECT e.*, u.username as organizer_name, u.full_name as organizer_full_name
    FROM events e
    JOIN users u ON e.organizer_id = u.id
    WHERE e.id = p_event_id AND e.is_active = TRUE;
END //

CREATE PROCEDURE GetUpcomingEvents()
BEGIN
    SELECT e.*, u.username as organizer_name, u.full_name as organizer_full_name
    FROM events e
    JOIN users u ON e.organizer_id = u.id
    WHERE e.date >= NOW() AND e.is_active = TRUE
    ORDER BY e.date ASC;
END //

CREATE PROCEDURE GetPastEvents()
BEGIN
    SELECT e.*, u.username as organizer_name, u.full_name as organizer_full_name
    FROM events e
    JOIN users u ON e.organizer_id = u.id
    WHERE e.date < NOW() AND e.is_active = TRUE
    ORDER BY e.date DESC;
END //

CREATE PROCEDURE UpdateEvent(
    IN p_event_id INT,
    IN p_title VARCHAR(200),
    IN p_description TEXT,
    IN p_date DATETIME,
    IN p_location VARCHAR(200),
    IN p_max_participants INT
)
BEGIN
    UPDATE events
    SET title = COALESCE(p_title, title),
        description = COALESCE(p_description, description),
        date = COALESCE(p_date, date),
        location = COALESCE(p_location, location),
        max_participants = COALESCE(p_max_participants, max_participants)
    WHERE id = p_event_id;
END //

CREATE PROCEDURE DeleteEvent(IN p_event_id INT)
BEGIN
    UPDATE events SET is_active = FALSE WHERE id = p_event_id;
END //

-- Asistencia a eventos
CREATE PROCEDURE RegisterAttendance(
    IN p_user_id INT,
    IN p_event_id INT
)
BEGIN
    INSERT INTO event_attendance (user_id, event_id)
    VALUES (p_user_id, p_event_id)
    ON DUPLICATE KEY UPDATE attended = TRUE;
END //

CREATE PROCEDURE GetEventAttendees(IN p_event_id INT)
BEGIN
    SELECT u.id, u.username, u.full_name, ea.registered_at, ea.attended
    FROM event_attendance ea
    JOIN users u ON ea.user_id = u.id
    WHERE ea.event_id = p_event_id;
END //

-- Comentarios y calificaciones
CREATE PROCEDURE CreateComment(
    IN p_user_id INT,
    IN p_event_id INT,
    IN p_content TEXT,
    IN p_rating INT
)
BEGIN
    INSERT INTO comments (user_id, event_id, content, rating)
    VALUES (p_user_id, p_event_id, p_content, p_rating);
    SELECT LAST_INSERT_ID() as comment_id;
END //

CREATE PROCEDURE GetEventComments(IN p_event_id INT)
BEGIN
    SELECT c.*, u.username, u.full_name
    FROM comments c
    JOIN users u ON c.user_id = u.id
    WHERE c.event_id = p_event_id
    ORDER BY c.created_at DESC;
END //

-- Compartición de eventos
CREATE PROCEDURE LogEventShare(
    IN p_event_id INT,
    IN p_share_type VARCHAR(20),
    IN p_recipient VARCHAR(255)
)
BEGIN
    INSERT INTO event_shares (event_id, share_type, recipient)
    VALUES (p_event_id, p_share_type, p_recipient);
END //

-- Estadísticas
CREATE PROCEDURE GetUserEventStats(IN p_user_id INT)
BEGIN
    SELECT
        (SELECT COUNT(*) FROM event_attendance WHERE user_id = p_user_id) as events_registered,
        (SELECT COUNT(*) FROM event_attendance WHERE user_id = p_user_id AND attended = TRUE) as events_attended,
        (SELECT COUNT(*) FROM events WHERE organizer_id = p_user_id) as events_organized;
END //

CREATE PROCEDURE GetEventStatistics(IN p_event_id INT)
BEGIN
    SELECT
        e.title,
        e.date,
        e.location,
        (SELECT COUNT(*) FROM event_attendance WHERE event_id = p_event_id) as total_registered,
        (SELECT COUNT(*) FROM event_attendance WHERE event_id = p_event_id AND attended = TRUE) as total_attended,
        (SELECT AVG(rating) FROM comments WHERE event_id = p_event_id) as average_rating,
        (SELECT COUNT(*) FROM comments WHERE event_id = p_event_id) as total_comments,
        (SELECT COUNT(*) FROM event_shares WHERE event_id = p_event_id) as total_shares
    FROM events e
    WHERE e.id = p_event_id;
END //

DELIMITER ;