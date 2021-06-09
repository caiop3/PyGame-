import pygame
from reference import load_assets, IMAGE, MUSIC, LIFE_FONT, SCORE_FONT, LIVES_FONT, EAGLE_SOUND, BOOM_SOUND, PLAYER_SHEET
from sprites import Covid, Balao, Life, Eagle1, Eagle2, Gel, load_spritesheet, Player
from data import WIDTH, HEIGHT, FPS

# --- Cria um grupo de sprites geral e para cada obstáculo
def game_screen(window):

    assets = load_assets()
    
    move_image_1 = 0
    move_image_2 = HEIGHT

    all_sprites = pygame.sprite.Group()
    aguias = pygame.sprite.Group()
    covides = pygame.sprite.Group()
    gels = pygame.sprite.Group()

    groups = {}
    groups['all_sprites'] = all_sprites
    groups['aguias'] = aguias
    groups['covides'] = covides
    groups['gels'] = gels
    
    score = 0
    lives = 3
    init_balife = 5
    covid_lives = 3
    keys_down = {}

    # lives_text = assets[LIFE_FONT].render('{:04d}'.format(lives), True, (255, 0, 0))
    # lives_text = pygame.transform.scale(lives_text, (20, 20))
    # text_rect_l = lives_text.get_rect()

    # --- Cria o jogador (balão)
    balao = Balao(groups, assets, init_balife)
    all_sprites.add(balao)

    balloon_life = Life(balao, assets)
    all_sprites.add(balloon_life)

    # --- Cria as covides
    covid = Covid(assets)
    all_sprites.add(covid)
    covides.add(covid)

    # --- Cria as águias e suas quantidades 
    for i in range(12):
        eagle1 = Eagle1(assets)
        eagle2 = Eagle2(assets)
        all_sprites.add(eagle1)
        all_sprites.add(eagle2)
        aguias.add(eagle1)
        aguias.add(eagle2)

    # --- Variável para o ajuste da velocidade
    clock = pygame.time.Clock()

    DONE = 0
    PLAYING = 1
    EXPLODING = 2
    state = PLAYING

    # ===== LOOP PRRINCIPAL =====    
    assets[MUSIC].play(loops=-1)
    while state != DONE:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = DONE
            
            if state == PLAYING:
            # Verifica se apertou alguma tecla
                if event.type == pygame.KEYDOWN: # Dependendo da tecla, altera a velocidade  
                    
                    keys_down[event.key] = True
                    if event.key == pygame.K_LEFT:
                        balao.speedx -= 5
                        # balloon_life.speedx -= 5
                    if event.key == pygame.K_RIGHT:
                        balao.speedx += 5
                        # balloon_life.speedx += 5
                    if event.key == pygame.K_UP:
                        balao.speedy -= 3.5
                        # balloon_life.speedy -= 3.5
                    if event.key == pygame.K_DOWN:
                        balao.speedy += 3.5
                        # balloon_life.speedy += 3.5
                    if event.key == pygame.K_SPACE: # Atira álcool em gel
                        balao.shoot()
                # Verifica se soltou alguma tecla
                if event.type == pygame.KEYUP: # Dependendo da tecla, altera a velocidade
                    
                    if event.key in keys_down and keys_down[event.key]:
                        if event.key == pygame.K_LEFT:
                            balao.speedx += 5
                            # balloon_life.speedx += 5
                        if event.key == pygame.K_RIGHT:
                            balao.speedx -= 5
                            # balloon_life.speedx -= 5
                        if event.key == pygame.K_UP:
                            balao.speedy += 3.5
                            # balloon_life.speedy += 3.5
                        if event.key == pygame.K_DOWN:
                            balao.speedy -= 3.5
                            # balloon_life.speedy -= 3.5

        # --- Atualiza os sprites
        all_sprites.update()
        #aguias.update()

        if state == PLAYING:
        # --- Trata colisões
            col_1 = pygame.sprite.spritecollide(balao, aguias, True, pygame.sprite.collide_mask)
            for aguia in col_1:
                balao.lives -= 1
                score -= 50
                if aguia == eagle1:
                    eagle1 = Eagle1(assets)
                    all_sprites.add(eagle1)
                    aguias.add(eagle1)  
                elif aguia == eagle2:
                    eagle2 = Eagle2(assets)
                    all_sprites.add(eagle2) 
                    aguias.add(eagle2)

            if len(col_1) > 0:
                assets[EAGLE_SOUND].play()
                if balao.lives == 0:
                    lives -= 1
                    balloon_life.kill()
                    balao.kill()
                    assets[BOOM_SOUND].play()
                    player = Player(balao.rect.center, assets['player_sheet'])
                    all_sprites.add(player)
                    state = EXPLODING
                    keys_down = {}
                    explosion_tick = pygame.time.get_ticks()
                    explosion_duration = player.frame_ticks * len(player.animation) + 500
            
            col_2 = pygame.sprite.spritecollide(balao, covides, True, pygame.sprite.collide_mask)
            for covid in col_2:
                covid = Covid(assets)
                all_sprites.add(covid)
                covides.add(covid)
                balao.lives -= 2
                score -= 100

            col_3 = pygame.sprite.spritecollide(covid, gels, True, pygame.sprite.collide_mask)
            for gel in col_3:
                covid_lives -= 1
                if covid_lives == 0:
                    covid.kill()
                    covid = Covid(assets)
                    all_sprites.add(covid)
                    covides.add(covid)
                    covid_lives = 3
                    balao.lives += 3
                    score += 200  

        elif state == EXPLODING:
            assets[MUSIC].stop()
            now = pygame.time.get_ticks()
            if now - explosion_tick > explosion_duration:
                if lives == 0:
                    state = DONE
                else:
                    state = PLAYING
                    assets[MUSIC].play()
                    balao = Balao(groups, assets, init_balife)
                    all_sprites.add(balao)
                    balloon_life = Life(balao, assets)
                    all_sprites.add(balloon_life)

        # --- Saídas
        window.fill((0, 0, 0)) # Preenche com a cor branca
        window.blit(assets[IMAGE], (0,move_image_1)) 
        window.blit(assets[IMAGE], (0,move_image_2)) 

        # Muda as posições da imagem de fundo
        move_image_1 -= 2
        move_image_2 -= 2

        # Plota novamente após sair da tela
        if move_image_1 <= -HEIGHT:
            move_image_1 = HEIGHT
        if move_image_2 <= -HEIGHT:
            move_image_2 = HEIGHT

        # Desenha todos os sprites
        all_sprites.draw(window)

        # lives_text = assets[LIFE_FONT].render('{:04d}'.format(lives), True, (255, 0, 0))

        text_surface = assets[SCORE_FONT].render("{:08d}".format(score), True, (0, 0, 255))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (WIDTH / 2,  0)
        window.blit(text_surface, text_rect)

        text_surface = assets[LIVES_FONT].render(chr(9829) * lives, True, (255, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.bottomleft = (10, HEIGHT - 10)
        window.blit(text_surface, text_rect)

        pygame.display.update()  # Mostra o novo frame para o jogador

