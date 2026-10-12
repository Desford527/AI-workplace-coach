CREATE TABLE `documents` (
	`owner` text NOT NULL,
	`key` text NOT NULL,
	`payload` text NOT NULL,
	`revision` integer DEFAULT 1 NOT NULL,
	`updated` text NOT NULL,
	PRIMARY KEY(`owner`, `key`)
);
