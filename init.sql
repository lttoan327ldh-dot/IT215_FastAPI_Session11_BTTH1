CREATE DATABASE IF NOT EXISTS parking_db CHARACTER SET utf8mb4;
USE parking_db;

CREATE TABLE IF NOT EXISTS parking_slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slot_code VARCHAR(50) NOT NULL UNIQUE,
    zone_name VARCHAR(255) NOT NULL,
    max_weight INT NOT NULL,
    is_available TINYINT(1) NOT NULL DEFAULT 1
);

INSERT INTO parking_slots (slot_code, zone_name, max_weight, is_available) VALUES
('P-A-01', 'Khu vực xe máy', 300, 1),
('P-A-02', 'Khu vực xe máy', 300, 0),
('P-B-01', 'Khu vực xe 4 chỗ', 2000, 1);
