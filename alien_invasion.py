import pygame, sys
from alien_game.settings import Settings
from alien_game.ship import Ship
import alien_game.game_functions as gf
from pygame.sprite import Group
from alien_game.game_stats import GameStats
from alien_game.button import Button
from alien_game.scoreboard import Scoreboard


def run_game():
    # 初始化游戏并创建一个屏幕对象
    ai_settings = Settings()
    screen = pygame.display.set_mode(
        (ai_settings.screen_height, ai_settings.screen_width)
    )

    # 创建Play按钮
    play_button = Button(ai_settings, screen, 'Play')
    # 创建一艘飞船
    ship = Ship(ai_settings, screen)
    # 创建一个用于存储子弹的编组
    bullets = Group()
    # 创建一个外星人编组
    aliens = Group()
    # 创建外星人群
    gf.create_fleet(ai_settings, screen, ship, aliens)
    # 创建一个用于存储游戏统计信息的实例
    stats = GameStats(ai_settings)
    # 创建记分牌
    sb = Scoreboard(ai_settings, screen, stats)

    # 开始游戏的主循环
    while True:
        gf.check_events(ai_settings, stats, screen, ship, bullets, aliens, play_button, sb)
        if stats.game_active:
            ship.update()
            gf.update_bullets(ai_settings, screen, ship, aliens, bullets, stats, sb)
            gf.update_aliens(ai_settings, stats, screen, ship, aliens, bullets, sb)

        gf.update_screen(ai_settings, screen, stats, ship, bullets, aliens, play_button, sb)


run_game()