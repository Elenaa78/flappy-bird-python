import pygame
import random
import sys
import sqlite3


def baza():
    conn = sqlite3.connect("wyniki.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wyniki (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            punkty INTEGER
        )
    """)
    conn.commit()
    conn.close()    

def dodaj_wynik(punkty):
    conn = sqlite3.connect("wyniki.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO wyniki (punkty) VALUES (?)", (punkty,))
    conn.commit()
    conn.close()

def najlepszy():
    conn = sqlite3.connect("wyniki.db")
    cursor=conn.cursor()
    cursor.execute("SELECT punkty FROM wyniki ORDER BY punkty DESC LIMIT 1")
    wynik = cursor.fetchone()
    conn.close()
    return wynik[0] if wynik else "BRAK"


pygame.init()
baza()

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
background = pygame.image.load("/chmury.jpg").convert()
background = pygame.transform.scale(background, (800, 800))
background_x = 0

running = True
dt = 0
przerwa = 170
predkosc = 250
szerokosc = 85

przycisk = pygame.Rect(screen.get_width() // 2 - 100,  screen.get_height() // 2 - 30, 200, 60)

font = pygame.font.SysFont('Arial', 30)

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

bird = pygame.image.load("/bird.png").convert_alpha()

rury = []

najlepszy_wynik = najlepszy()

def okno():
    background2 = pygame.image.load("/menu.png").convert()
    background2 = pygame.transform.scale(background2, (800, 800))
    screen.blit(background2, (0, 0))
    global najlepszy_wynik, player_pos
    najlepszy_wynik = najlepszy()
    player_pos.y = screen.get_height() / 2

    pygame.draw.rect(screen, 'gray', przycisk)
    text = font.render("START", True, 'black')
    text_rect = text.get_rect(center=przycisk.center)
    screen.blit(text, text_rect)

    rekord = font.render(f"NAJLEPSZY WYNIK: {najlepszy_wynik}", True, 'black')
    screen.blit(rekord, (40, 30))

    pygame.display.flip()


def pokaz_rury():
    top_height = random.randint(100, 500)
    bottom_y = top_height + przerwa
    top_rect = pygame.Rect(800, 0, szerokosc, top_height)
    bottom_rect = pygame.Rect(800, bottom_y, szerokosc, 800 - bottom_y)
    return [top_rect, bottom_rect, False] 

rury.append(pokaz_rury())

opadanie = 0
prędkość_opadania = 660
prędkość_skoku = -330

koniec = False

def gra():
    global screen, clock, background, background_x, running, dt, przerwa, predkosc, szerokosc, font ,player_pos, rury, opadanie, prędkość_opadania , prędkość_skoku, bird, koniec
    punkty = 0
    dt = 0 
    opadanie = 0
    koniec = False
    player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    rury = []
    rury.append(pokaz_rury())
    clock.tick(60)
    while running:
        background_x -= 100 * dt
        if background_x <= -800:
            background_x = 0

        screen.blit(background, (background_x, 0))
        screen.blit(background, (background_x + 800, 0))

        text2 = font.render(f'WYNIK: {punkty} ', True, (0, 0, 0))
        screen.blit(text2, (80, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_SPACE]:
            opadanie = prędkość_skoku

        opadanie += prędkość_opadania * dt
        player_pos.y += opadanie * dt


        if player_pos.y < 0 or player_pos.y >screen.get_height():
            dodaj_wynik(punkty)
            najlepszy_wynik = najlepszy()
            screen.fill('white')
            text_game_over = font.render("GAME OVER", True, (255, 0, 0))
            twoj_wynik = font.render(f"TWOJ WYNIK: {punkty}", True, 'black')
            screen.blit(text_game_over, (300, 300))
            screen.blit(twoj_wynik, (300, 400))
            pygame.display.flip()
            pygame.time.wait(4000)
            return



        screen.blit(bird, player_pos)
        bird_rect = pygame.Rect(player_pos.x, player_pos.y, bird.get_width(), bird.get_height())

        kolizja = False

        for rura in rury:
            top_rect, bottom_rect, punkty_naliczone = rura
            top_rect.x -= predkosc * dt
            bottom_rect.x -= predkosc * dt
            pygame.draw.rect(screen,  (128, 128, 128), top_rect)
            pygame.draw.rect(screen,  (128, 128, 128), bottom_rect)

            if bird_rect.x >= top_rect.x and not punkty_naliczone:
                if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                    koniec=True
                else:
                    punkty += 10
                    rura[2] = True


        nowe_rury = []
        for rura in rury:
            if rura[0].x + szerokosc > 0:
                nowe_rury.append(rura)
        rury = nowe_rury


        if len(rury) > 0 and rury[-1][0].x < 400:
            rury.append(pokaz_rury())

        if koniec == True:
            dodaj_wynik(punkty)
            najlepszy_wynik = najlepszy()
            screen.fill('white')
            text_game_over = font.render("GAME OVER", True, (255, 0, 0))
            twoj_wynik = font.render(f"TWOJ WYNIK: {punkty}", True, 'black')
            screen.blit(text_game_over, (300, 300))
            screen.blit(twoj_wynik, (300, 400))
            pygame.display.flip()
            pygame.time.wait(2500)
            return

        pygame.display.flip()

        dt = clock.tick(60) / 1000


menu=True
while menu:
    okno()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if przycisk.collidepoint(event.pos):
                gra()

pygame.quit()
