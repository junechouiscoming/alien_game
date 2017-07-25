import sys, pygame
from alien_game.bullet import Bullet
from alien_game.alien import Alien
from time import sleep

def check_keydown_events(event, ai_settings, screen, ship, bullets):
    '''响应按键'''
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()

def check_keyup_events(event, ship):
    '''响应松开'''
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def check_events(ai_settings, stats, screen, ship, bullets, aliens, play_button, sb):
    '''监视键盘和鼠标的事件'''
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, stats, screen, ship, bullets, aliens, play_button, sb, mouse_x, mouse_y)

def check_play_button(ai_settings, stats, screen, ship, bullets, aliens, play_button, sb, mouse_x, mouse_y):
    '''在玩家单击Play按钮时开始游戏'''
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        # 重置游戏的速度设置
        ai_settings.initialize_dynamic_settings()
        # 隐藏光标
        pygame.mouse.set_visible(False)
        if play_button.rect.collidepoint(mouse_x, mouse_y):
            # 重置游戏统计信息
            stats.reset_stats()
            stats.game_active = True

            # 重置记分牌图像
            sb.prep_score()
            sb.prep_high_score()
            sb.prep_level()
            sb.prep_ships()

            # 清空外星人列表和子弹
            aliens.empty()
            bullets.empty()

            # 创建新的外星人并让飞船居中
            create_fleet(ai_settings, screen, ship, aliens)
            ship.center_ship()

def fire_bullet(ai_settings, screen, ship, bullets):
    '''如果子弹没有达到限制，就再发射一颗子弹'''
    if len(bullets) < ai_settings.bullet_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)

def update_bullets(ai_settings, screen, ship, aliens, bullets, stats, sb):
    '''更新子弹的位置，并删除消失的子弹'''
    # 更新子弹位置
    bullets.update()
    # 删除已消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets, stats, sb)


def check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets, stats, sb):
    # 如果有子弹和外星人发生碰撞，就删除相应的外星人和子弹
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)
    if len(aliens) == 0:
        # 删除现有的子弹，加快游戏节奏并新建一群外星人
        bullets.empty()
        ai_settings.increase_speed()
        # 提高等级
        stats.level += 1
        sb.prep_level()

        create_fleet(ai_settings, screen, ship, aliens)

def get_number_alien_x(ai_settings, alien_width):
    '''计算每行可容纳多少外星人'''
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_alien_x = int(available_space_x / alien_width)
    return number_alien_x

def get_number_rows(ai_settings, ship_height, alien_height):
    '''计算屏幕可容纳多少行外星人'''
    available_space_y = ai_settings.screen_height - \
                        (3 * alien_height) - ship_height
    number_rows = int(available_space_y / (6 * alien_height))
    return number_rows

def create_alien(ai_settings, screen ,aliens, alien_number, row_number):
    '''创建一个外星人并将其放在当前行'''
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    # alien.rect.x = alien.rect.width + 2 * alien.rect.width * alien_number
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

def create_fleet(ai_settings, screen, ship, aliens):
    '''创建外星人群'''
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_alien_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    # 创建外星人群
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)

def check_fleet_edges(ai_settings, aliens):
    '''有外星人到达屏幕边缘时采取的措施'''
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break

def change_fleet_direction(ai_settings, aliens):
    '''将整群外星人下移，并改变他们的方向'''
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def update_aliens(ai_settings, stats, screen, ship, aliens, bullets, sb):
    '''检查是否有外星人位于屏幕边缘，并更新整群外星人的位置'''
    check_fleet_edges(ai_settings, aliens)
    # 检查是否有外星人到达屏幕低端
    check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets, sb)
    aliens.update()
    # 检测外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, ship, aliens, bullets, sb)

def ship_hit(ai_settings, stats, screen, ship, aliens, bullets, sb):
    '''响应被外星人撞击到的飞船'''
    if stats.ships_left > 0:
        stats.ships_left -= 1

        # 更新飞船显示数
        sb.prep_ships()

        # 清空外星人和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人并将飞船置于屏幕底部中央
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()
        sleep(1)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

def check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets, sb):
    '''检查是否有外星人到达屏幕低端'''
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # 像飞船被撞到一样处理
            ship_hit(ai_settings, stats, screen, ship, aliens, bullets, sb)
            break

def check_high_score(stats, sb):
    '''检查是否诞生了最高得分'''
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()

def update_screen(ai_settings, screen, stats, ship, bullets, aliens, play_button, sb):
    # 每次循环都会重新绘制屏幕
    screen.fill(ai_settings.bg_color)

    # 在飞船和外星人后面重新绘制所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    # 调用Ship类的draw_ship方法
    ship.draw_ship()
    # 对编组调用draw()，Pygame自动绘制编组中的每个元素
    aliens.draw(screen)
    sb.show_score()
    # 如果游戏处于非活跃状态，就绘制button
    if not stats.game_active:
        play_button.draw_button()

    # 让最近绘制的屏幕可见
    pygame.display.flip()