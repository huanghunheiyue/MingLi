"""明代历史文化知识库 - 人物部分"""
"""
明代历史文化知识库
所有数据严格基于史实，杜绝 AI 编造。
"""

SAFETY_GUIDELINE = (
    "弘扬中华优秀传统文化、以史为鉴、体现中华民族共同体意识，"
    "严禁民族对立、政治影射、戏谑伟人。所有描述以正史为准。"
)

FIGURES: dict = {
    # 名臣
    "于谦": {
        "category": "名臣", "era": "正统/景泰",
        "birth_year": 1398, "death_year": 1457,
        "key_events": ["土木堡之变", "北京保卫战", "夺门之变被冤杀"],
        "achievements": [
            "土木堡之变后力排南迁之议，坚守北京",
            "主持北京保卫战，击退瓦剌也先",
            "《石灰吟》粉骨碎身浑不怕，要留清白在人间为千古名句",
        ],
        "quote": "粉骨碎身浑不怕，要留清白在人间。",
        "tags": ["忠臣", "北京保卫战", "清白"],
    },
    "海瑞": {
        "category": "名臣", "era": "嘉靖/隆庆/万历",
        "birth_year": 1514, "death_year": 1587,
        "key_events": ["上《治安疏》骂嘉靖", "推行清丈田亩", "卒于官"],
        "achievements": [
            "明代著名清官，一生清贫，卒于任上仅余俸银数两",
            "上书嘉靖帝，直言天下人谓陛下为昏君",
            "被誉为海青天，与宋包拯齐名",
        ],
        "quote": "事君者以忠，治民者以仁。",
        "tags": ["清官", "海青天", "廉政"],
    },
    "张居正": {
        "category": "名臣", "era": "万历",
        "birth_year": 1525, "death_year": 1582,
        "key_events": ["一条鞭法", "考成法", "万历前期中兴"],
        "achievements": [
            "明代唯一生前被授予太傅、太师的头号首辅",
            "推行一条鞭法，把实物税与徭役折银征收，简化税制",
            "考成法考核官员，使政令虽万里外朝下而夕奉行",
            "死后被抄家，改革成果大半付诸东流",
        ],
        "quote": "愿以深心奉尘刹，不予自身求利益。",
        "tags": ["改革", "万历中兴", "一条鞭法"],
    },
    "徐阶": {
        "category": "名臣", "era": "嘉靖",
        "birth_year": 1503, "death_year": 1583,
        "key_events": ["倒严", "推动隆庆开关"],
        "achievements": [
            "隐忍多年扳倒严嵩，为夏言复仇",
            "推动嘉隆大改革，促成隆庆开关与俺答封贡",
        ],
        "quote": "",
        "tags": ["倒严", "隐忍"],
    },
    "杨继盛": {
        "category": "名臣", "era": "嘉靖",
        "birth_year": 1516, "death_year": 1555,
        "key_events": ["弹劾严嵩十大罪", "下狱被杖"],
        "achievements": [
            "上《请诛贼臣疏》弹劾严嵩五奸十大罪",
            "被诬下狱，腿肉被割，仍书心字于壁",
        ],
        "quote": "铁肩担道义，辣手著文章。",
        "tags": ["死谏", "弹严"],
    },
    "杨涟": {
        "category": "名臣", "era": "泰昌/天启",
        "birth_year": 1572, "death_year": 1625,
        "key_events": ["六君子之狱", "左光斗同死"],
        "achievements": [
            "东林党重要人物，弹劾魏忠贤二十四大罪",
            "天启五年下诏狱，被拷讯至死",
        ],
        "quote": "",
        "tags": ["东林", "死谏", "六君子"],
    },
    # 文人
    "王阳明": {
        "category": "文人", "era": "成化/正德/嘉靖",
        "birth_year": 1472, "death_year": 1529,
        "key_events": ["龙场悟道", "平宁王朱宸濠之乱", "心学集大成"],
        "achievements": [
            "创立阳明心学，提出知行合一与致良知",
            "平定宁王朱宸濠叛乱，立下赫赫军功",
            "其思想远播日本、朝鲜，是东亚思想史的重要一环",
        ],
        "quote": "知行合一，致良知。",
        "tags": ["心学", "知行合一", "军功"],
    },
    "李贽": {
        "category": "文人", "era": "嘉靖/万历",
        "birth_year": 1527, "death_year": 1602,
        "key_events": ["剃发为僧", "异端思想", "被捕自刎"],
        "achievements": [
            "明代最具异端色彩的思想家，批判儒家道统",
            "著作《焚书》《藏书》主张童心说",
            "被誉为中国 16 世纪反传统异端",
        ],
        "quote": "夫童心者，真心也……若失却童心，便失却真心。",
        "tags": ["异端", "童心说"],
    },
    "唐伯虎": {
        "category": "文人", "era": "成化/正德",
        "birth_year": 1470, "death_year": 1524,
        "key_events": ["会试舞弊案牵连", "点秋香为后人附会", "江南四大才子"],
        "achievements": [
            "明代著名画家、诗人，吴门画派代表人物之一",
            "书画双绝，与沈周、文徵明、仇英合称明四家",
            "民间故事三笑点秋香多属虚构，应以史实为准",
        ],
        "quote": "别人笑我太疯癫，我笑他人看不穿。",
        "tags": ["才子", "画家", "吴门画派"],
    },
    "汤显祖": {
        "category": "文人", "era": "嘉靖/万历",
        "birth_year": 1550, "death_year": 1616,
        "key_events": ["临川四梦", "遂昌知县"],
        "achievements": [
            "明代最伟大的戏曲家，临川四梦牡丹亭紫钗记南柯记邯郸记",
            "牡丹亭情不知所起一往而深千古传颂",
            "与莎士比亚同年逝世，东西方戏剧双星",
        ],
        "quote": "情不知所起，一往而深。",
        "tags": ["戏曲", "牡丹亭", "临川四梦"],
    },
    "徐渭": {
        "category": "文人", "era": "嘉靖/万历",
        "birth_year": 1521, "death_year": 1593,
        "key_events": ["胡宗宪幕僚", "狂草泼墨", "九次自杀未遂"],
        "achievements": [
            "明代三大才子之一，诗书画戏皆绝",
            "开创青藤画派，泼墨大写意画风影响后世八大山人、吴昌硕、齐白石",
            "著有《南词叙录》为中国第一部南戏研究专著",
        ],
        "quote": "半生落魄已成翁，独立书斋啸晚风。",
        "tags": ["狂草", "泼墨", "三大才子"],
    },
    # 武将
    "戚继光": {
        "category": "武将", "era": "嘉靖/隆庆/万历",
        "birth_year": 1528, "death_year": 1588,
        "key_events": ["抗倭", "义乌兵", "镇守蓟镇"],
        "achievements": [
            "东南抗倭 13 年，荡平倭寇",
            "著《纪效新书》《练兵实纪》，创鸳鸯阵法",
            "镇守蓟镇 16 年，保卫北疆，被誉为战神",
        ],
        "quote": "封侯非我意，但愿海波平。",
        "tags": ["抗倭", "鸳鸯阵", "战神"],
    },
    "俞大猷": {
        "category": "武将", "era": "嘉靖",
        "birth_year": 1503, "death_year": 1579,
        "key_events": ["抗倭", "与戚继光齐名"],
        "achievements": [
            "与戚继光并称俞龙戚虎",
            "精通棍法，著《剑经》",
        ],
        "quote": "",
        "tags": ["抗倭", "俞龙戚虎"],
    },
    "袁崇焕": {
        "category": "武将", "era": "天启/崇祯",
        "birth_year": 1584, "death_year": 1630,
        "key_events": ["宁远大捷", "己巳之变", "被冤杀"],
        "achievements": [
            "宁远之战以红衣大炮击伤努尔哈赤，是明军首次重大胜利",
            "皇太极绕道入关后回师，崇祯中反间计下狱",
            "被凌迟处死，身死国灭，其冤为明亡重要标志",
        ],
        "quote": "杖策只因图雪耻，横戈原不为封侯。",
        "tags": ["宁远", "冤案", "抗清"],
    },
    "李成梁": {
        "category": "武将", "era": "隆庆/万历",
        "birth_year": 1526, "death_year": 1615,
        "key_events": ["辽东总兵", "扶植努尔哈赤"],
        "achievements": [
            "镇守辽东近三十年，屡破蒙古、女真",
            "后期有养虎贻患之议，然功过争议颇多",
        ],
        "quote": "",
        "tags": ["辽东"],
    },
    # 科学家
    "李时珍": {
        "category": "科学家", "era": "嘉靖/万历",
        "birth_year": 1518, "death_year": 1593,
        "key_events": ["本草纲目"],
        "achievements": [
            "耗时 27 年编成《本草纲目》，载药 1892 种",
            "达尔文称之为中国古代百科全书",
        ],
        "quote": "身如逆流船，心比铁石坚。",
        "tags": ["本草纲目", "医药"],
    },
    "徐光启": {
        "category": "科学家", "era": "万历/天启/崇祯",
        "birth_year": 1562, "death_year": 1633,
        "key_events": ["与利玛窦译《几何原本》", "编《农政全书》"],
        "achievements": [
            "明代最杰出的科学家，与利玛窦合译《几何原本》前 6 卷",
            "编《农政全书》60 卷，是 17 世纪中国农学集大成之作",
            "是中西科学交流的奠基人之一",
        ],
        "quote": "欲求超胜，必须会通；会通之前，先须翻译。",
        "tags": ["西学东渐", "几何原本", "农政全书"],
    },
    "宋应星": {
        "category": "科学家", "era": "万历/崇祯",
        "birth_year": 1587, "death_year": 1666,
        "key_events": ["天工开物"],
        "achievements": [
            "著《天工开物》，被誉为中国 17 世纪的工艺百科全书",
            "海外译本众多，Tiangong Kaiwu已成国际通用名词",
        ],
        "quote": "天覆地载，物号数万。",
        "tags": ["天工开物", "工艺"],
    },
    "徐霞客": {
        "category": "科学家", "era": "万历/崇祯",
        "birth_year": 1587, "death_year": 1641,
        "key_events": ["游历四方", "徐霞客游记"],
        "achievements": [
            "中国最早的地理学家之一",
            "《徐霞客游记》60 万字，开创系统观察自然之先河",
            "对喀斯特地貌的考察比西方早 200 年",
        ],
        "quote": "大丈夫当朝碧海而暮苍梧。",
        "tags": ["游记", "地理"],
    },
    "朱载堉": {
        "category": "科学家", "era": "嘉靖/万历",
        "birth_year": 1536, "death_year": 1611,
        "key_events": ["十二平均律"],
        "achievements": [
            "明代王子、世界级音乐理论家",
            "首创十二平均律，西方键盘乐器由此奠基",
            "曾被德国学者誉为东方文艺复兴的先驱",
        ],
        "quote": "",
        "tags": ["十二平均律", "音乐"],
    },
    # 帝王
    "朱元璋": {
        "category": "帝王", "era": "洪武",
        "birth_year": 1328, "death_year": 1398,
        "key_events": ["开局一个碗", "建立明朝", "洪武之治"],
        "achievements": [
            "布衣出身，灭元建明，统一全国",
            "整顿吏治，惩治贪腐（《大诰》）",
            "废丞相、设三司，皇权高度集中",
        ],
        "quote": "朕本淮右布衣。",
        "tags": ["洪武", "开国"],
    },
    "朱棣": {
        "category": "帝王", "era": "永乐",
        "birth_year": 1360, "death_year": 1424,
        "key_events": ["靖难之役", "永乐盛世", "郑和下西洋"],
        "achievements": [
            "以藩王夺位，史称靖难之役",
            "永乐盛世奠定明朝鼎盛格局",
            "派郑和下西洋，编《永乐大典》",
            "迁都北京，五征漠北",
        ],
        "quote": "",
        "tags": ["永乐", "盛世", "靖难"],
    },
    "朱高炽": {
        "category": "帝王", "era": "洪熙",
        "birth_year": 1398, "death_year": 1425,
        "key_events": ["仁宗昭皇帝"],
        "achievements": [
            "在位仅 10 个月，却停止了永乐时期的过度征伐",
            "仁宣之治的开创者",
        ],
        "quote": "",
        "tags": ["仁宗"],
    },
    "朱瞻基": {
        "category": "帝王", "era": "宣德",
        "birth_year": 1399, "death_year": 1435,
        "key_events": ["仁宣之治", "御驾亲征"],
        "achievements": [
            "与其父朱高炽并称仁宣之治，是明朝的黄金时代",
            "宣德炉、宣德瓷为后世典范",
        ],
        "quote": "",
        "tags": ["宣德", "仁宣之治"],
    },
    "朱佑樘": {
        "category": "帝王", "era": "成化/弘治",
        "birth_year": 1470, "death_year": 1505,
        "key_events": ["弘治中兴"],
        "achievements": [
            "弘治中兴被誉为明朝中兴之最",
            "驱逐奸佞，任用贤臣",
        ],
        "quote": "",
        "tags": ["弘治", "中兴"],
    },
    "朱厚熜": {
        "category": "帝王", "era": "嘉靖",
        "birth_year": 1507, "death_year": 1567,
        "key_events": ["大礼议", "壬寅宫变", "倭寇狂獗"],
        "achievements": [
            "在位 45 年，是明朝实际掌权最久的皇帝",
            "中后期沉迷道教，朝政被严嵩把持 20 余年",
            "嘉靖倭乱激发出戚继光抗倭",
        ],
        "quote": "",
        "tags": ["嘉靖", "道教"],
    },
    "朱由检": {
        "category": "帝王", "era": "崇祯",
        "birth_year": 1611, "death_year": 1644,
        "key_events": ["即位勤政", "自缢煤山"],
        "achievements": [
            "即位时明朝已病入膏肓，非亡国之君而当亡国之运",
            "勤政节俭，鸡鸣而起夜分不寐，但然刚愎多疑",
            "李自成破北京后自缢于煤山，明亡",
        ],
        "quote": "朕非亡国之君，诸臣尽亡国之臣尔！",
        "tags": ["崇祯", "煤山", "明亡"],
    },
    # 航海
    "郑和": {
        "category": "航海家", "era": "永乐",
        "birth_year": 1371, "death_year": 1433,
        "key_events": ["七下西洋"],
        "achievements": [
            "率当时世界最大船队七下西洋，远抵非洲东岸",
            "比欧洲大航海时代早近一个世纪",
            "体现中国开放、和平、包容的海洋文明理念",
        ],
        "quote": "",
        "tags": ["航海", "和平外交"],
    },
}

