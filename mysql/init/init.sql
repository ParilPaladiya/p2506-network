-- MySQL Initialization Script for Sensor Data Storage

CREATE DATABASE IF NOT EXISTS sensor_db;
USE sensor_db;

-- Raw temperature data (Node-RED → MySQL)
CREATE TABLE IF NOT EXISTS temperature_data (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    device_id   VARCHAR(20)    NOT NULL,
    temperature DECIMAL(5, 2)  NOT NULL,
    timestamp   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- Alert data (Alert Manager → MySQL)
CREATE TABLE IF NOT EXISTS temperature_alerts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    timestamp   DATETIME       NOT NULL,
    device_id   VARCHAR(20)    NOT NULL,
    temperature DECIMAL(5, 2)  NOT NULL,
    alert_level VARCHAR(200)   NOT NULL
);

-- Indexes for faster Grafana queries
CREATE INDEX idx_td_device   ON temperature_data    (device_id, timestamp);
CREATE INDEX idx_ta_device   ON temperature_alerts  (device_id, timestamp);
