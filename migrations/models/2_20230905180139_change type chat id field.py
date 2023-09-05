from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `notification_groups` MODIFY COLUMN `admin_id` BIGINT;
        ALTER TABLE `users` MODIFY COLUMN `admin_id` BIGINT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` MODIFY COLUMN `admin_id` INT;
        ALTER TABLE `notification_groups` MODIFY COLUMN `admin_id` INT;"""