EVENTS: dict = {
    "靖难之役": {
        "year": "1399-1402", "location": "北平→南京",
        "key_figures": ["朱棣", "建文帝", "耿炳文", "李景隆"],
        "summary": "建文帝即位后削藩，燕王朱棣以清君侧为名起兵，历时三年攻入南京，建文帝下落成谜，朱棣即位，是为永乐帝。",
        "significance": "靖难之役改变了明朝政治走向，削藩失败使藩王势力大衰，皇权高度集中；同时也带来南北经济文化重心的进一步转移。",
        "reflection": "以史为鉴，权力交接的稳妥是国之大事，清君侧常为野心之辞，制度设计比个人贤愚更重要。",
        "tags": ["靖难", "永乐"],
    },
    "永乐盛世": {
        "year": "1403-1424", "location": "全国",
        "key_figures": ["朱棣", "姚广孝", "郑和", "解缙"],
        "summary": "永乐年间政治清明、经济繁荣、文化昌盛、万国来朝，被后世视为明朝鼎盛时期。",
        "significance": "迁都北京、编《永乐大典》、派郑和下西洋、五征漠北，奠定中华多元一体格局的进一步巩固。",
        "reflection": "盛世不是一人之功，而是制度、贤臣、百姓合力；展现中华民族开放、自信的、丰富的精神气质。",
        "tags": ["盛世", "永乐"],
    },
    "仁宣之治": {
        "year": "1424-1435", "location": "全国",
        "key_figures": ["朱高炽", "朱瞻基", "杨士奇", "杨荣", "杨溥"],
        "summary": "明仁宗、宣宗两朝推行休养生息政策，宽松刑罚、废除苛捐，是明朝政治最清明的时期之一。",
        "significance": "为明朝前期鼎盛画上句号，亦为后世留下内圣外王的治理范本。",
        "reflection": "盛世之后能自我克制、与民休息，是大智慧。",
        "tags": ["仁宣之治", "盛世"],
    },
    "土木堡之变": {
        "year": "1449", "location": "河北怀来土木堡",
        "key_figures": ["明英宗", "王振", "也先"],
        "summary": "明英宗受太监王振怂恿，亲征瓦剌，在土木堡全军覆没，英宗被俘，是明朝由盛转衰的关键转折点。",
        "significance": "明朝军事实力遭到毁灭性打击，文官集团由此崛起，宦官干政的恶果初现。",
        "reflection": "以史为鉴，决策不可任性，主少国疑之时尤需制度约束。",
        "tags": ["土木堡", "由盛转衰"],
    },
    "北京保卫战": {
        "year": "1449", "location": "北京",
        "key_figures": ["于谦", "明代宗", "也先"],
        "summary": "土木堡之变后兵部侍于谦力排南迁之议，拥立代宗，整军经武，于德胜门、北京城下大败瓦剌，迎回英宗。",
        "significance": "保住明朝国祚百年，于谦被誉为救时宰相。",
        "reflection": "国之存亡系于担当，粉骨碎身浑不怕，要留清白在人间是中华风骨的写照。",
        "tags": ["于谦", "保卫"],
    },
    "弘治中兴": {
        "year": "1488-1505", "location": "全国",
        "key_figures": ["朱佑樘", "刘健", "谢迁", "李东阳"],
        "summary": "明孝宗励精图治、整顿吏治、勤政爱臣，被誉为明朝中兴之最。",
        "significance": "结束了成化朝的混乱局面，奠定了明代后期稳定的政治基础。",
        "reflection": "贤君不易得，制度更不易得；一代明君可致一时中兴，制度健全方能长治久安。",
        "tags": ["弘治", "中兴"],
    },
    "张居正改革": {
        "year": "1572-1582", "location": "全国",
        "key_figures": ["张居正", "万历帝", "冯保"],
        "summary": "万历前期首辅张居正推行一条鞭法、考成法，使国家财政大幅改善，政令畅通。",
        "significance": "是明朝最后一次大规模改革；张居正死后被清算，改革成果大半付诸东流。",
        "reflection": "改革成败不在一策，而在人亡政息；以史为鉴，制度建设方能超越个人。",
        "tags": ["改革", "万历"],
    },
    "抗倭援朝": {
        "year": "1592-1598", "location": "朝鲜半岛",
        "key_figures": ["李如松", "李舜臣", "丰臣秀吉"],
        "summary": "日本丰臣秀吉侵朝鲜，明军两次出兵援助，最终将其逐退。",
        "significance": "维护了东亚宗藩秩序，体现了中华文明圈的和平稳定。",
        "reflection": "中华文化圈和平秩序的维护需要担当；以邻为壑不可取，和合才是正道。",
        "tags": ["援朝", "和平"],
    },
    "萨尔浒之战": {
        "year": "1619", "location": "辽宁抚顺",
        "key_figures": ["努尔哈赤", "杨镐", "杜松"],
        "summary": "明军分四路围攻后金，被努尔哈赤各个击破，明军主力尽丧，从此明对后金转入战略防御。",
        "significance": "明朝军事力量进一步衰落，东北防线崩溃。",
        "reflection": "知己知彼方能百战不殆；以史为鉴，应警惕战略分散与骄傲轻敌。",
        "tags": ["萨尔浒", "转折"],
    },
    "东林党争": {
        "year": "1604-1629", "location": "全国",
        "key_figures": ["顾宪成", "高攀龙", "魏忠贤"],
        "summary": "东林书院讲学引发士大夫清议，与阉党、齐楚浙党形成激烈党争，最终阉党获胜，东林遭血洗。",
        "significance": "士大夫与宦官的最后一次大对决，明末政治极度黑暗。",
        "reflection": "党争消耗国力；以史为鉴，团结协作方能抵御外侮。",
        "tags": ["党争", "东林"],
    },
    "明末农民起义": {
        "year": "1627-1644", "location": "全国",
        "key_figures": ["李自成", "张献忠", "王二"],
        "summary": "崇祯年间陕北农民揭竿而起，最终李自成攻入北京，崇祯自缢，明亡。",
        "significance": "明末赋役沉重、灾荒频仍，起义最终瓦解了明朝统治。",
        "reflection": "水能载舟亦能覆舟；以史为鉴，民心向背是政权最根本的依靠。",
        "tags": ["明亡", "起义"],
    },
    "郑和下西洋": {
        "year": "1405-1433", "location": "西太平洋→印度洋",
        "key_figures": ["郑和", "朱棣"],
        "summary": "永乐年间郑和率当时世界最大船队七下西洋，远抵东非麻林地（今肯尼亚），未取他一寸土地。",
        "significance": "展现中华文明开放、和平、包容的气质，是中华民族共同体意识扩展的体现。",
        "reflection": "和平外交、协和万邦是中华优秀传统文化的重要基因；以史为鉴，开放带来繁荣。",
        "tags": ["和平", "航海"],
    },
    "永乐大典编纂": {
        "year": "1403-1408", "location": "南京",
        "key_figures": ["解缙", "姚广孝", "朱棣"],
        "summary": "永乐帝命解缙、姚广孝等编纂《永乐大典》，收书 8000 余种，22877 卷，是中国最大的类书。",
        "significance": "保存了大量宋元以前典籍；正本下落不明，副本亦有残缺，仍是文化瑰宝。",
        "reflection": "中华文明的连续性源于对典籍的珍视与整理。",
        "tags": ["类书", "文化"],
    },
}

