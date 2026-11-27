FACES = [
    ("MING-A", "松桥明体", "open", "松桥东巷西门口北街临时车向请依次通行公告景河导览朝阳流云青石木路站便利入口出口号室年号·–1234567890",
     "松桥东巷 东巷指示 松桥西门 北街入口 请依次通行", "songqiao-ming.otf"),
    ("MING-B", "云隅碑宋", "public_only", "松桥东西南巷北街临时车辆向请依次通行公告青石木路",
     "青石路景河街 西门 东巷 松桥松桥", "yunyu-song.otf"),
    ("HANGUL-O", "汀声常用字", "open", "안내출입구동쪽서남북길가나다라마바사아자차카타파하·",
     "동쪽 안내 서쪽 안내 출입구 입구 안내 북쪽", "ting-hangul.otf"),
    ("HANGUL-P", "学馆朝文", "public_only", "안내출입구동쪽서남북길",
     "공공 안내 동쪽 길 출입 안내", "study-hangul.ttf"),
    ("LATIN-C", "石纹转角体", "open", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz 0123456789&–·.,:!?é",
     "ARCHWAY NORTH GATE RIVER WALK TO EAST LANE", "stoneway-bold.ttf"),
    ("PAN-E", "南序展牌体", "open", "松桥东巷南西门街临时车道方向河青石木路안내입구·",
     "松桥东巷 안내 东门 안내 西门入口", "nanxu-sign.otf"),
]


def seed(db):
    for face in FACES:
        db.execute(
            """INSERT INTO typefaces (code, family, license_kind, coverage, specimen, font_file)
               VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (code) DO NOTHING""",
            face,
        )
    db.execute(
        """INSERT INTO proofs (code, location, copy_text, use_kind)
           VALUES ('SQ-102', '松桥东巷 商铺导向牌', '东巷 안내', 'commercial')
           ON CONFLICT (code) DO NOTHING"""
    )
    db.execute(
        """INSERT INTO proofs (code, location, copy_text, use_kind)
           VALUES ('SQ-115', '松桥北街 公共路引', '北街', 'public')
           ON CONFLICT (code) DO NOTHING"""
    )
    inserted = db.execute(
        """INSERT INTO proofs (code, location, copy_text, use_kind, state, locked_by, locked_at)
           VALUES ('SQ-090', '西门既有铭牌', '西门', 'commercial', 'locked',
                   'archive@demo.local', '2026-11-25T07:40:00Z')
           ON CONFLICT (code) DO NOTHING"""
    )
    if inserted:
        for glyph in "西门":
            db.execute(
                "INSERT INTO font_assignments (proof_code, glyph, face_code) VALUES ('SQ-090', %s, 'MING-A')",
                (glyph,),
            )
    return {
        table: db.one(f"SELECT COUNT(*) AS count FROM {table}")["count"]
        for table in ("proofs", "typefaces", "font_assignments", "glyph_proposals")
    }
