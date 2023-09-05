from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `menu_items` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` LONGTEXT NOT NULL,
    `status` BOOL NOT NULL  DEFAULT 1,
    `level` INT NOT NULL  DEFAULT 1,
    `queue` LONGTEXT,
    `parent_id` BIGINT,
    CONSTRAINT `fk_menu_ite_menu_ite_98622c9d` FOREIGN KEY (`parent_id`) REFERENCES `menu_items` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `users` (
    `chat_id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `nickname` LONGTEXT NOT NULL,
    `fullname` LONGTEXT,
    `profession` LONGTEXT,
    `hints` BOOL NOT NULL  DEFAULT 1,
    `admin_id` BIGINT,
    CONSTRAINT `fk_users_users_6e07eb46` FOREIGN KEY (`admin_id`) REFERENCES `users` (`chat_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `admin_info` (
    `google_table_url` LONGTEXT NOT NULL,
    `admin_id` BIGINT NOT NULL  PRIMARY KEY,
    CONSTRAINT `fk_admin_in_users_9ee941e2` FOREIGN KEY (`admin_id`) REFERENCES `users` (`chat_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `notification_groups` (
    `chat_id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `admin_id` BIGINT,
    CONSTRAINT `fk_notifica_users_62ab5bc5` FOREIGN KEY (`admin_id`) REFERENCES `users` (`chat_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user_menu_item` (
    `users_id` BIGINT NOT NULL,
    `menuitem_id` BIGINT NOT NULL,
    FOREIGN KEY (`users_id`) REFERENCES `users` (`chat_id`) ON DELETE CASCADE,
    FOREIGN KEY (`menuitem_id`) REFERENCES `menu_items` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