CULTURE: dict = {
    "永乐大典": {"type": "类书", "author": "解缙、姚广孝", "year": "1408",
                 "significance": "中国古代最大的类书，保存了大量珍贵典籍。"},
    "天工开物": {"type": "科技著作", "author": "宋应星", "year": "1637",
                 "significance": "被誉为17世纪中国工艺百科全书。"},
    "农政全书": {"type": "农学著作", "author": "徐光启", "year": "1639",
                 "significance": "明代农学集大成之作，60 卷。"},
    "本草纲目": {"type": "医药著作", "author": "李时珍", "year": "1578",
                 "significance": "载药 1892 种，被誉为东方医药百科全书。"},
    "徐霞客游记": {"type": "地理著作", "author": "徐霞客", "year": "1640",
                   "significance": "开创系统观察自然之先河，对喀斯特地貌考察早西方 200 年。"},
    "三国演义": {"type": "小说", "author": "罗贯中", "year": "元末明初",
                 "significance": "中国第一部章回体小说，文人智慧的结晶。"},
    "水浒传": {"type": "小说", "author": "施耐庵", "year": "元末明初",
               "significance": "中国第一部以农民起义为题材的长篇小说。"},
    "西游记": {"type": "小说", "author": "吴承恩", "year": "16 世纪中叶",
               "significance": "浪漫主义神魔小说的巅峰之作。"},
    "金瓶梅": {"type": "小说", "author": "兰陵笑笑生", "year": "16 世纪后期",
               "significance": "中国第一部以市井生活为题材的长篇小说。"},
    "牡丹亭": {"type": "戏曲", "author": "汤显祖", "year": "1598",
               "significance": "明代戏曲最高峰，情不知所起一往而深。"},
    "阳明心学": {"type": "哲学", "author": "王阳明", "year": "16 世纪初",
                 "significance": "影响东亚 500 年，与朱子学分庭抗礼。"},
    "泰州学派": {"type": "哲学", "author": "王艮", "year": "16 世纪中叶",
                 "significance": "阳明心学的平民化分支，下层民众的觉醒。"},
    "紫砂壶": {"type": "工艺", "author": "时大彬等", "year": "16 世纪",
               "significance": "宜兴紫砂成为中华茶文化的标志器物。"},
    "青花瓷": {"type": "工艺", "author": "景德镇窑工", "year": "永乐/宣德",
               "significance": "永宣青花是中华瓷器艺术的巅峰，明如镜白如玉薄如纸声如磬。"},
}

