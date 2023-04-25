import math
import random
import sys
import time

import pygame as pg


delta = {  # 押下キーと移動量の辞書
    pg.K_UP: (0, -1),
    pg.K_DOWN: (0, +1),
    pg.K_LEFT: (-1, 0),
    pg.K_RIGHT: (+1, 0),
}


def init_kk_imgs() -> "dict[tuple[int, int], pg.Surface]":
    """
    移動量の合計値タプルをキー，対応する向きの画像Surfaceを値とした辞書を返す
    """
    kk_img0 = pg.transform.rotozoom(pg.image.load("ex02/fig/3.png"), 0, 2.0)
    kk_img = pg.transform.flip(kk_img0, True, False)  # デフォルトのこうかとん
    return {
        (+1, 0): kk_img,  # 右
        (+1, -1): pg.transform.rotozoom(kk_img, 45, 1.0),  # 右上
        (0, -1): pg.transform.rotozoom(kk_img, 90, 1.0),  # 上
        (-1, -1): pg.transform.rotozoom(kk_img0, -45, 1.0),  # 左上
        (-1, 0): kk_img0,  # 左
        (-1, +1): pg.transform.rotozoom(kk_img0, 45, 1.0),  # 左下
        (0, +1): pg.transform.rotozoom(kk_img, -90, 1.0),  # 下
        (+1, +1): pg.transform.rotozoom(kk_img, -45, 1.0),  # 右下
        }


def init_bb_imgs() -> "list[pg.Surface]":
    """
    サイズの異なる爆弾Surfaceを要素としたリストを返す
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    return bb_imgs


def check_bound(area: pg.Rect, obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数1 area：画面SurfaceのRect
    引数2 obj：オブジェクト（爆弾，こうかとん）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < area.left or area.right < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < area.top or area.bottom < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: "tuple[float, float]") -> "tuple[float, float]":
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    ただし，距離が500未満なら，慣性として前の移動方向current_xyを返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル（ノルムをsqrt(2)に正規化）
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    if norm < 500:
        return current_xy
    return x_diff/norm*math.sqrt(2), y_diff/norm*math.sqrt(2)


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((1600, 900))
    clock = pg.time.Clock()
    bg_img = pg.image.load("ex02/fig/pg_bg.jpg")
    kk_imgs = init_kk_imgs()
    kk_img = kk_imgs[(+1, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 900, 400

    bb_imgs = init_bb_imgs()
    bb_rct = bb_imgs[0].get_rect()
    bb_rct.center = random.randint(0, 1600), random.randint(0, 900)
    vx, vy = +1, +1
    accs = [a for a in range(1, 11)]  # 加速度リスト

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        tmr += 1
        screen.blit(bg_img, [0, 0])
        
        if kk_rct.colliderect(bb_rct):
            # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
            kk_img = pg.transform.rotozoom(pg.image.load("ex02/fig/8.png"), 0, 2.0)
            screen.blit(kk_img, kk_rct)
            pg.display.update()
            time.sleep(1)
            return

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for k, mv in delta.items():
            if key_lst[k]:
                kk_rct.move_ip(mv)
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(screen.get_rect(), kk_rct) != (True, True):
            for k, mv in delta.items():
                if key_lst[k]:
                    kk_rct.move_ip(-mv[0], -mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            kk_img = kk_imgs[tuple(sum_mv)]
        screen.blit(kk_img, kk_rct)

        yoko, tate = check_bound(screen.get_rect(), bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        avx, avy = vx*accs[min(tmr//2000, 9)], vy*accs[min(tmr//2000, 9)]
        bb_rct.move_ip(avx, avy)
        bb_img = bb_imgs[min(tmr//2000, 9)]
        bb_rct.width, bb_rct.height = bb_img.get_rect().width, bb_img.get_rect().height
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        clock.tick(1000)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()