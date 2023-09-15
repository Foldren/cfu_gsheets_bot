from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `periods_stats` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` LONGTEXT NOT NULL
) CHARACTER SET utf8mb4;
        CREATE TABLE `user_period_stat` (
    `users_id` BIGINT NOT NULL REFERENCES `users` (`chat_id`) ON DELETE CASCADE,
    `periodstat_id` BIGINT NOT NULL REFERENCES `periods_stats` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `user_period_stat`;
        DROP TABLE IF EXISTS `periods_stats`;"""
