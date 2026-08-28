"""悼明梗元素库（增强娱乐性）"""

MEMES = [
    # 开局系
    {"text": "开局一个碗", "source": "朱元璋", "category": "开局", "tags": ["开局", "朱元璋", "逆袭"], "mood": "致敬"},
    {"text": "朕本淮右布衣", "source": "朱元璋", "category": "名句", "tags": ["朱元璋", "皇帝", "自述"], "mood": "致敬"},
    {"text": "驱逐胡虏，恢复中华", "source": "朱元璋北伐檄文", "category": "名句", "tags": ["朱元璋", "北伐", "民族"], "mood": "致敬"},
    # 抗倭系
    {"text": "封侯非我意，但愿海波平", "source": "戚继光", "category": "名句", "tags": ["戚继光", "抗倭", "无私"], "mood": "致敬"},
    {"text": "俞龙戚虎", "source": "俞大猷 / 戚继光", "category": "典故", "tags": ["俞大猷", "戚继光", "武将"], "mood": "致敬"},
    {"text": "鸳鸯阵", "source": "戚继光", "category": "典故", "tags": ["戚继光", "阵法", "军事"], "mood": "致敬"},
    # 心学系
    {"text": "知行合一", "source": "王阳明", "category": "名句", "tags": ["王阳明", "心学", "哲学"], "mood": "致敬"},
    {"text": "此心光明，亦复何言", "source": "王阳明临终", "category": "名句", "tags": ["王阳明", "心学", "临终"], "mood": "致敬"},
    {"text": "龙场悟道", "source": "王阳明", "category": "典故", "tags": ["王阳明", "心学", "逆境"], "mood": "致敬"},
    # 清白死谏系
    {"text": "粉骨碎身浑不怕，要留清白在人间", "source": "于谦《石灰吟》", "category": "名句", "tags": ["于谦", "清白", "名句"], "mood": "致敬"},
    {"text": "北京保卫战", "source": "于谦", "category": "事件", "tags": ["于谦", "北京", "保卫"], "mood": "致敬"},
    {"text": "铁肩担道义，辣手著文章", "source": "杨继盛", "category": "名句", "tags": ["杨继盛", "死谏", "名句"], "mood": "致敬"},
    # 改革系
    {"text": "一条鞭法", "source": "张居正", "category": "典故", "tags": ["张居正", "改革", "税制"], "mood": "反思"},
    {"text": "我非相，乃摄也", "source": "张居正", "category": "名句", "tags": ["张居正", "首辅", "名分"], "mood": "反思"},
    # 文学系
    {"text": "别人笑我太疯癫，我笑他人看不穿", "source": "唐伯虎《桃花庵歌》", "category": "名句", "tags": ["唐伯虎", "狂生", "名句"], "mood": "戏谑"},
    {"text": "情不知所起，一往而深", "source": "汤显祖《牡丹亭》", "category": "名句", "tags": ["汤显祖", "牡丹亭", "戏曲"], "mood": "致敬"},
    {"text": "临川四梦", "source": "汤显祖", "category": "典故", "tags": ["汤显祖", "戏曲", "四梦"], "mood": "致敬"},
    # 科技系
    {"text": "东方医药百科全书", "source": "《本草纲目》", "category": "科技", "tags": ["李时珍", "医药", "百科"], "mood": "致敬"},
    {"text": "中国 17 世纪的工艺百科全书", "source": "《天工开物》", "category": "科技", "tags": ["宋应星", "工艺", "百科"], "mood": "致敬"},
    {"text": "欲求超胜，必须会通", "source": "徐光启", "category": "名句", "tags": ["徐光启", "西学东渐", "科学"], "mood": "致敬"},
    {"text": "大丈夫当朝碧海而暮苍梧", "source": "徐霞客", "category": "名句", "tags": ["徐霞客", "地理", "壮游"], "mood": "致敬"},
    {"text": "音乐上的哥白尼", "source": "朱载堉·十二平均律", "category": "典故", "tags": ["朱载堉", "音乐", "平均律"], "mood": "致敬"},
    # 航海系
    {"text": "七下西洋", "source": "郑和", "category": "事件", "tags": ["郑和", "航海", "和平"], "mood": "致敬"},
    {"text": "协和万邦", "source": "郑和下西洋", "category": "典故", "tags": ["郑和", "外交", "和平"], "mood": "致敬"},
    # 帝王系
    {"text": "天子守国门，君王死社稷", "source": "明朝祖训", "category": "名句", "tags": ["明朝", "祖训", "气节"], "mood": "致敬"},
    {"text": "不和亲，不赔款，不割地，不纳贡", "source": "明朝祖训", "category": "名句", "tags": ["明朝", "祖训", "气节"], "mood": "致敬"},
    {"text": "朕非亡国之君，诸臣尽亡国之臣尔", "source": "崇祯自缢前", "category": "名句", "tags": ["崇祯", "明亡", "悲剧"], "mood": "惋惜"},
    {"text": "朕死，无面目见祖宗于地下，自去冠冕，以发覆面", "source": "崇祯《自遗书》", "category": "名句", "tags": ["崇祯", "煤山", "殉国"], "mood": "惋惜"},
    {"text": "永乐盛世", "source": "明成祖朱棣", "category": "事件", "tags": ["朱棣", "盛世", "鼎盛"], "mood": "致敬"},
    # 反差/戏谑系
    {"text": "当皇帝有什么好？天天 996 还被骂", "source": "网络梗改编", "category": "反差", "tags": ["戏谑", "崇祯", "现代视角"], "mood": "戏谑"},
    {"text": "如果海瑞当老板", "source": "网络梗改编", "category": "反差", "tags": ["戏谑", "海瑞", "职场"], "mood": "戏谑"},
    {"text": "当王阳明遇上 ChatGPT", "source": "网络梗改编", "category": "反差", "tags": ["戏谑", "王阳明", "AI"], "mood": "戏谑"},
    {"text": "给戚继光一份 Excel", "source": "网络梗改编", "category": "反差", "tags": ["戏谑", "戚继光", "现代办公"], "mood": "戏谑"},
    # 数字系
    {"text": "276 年，16 帝", "source": "明史", "category": "数字", "tags": ["明朝", "国祚", "数据"], "mood": "致敬"},
    {"text": "1892 种药材", "source": "《本草纲目》", "category": "数字", "tags": ["李时珍", "数据"], "mood": "致敬"},
    {"text": "22877 卷", "source": "《永乐大典》", "category": "数字", "tags": ["永乐大典", "类书", "数据"], "mood": "致敬"},
]


def list_memes(category=None, mood=None):
    items = MEMES
    if category:
        items = [m for m in items if m["category"] == category]
    if mood:
        items = [m for m in items if m["mood"] == mood]
    return items


def random_meme(category=None, mood=None):
    import random
    items = list_memes(category, mood)
    return random.choice(items) if items else None


def list_meme_categories():
    return sorted({m["category"] for m in MEMES})