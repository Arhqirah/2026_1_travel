

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";



CREATE TABLE `destinations` (
  `destination_pk` char(32) NOT NULL,
  `destination_user_fk` char(32) NOT NULL,
  `destination_title` varchar(100) NOT NULL,
  `destination_country` varchar(100) NOT NULL,
  `destination_start_date` date DEFAULT NULL,
  `destination_end_date` date DEFAULT NULL,
  `destination_description` varchar(500) NOT NULL,
  `destination_image_name` varchar(255) NOT NULL DEFAULT '',
  `destination_created_at` bigint(20) UNSIGNED NOT NULL,
  `destination_updated_at` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE `users` (
  `user_pk` char(32) NOT NULL,
  `user_first_name` varchar(20) NOT NULL,
  `user_last_name` varchar(20) NOT NULL,
  `user_email` varchar(100) NOT NULL,
  `user_password` varchar(255) NOT NULL,
  `user_created_at` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE `destinations`
  ADD PRIMARY KEY (`destination_pk`),
  ADD KEY `destination_user_fk` (`destination_user_fk`);


ALTER TABLE `users`
  ADD PRIMARY KEY (`user_pk`),
  ADD UNIQUE KEY `user_email` (`user_email`);


ALTER TABLE `destinations`
  ADD CONSTRAINT `destinations_ibfk_1` FOREIGN KEY (`destination_user_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE;
COMMIT;
