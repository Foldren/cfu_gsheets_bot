from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `admin_info` ADD `gt_day_stat_url` LONGTEXT NOT NULL;
        ALTER TABLE `admin_info` ADD `gt_week_stat_url` LONGTEXT NOT NULL;
        ALTER TABLE `admin_info` ADD `gt_month_stat_url` LONGTEXT NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `admin_info` DROP COLUMN `gt_day_stat_url`;
        ALTER TABLE `admin_info` DROP COLUMN `gt_week_stat_url`;
        ALTER TABLE `admin_info` DROP COLUMN `gt_month_stat_url`;"""