SCIENCE: dict = {
    "十二平均律": {
        "inventor": "朱载堉", "year": "1584",
        "significance": "首创十二平均律，比西方早 100 年，被尊为音乐上的哥白尼。",
    },
    "天工开物插图": {
        "inventor": "宋应星", "year": "1637",
        "significance": "中国古代最精美的科技插图。",
    },
    "《几何原本》前六卷": {
        "inventor": "徐光启、利玛窦合译", "year": "1607",
        "significance": "西方科学传入中国的里程碑。",
    },
}

MING_DATA = {
    "FIGURES": FIGURES,
    "EVENTS": EVENTS,
    "CULTURE": CULTURE,
    "SCIENCE": SCIENCE,
}


def get_figure(name: str):
    return FIGURES.get(name)


def get_event(name: str):
    return EVENTS.get(name)


def list_subjects(content_type: str) -> list:
    """根据文案类型返回可选主题列表"""
    if content_type in ("eulogy", "elegiac_prose", "couplet", "poem", "funeral_oration"):
        return sorted(FIGURES.keys())
    if content_type == "historical_event":
        return sorted(EVENTS.keys())
    if content_type == "meme":
        return sorted(FIGURES.keys()) + sorted(EVENTS.keys())
    return sorted(FIGURES.keys()) + sorted(EVENTS.keys())


