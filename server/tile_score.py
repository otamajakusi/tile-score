from mahjong.hand_calculating.hand import HandCalculator
from mahjong.meld import Meld
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.tile import TilesConverter as tc
from mahjong.utils import is_chi, is_pon, is_honor
from enum import IntEnum

MAX_TILE_NUM = 4 * 4 + 2
MIN_TILE_NUM = 3 * 4 + 2


class TileId(IntEnum):
    # BACK
    BACK = 99
    # MAN
    MAN1 = 0
    MAN2 = 1
    MAN3 = 2
    MAN4 = 3
    MAN5 = 4
    MAN6 = 5
    MAN7 = 6
    MAN8 = 7
    MAN9 = 8
    # PIN
    PIN1 = 9
    PIN2 = 10
    PIN3 = 11
    PIN4 = 12
    PIN5 = 13
    PIN6 = 14
    PIN7 = 15
    PIN8 = 16
    PIN9 = 17
    # SOU
    SOU1 = 18
    SOU2 = 19
    SOU3 = 20
    SOU4 = 21
    SOU5 = 22
    SOU6 = 23
    SOU7 = 24
    SOU8 = 25
    SOU9 = 26
    # TON,NAN,SHA,PEI
    TON = 27
    NAN = 28
    SHA = 29
    PEI = 30
    # HAKU,HATSU,CHUN
    HAKU = 31
    HATSU = 32
    CHUN = 33


def score(boxes, tsumo, y_divider, round_wind=None, player_wind=None):
    """
    +---------------+
    |  _ _ _ _   _  |
    | |_|_|_|_| |_| | classfied to `open`
    |               |
    |---------------| <- y_divider
    |  _ _ _ _ _ _  |
    | |_|_|_|_|_|_| | classfied to `closed`
    |               |
    +---------------+
    boxes:
      array of box which elements are: tile id, xmin, ymin, xmax and ymax.
      e.g. [[0, 100, 200, 150, 250],
            [2, 200, 300, 350, 350],
            [...]]
      the right most of the tile is assumed as win tile, and ron or tsumo is specified by tsumo.
      tile id is:
        man1...man9: 0...8
        pin1...pin9: 9...17
        sou1...sou9: 18...26
        ton, nan, sha, pei: 27, 28, 29, 30
        haku, hatsu, chun: 31, 32, 33
    y_divider:
      tiles are divided into two types; open or closed.
      if the position is upper than y_divider, the tile is classfied as open.
    """
    open_boxes, win_box, closed_boxes = classify_boxes(boxes, y_divider)
    if open_boxes is None:
        return None

    melds = make_melds(open_boxes)
    if melds is None:
        return None

    # 4-tile-set of kan should be trimed to 3-tile-set.
    open_kan = [x.tiles_34[0] for x in melds if x.type == Meld.KAN and x.opened]
    open_tiles = boxes_to_tiles(open_boxes, open_kan)
    if open_tiles is None:
        return None

    win_tile = boxes_to_tiles([win_box])
    if win_tile is None:
        return None

    closed_kan_melds, closed_boxes_replaced = make_closed_kan_melds(closed_boxes)

    # 4-tile-set of kan should be trimed to 3-tile-set.
    closed_kan = [x.tiles_34[0] for x in closed_kan_melds]
    closed_tiles = boxes_to_tiles(closed_boxes_replaced, closed_kan)
    if closed_tiles is None:
        return None

    hand = closed_tiles + open_tiles + win_tile
    print("win:\n", tc.to_one_line_string(win_tile))
    print("hand:\n", tc.to_one_line_string(hand))
    print("melds:\n", melds + closed_kan_melds)
    for meld in melds:
        print(tc.to_one_line_string(meld.tiles))

    options = OptionalRules(has_open_tanyao=True, kazoe_limit=HandConfig.KAZOE_NO_LIMIT)
    config = HandConfig(
        is_tsumo=tsumo, player_wind=player_wind, round_wind=round_wind, options=options,
    )
    print("tsumo:", tsumo, " player:", player_wind, " round:", round_wind)

    result = HandCalculator().estimate_hand_value(
        hand, win_tile[0], melds=melds + closed_kan_melds, config=config
    )
    print_hand_result(result)
    return result


def make_melds(open_boxes):
    melds = []
    pos = 0
    rest = len(open_boxes)
    while rest > 0:
        boxes = open_boxes[pos:]
        """
        3: (3)
        4: (4)
        6: (3 3)
        7: (4 3 | 3 4)
        8: (4 4)
        9: (3 3 3)
        *10: (4 3 3 | 3 4 3 | 3 3 4) 5555678888
        11: (4 4 3 | 4 3 4 | 3 4 4) 5555678
        12: (3 3 3 3 | 4 4 4) 111123456789
        *13: (4 3 3 3 | 3 4 3 3 | 3 3 4 3 | 3 3 3 4)
        *14: (4 4 3 3 | 4 3 4 3 | 4 3 3 4 | 3 4 4 3 | 3 4 3 4 | 3 3 4 4)
        15: (4 4 4 3 | 4 4 3 4 | 4 3 4 4 | 3 4 4 4)
        16: (4 4 4 4)
        """
        if rest in (3, 6, 9):  # multiple of 3 and not multiple of 4
            meld = meld_3_tiles(boxes)
            if meld is None:
                return None
            melds.append(meld)
            pos += 3
            rest -= 3
        elif rest in (4, 8, 16):  # multiple of 4 and not multiple 3
            meld = meld_4_tiles(boxes)
            if meld is None:
                return None
            melds.append(meld)
            pos += 4
            rest -= 4
        elif rest in (7, 11, 15):  # only one set of 3
            # chi
            if boxes_is_chi(boxes):
                meld = meld_3_tiles(boxes, meld_type=Meld.CHI)
                if meld is None:
                    return None
                melds.append(meld)
                pos += 3
                rest -= 3
            # kan (should be checked after chi)
            elif boxes_is_kan(boxes):
                meld = meld_4_tiles(boxes)
                if meld is None:
                    return None
                melds.append(meld)
                pos += 4
                rest -= 4
            # pon
            elif boxes_is_pon(boxes):
                meld = meld_3_tiles(boxes, meld_type=Meld.PON)
                if meld is None:
                    return None
                melds.append(meld)
                pos += 3
                rest -= 3
            else:
                print("error: illegal open_boxes({})".format(rest))
                return None
        elif rest in (12,):
            # kan
            if boxes_is_kan(boxes) and boxes_is_kan(boxes[4 : 4 + 4]):
                meld = meld_4_tiles(boxes)
                if meld is None:
                    return None
                melds.append(meld)
                pos += 4
                rest -= 4
            else:
                meld = meld_3_tiles(boxes)
                if meld is None:
                    return None
                melds.append(meld)
                pos += 3
                rest -= 3
        elif rest in (10, 13, 14):  # two sets of 3 and one set of 4 (at least)
            # e.g. 2222345555 -> 2222 345 555 or 222 234 5555 (kan-chi-pon)
            kan_elem = boxes[0][0]
            chi_elems = sorted([b[0] for b in boxes[4 : 4 + 3]])
            pon_elem = boxes[4 + 3][0]
            # chi
            if boxes_is_chi(boxes):
                meld = meld_3_tiles(boxes, meld_type=Meld.CHI)
                if meld is None:
                    return None
                melds.append(meld)
                pos += 3
                rest -= 3
            # may be kan
            elif boxes_is_kan(boxes):
                if (
                    boxes_is_chi(boxes[4 : 4 + 3])
                    and boxes_is_pon(boxes[4 + 3 : 4 + 3 + 3])
                    and kan_elem + 1 == chi_elems[0]
                    and chi_elems[2] == pon_elem
                ):
                    # TODO: also pon can be chosen
                    meld = meld_4_tiles(boxes)
                    if meld is None:
                        return None
                    melds.append(meld)
                    pos += 4
                    rest -= 4
                else:
                    meld = meld_4_tiles(boxes)
                    melds.append(meld)
                    pos += 4
                    rest -= 4
            # pon
            elif boxes_is_pon(boxes):
                meld = meld_3_tiles(boxes, meld_type=Meld.PON)
                if meld is None:
                    return None
                melds.append(meld)
                pos += 3
                rest -= 3
            else:
                print("error: illegal open_boxes({})".format(rest))
                return None
        else:
            print("error: illegal open_boxes({})".format(rest))
            return None
    return melds


# All BACK tiles in closed_boxes are updated, if they compose a closed-kan.
def make_closed_kan_melds(closed_boxes):
    """
    closed_kan is assumed to be consisted of the patterns as follows:
    [back | front | front | back] or [front | back | back | front].
    front tile must be the same.
    """
    melds = []
    pos = 0
    rest = len(closed_boxes)
    replaced = closed_boxes[:]
    while rest >= 4:
        boxes = closed_boxes[pos:]
        kan = boxes_is_closed_kan(boxes)
        if kan is not None:
            boxes[0][0] = boxes[1][0] = boxes[2][0] = boxes[3][0] = kan
            meld = meld_4_tiles(boxes, opened=False)
            melds.append(meld)
            replaced[pos][0] = kan
            replaced[pos + 1][0] = kan
            replaced[pos + 2][0] = kan
            replaced[pos + 3][0] = kan
            pos += 4
            rest -= 4
        else:
            pos += 1
            rest -= 1
    return melds, replaced