def get_context_for_subject(subject: str, max_chars=None):
    """获取某个主题的上下文，供 Prompt 使用，可选截断"""
    if subject in FIGURES:
        f = FIGURES[subject]
        text = (
            f"人物：{subject}\n"
            f"类别：{f.get('category')}\n"
            f"时代：{f.get('era')}\n"
            f"生卒：{f.get('birth_year')}-{f.get('death_year')}\n"
            f"关键事迹：{'; '.join(f.get('key_events', []))}\n"
            f"主要成就：{'; '.join(f.get('achievements', []))}\n"
            f"名句：{f.get('quote', '无')}\n"
        )
    elif subject in EVENTS:
        e = EVENTS[subject]
        text = (
            f"事件：{subject}\n"
            f"年代：{e.get('year')}\n"
            f"地点：{e.get('location')}\n"
            f"关键人物：{', '.join(e.get('key_figures', []))}\n"
            f"史实摘要：{e.get('summary')}\n"
            f"历史意义：{e.get('significance')}\n"
            f"思政升华：{e.get('reflection')}\n"
        )
    else:
        text = f"主题：{subject}\n（暂无详细背景，请基于明代历史文化宏观把握）"
    if max_chars and len(text) > max_chars:
        text = text[:max_chars].rstrip() + "\n…（上下文截断）"
    return text



if __name__ == "__main__":
    print(f"人物数：{len(FIGURES)}")
    print(f"事件数：{len(EVENTS)}")
    print(f"文化数：{len(CULTURE)}")
    print(f"科技数：{len(SCIENCE)}")