def classify_boxes(boxes, y_divider):
    open_boxes = []
    closed_boxes = []
    if len(boxes) > MAX_TILE_NUM:
        print("error: number of tile is too large: ", len(boxes))
        return None, None, None
    if len(boxes) < MIN_TILE_NUM:
        print("error: number of tile is too short: ", len(boxes))
        return None, None, None

    # open or closed
    for box in boxes:
        ymin = box[2]
        ymax = box[4]
        if ymax <= y_divider:
            open_boxes.append(box)
        elif ymin >= y_divider:
            closed_boxes.append(box)
        else:
            print("error: ambiguous box was found: ", box)
            return None, None, None

    if len(open_boxes) == 0:
        print("error: win tile could not be found")
        return None, None, None
    if len(closed_boxes) == 0:
        print("error: closed tile could not be found")
        return None, None, None

    # sort by xmin
    open_boxes = sorted(open_boxes, key=lambda box: box[1])
    closed_boxes = sorted(closed_boxes, key=lambda box: box[1])
    # remove win tile from open_boxes
    win_box = open_boxes.pop(-1)

    return open_boxes, win_box, closed_boxes


def to_136_string(boxes, kan=None):
    man = ""
    pin = ""
    sou = ""
    honors = ""
    labels = dict(zip(list(range(9)), [str(i) for i in list(range(1, 9 + 1))]))
    kan = [] if kan is None else kan

    def delete_kan_if_hit(t):
        for i in range(len(kan)):
            if t == kan[i]:
                del kan[i]
                return True
        return False

    for box in boxes:
        t = box[0]
        res = delete_kan_if_hit(t)
        if res:
            continue
        if t < 9:
            man += labels[t]
        elif t < 18:
            pin += labels[t - 9]
        elif t < 27:
            sou += labels[t - 18]
        elif t < 34:
            honors += labels[t - 27]
        else:
            print("error: illegal tile({}) exists".format(t))
            return None, None, None, None
    return man, pin, sou, honors


def boxes_to_tiles(boxes, kan=None):
    man, pin, sou, honors = to_136_string(boxes, kan)
    if man is None:
        return None
    # print('man', man, 'pin', pin, 'sou', sou, 'honors', honors)
    return tc.string_to_136_array(man=man, pin=pin, sou=sou, honors=honors)


def boxes_is_chi(boxes):
    items = sorted([t[0] for t in boxes[0:3]])
    if is_honor(items[0]) or is_honor(items[2]):
        return False
    return is_chi(items)


def boxes_is_pon(boxes):
    items = [t[0] for t in boxes[0:3]]
    return is_pon(items)


def boxes_is_kan(boxes):
    return boxes[0][0] == boxes[1][0] == boxes[2][0] == boxes[3][0]


def boxes_is_closed_kan(boxes):
    if boxes[0][0] == boxes[3][0] and boxes[1][0] == boxes[2][0] == TileId.BACK:
        return boxes[0][0]
    if boxes[0][0] == boxes[3][0] == TileId.BACK and boxes[1][0] == boxes[2][0]:
        return boxes[1][0]
    return None


def meld_3_tiles(boxes, meld_type=None):
    man, pin, sou, honors = to_136_string(boxes[:3])
    if man is None:
        return None
    # print('man', man, 'pin', pin, 'sou', sou, 'honors', honors)
    tiles = tc.string_to_136_array(man=man, pin=pin, sou=sou, honors=honors)
    if meld_type is None:
        if boxes_is_pon(boxes):
            meld_type = Meld.PON
        elif boxes_is_chi(boxes):
            meld_type = Meld.CHI
        else:
            print("error: neither pon nor chi({})".format(boxes))
            return None
    # print(tc.to_one_line_string(tiles))
    return Meld(meld_type=meld_type, tiles=tiles)


def meld_4_tiles(boxes, opened=True):
    man, pin, sou, honors = to_136_string(boxes[:4])
    if man is None:
        return None
    # print('man', man, 'pin', pin, 'sou', sou, 'honors', honors)
    tiles = tc.string_to_136_array(man=man, pin=pin, sou=sou, honors=honors)
    # print(tc.to_one_line_string(tiles))
    return Meld(meld_type=Meld.KAN, tiles=tiles, opened=opened)


def print_hand_result(hand_result):
    if hand_result.error is not None:
        print(hand_result.error)
    else:
        print(hand_result.han, hand_result.fu)
        print(hand_result.cost)
        print(hand_result.cost["main"])
        print(hand_result.yaku)
        if hand_result.fu_details is not None:
            for fu_item in hand_result.fu_details:
                print(fu_item)


if __name__ == "__main__":
    boxes = [
        [99, 165, 360, 194, 410],
        [99, 221, 360, 249, 410],
        [30, 248, 362, 277, 412],
        [28, 111, 361, 138, 411],
        [28, 193, 363, 222, 412],
        [30, 276, 361, 305, 411],
        [99, 83, 361, 111, 410],
        [27, 357, 358, 387, 407],
        [99, 302, 358, 332, 407],
        [99, 138, 360, 166, 410],
        [99, 411, 359, 442, 409],
        [32, 439, 359, 471, 409],
        [99, 329, 358, 359, 410],
        [29, 29, 359, 56, 408],
        [99, 0, 358, 27, 410],
        [27, 385, 362, 415, 413],
        [32, 342, 138, 369, 176],
        [29, 53, 359, 82, 412],
    ]
    result = score(boxes, True, 512 // 2)
