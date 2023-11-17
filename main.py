import discord
import random
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.voice_states = True
intents.members = True

# シリーズごとのキャストリスト
cast_lists = {
    "初代": ["新田恵美", "南條愛乃", "内田彩", "三森すずこ", "飯田里穂", "Pile", "楠田亜衣奈", "久保ユリカ", "徳井青空"],
    "水": ["伊波杏樹", "逢田梨香子", "諏訪ななか", "小宮有紗", "斎藤朱夏", "小林愛香", "高槻かなこ", "鈴木愛奈", "降幡愛"],
    "虹": ["大西亜玖璃", "相良茉優", "前田佳織里", "久保田未夢", "村上奈津実", "鬼頭明里", "林鼓子", "指出毬亜", "田中ちえ美", "小泉萌香", "内田秀", "法元明菜", "矢野妃菜喜", "楠木ともり"],
    "星": ["伊達さゆり", "Liyuu", "岬なこ", "ペイトン尚未", "青山なぎさ", "鈴原希実", "藪島朱音", "大熊和奏", "絵森彩", "結那", "坂倉花"],
    "蓮": ["野中ここな", "佐々木琴子", "月音こな", "楡井希実", "菅叶和", "花宮初奈"]
}
series_num={
    "2":"初代",
    "3":"水",
    "4":"虹",
    "5":"星",
    "6":"蓮"
}

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

draft_host = None
draft_participants = []
choices_casts = []
all_casts=[]
joins_look=False
draft_chk=False
joins_end=False
selected_casts=[]
user_teams = {}

# 参加者とリストを紐付けるための辞書(最終的なものはこっち)
participant_lists_01 = {
    1:"",
    2:"",
    3:"",
    4:"",
    5:"",
    6:"",
    7:"",
    8:"",
    9:""}
# 参加者とリストを紐付けるための辞書(抽選に用いる)
participant_lists_00 = {
    1:"",
    2:"",
    3:"",
    4:"",
    5:"",
    6:"",
    7:"",
    8:"",
    9:""}

@bot.command(name="join", help="ドラフトを開始または参加します")
async def join(ctx, *, arg=""):
    global draft_host, draft_participants,joins_look,joins_end
    if draft_chk:
        await ctx.send("ドラフト開催中です。開催者のみが!draft endでドラフトを終了できます")
        return
    # ドラフトの開催者を設定
    if joins_end:
        await ctx.send("既に募集は締め切られています")
        return
    if arg == "":
        if joins_look:
            await ctx.send("重複してドラフトの参加者を募集することは出来ません")
            return
        draft_host = ctx.author
        draft_participants = []
        joins_look=True
        await ctx.send(f"{ctx.author.display_name}さんによってドラフトが開かれます。'!join draft'で参加、'!join q'で参加受付終了。")
        return

    # 参加受付終了
    if arg == "q":
        if ctx.author != draft_host:
            await ctx.send("あなたはドラフトの開催者ではありません。")
            return
        await ctx.send("ドラフトの参加受付を終了しました。")
        joins_look=False
        joins_end=True
        return

    # ドラフトへの参加
    if arg == "draft":
        if draft_host is None:
            await ctx.send("現在開かれているドラフトはありません。")
            return
        if ctx.author in draft_participants:
            await ctx.send("あなたは既に参加しています。")
            return
        draft_participants.append(ctx.author)
        await ctx.send(f"{ctx.author.display_name}の参加が認められました。")
    
@bot.command(name="joins", help="現在のドラフト参加者を表示します")
async def joins(ctx):
    if not draft_participants:
        await ctx.send("現在のドラフトにはまだ参加者がいません。")
        return

    participant_names = [participant.display_name for participant in draft_participants]
    await ctx.send("現在のドラフト参加者:\n" + "\n".join(participant_names))

choices_casts=[]

@bot.command(name="draft", help="ドラフトを開きます")
async def draft(ctx):
    global choices_casts,draft_chk,draft_participants
    choices_casts.clear()
    draft_nex=True
    if joins_look:
        await ctx.send("ドラフトは現在参加者を募集中です。打ち切りたい場合は'!join q'をお願いします")
        return
    if draft_host is None or ctx.author != draft_host:
        await ctx.send(f"ドラフトの開催者がいません、または{ctx.author.display_name}さんは開催者ではありません。")
        return
    # ドラフトの開催者のみ実行可能
    if ctx.author != draft_host:
        await ctx.send(f"{draft_host.display_name}さん以外にdraftの入力は行えません")
        return
    if draft_chk:
        await ctx.send("既にドラフトは開催しています。")
        return
    # ユーザーに選択肢を提示
    alls=False
    await ctx.send("1:全部, 2:初代, 3:水, 4:虹, 5:星, 6:蓮, 7:複数選択\n遊びたいシリーズを選んでください:")

    # ユーザーの応答を待つ
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        message = await bot.wait_for('message', check=check, timeout=60.0)  # 60秒でタイムアウト
    except asyncio.TimeoutError:
        await ctx.send('タイムアウトしました。')
        return
    else:
        inputs = message.content

        if inputs not in ["1","2","3","4","5","6","7"]:
            await ctx.send("正しい入力でお願いします。")
            await ctx.send("もう一度最初の入力から行ってください。")
            draft_nex=False
            return
        if inputs == "1":
            await ctx.send("全部が選択されました")
            choices_casts.extend(list(map(str,range(2,7))))
            alls=True
        elif inputs in ["2", "3", "4", "5", "6"]:
            if inputs not in choices_casts:
                choices_casts.append(inputs)

        if inputs == "7":
            await ctx.send("複数選択です。以下に入力が続きます。")
            await ctx.send("2:初代, 3:水, 4:虹, 5:星, 6:蓮の中から複数選んでください")

            try:
                ext_message = await bot.wait_for('message', check=check, timeout=60.0)  # 60秒でタイムアウト
            except asyncio.TimeoutError:
                await ctx.send('タイムアウトしました。')
                return
            else:
                ext = ext_message.content.split(',')  # カンマで分割
                series_names = {
                    "2": "初代",
                    "3": "水",
                    "4": "虹",
                    "5": "星",
                    "6": "蓮"
                }
            
                # 入力がすべて有効かチェック
                if all(n.strip() in series_names for n in ext):
                    selected_series = [series_names[n.strip()] for n in ext]
                    choices_casts=ext
                else:
                    await ctx.send("正しい入力でお願いします。")
                    await ctx.send("もう一度最初の入力から行ってください。")
                    draft_nex=False
                    return
                choices_casts.sort()
        for st in choices_casts:
            all_casts.extend(cast_lists[series_num[st]])
    if draft_nex:
        await ctx.send("以下のシリーズがえらばれました")

        tx=[]
        for ss in choices_casts:
            tx.append(series_num[ss])
        await ctx.send(f"シリーズ: {', '.join(tx)}")
        await ctx.send("参加者は以下の通りです。")
        await ctx.send(f"参加者: {', '.join([participant.display_name for participant in draft_participants])}")
    draft_chk=True

participant_choices = {}

@bot.command(name="start", help="ドラフトの各巡目の開始")
async def draft_start(ctx):
    global draft_participants,que,participant_lists_01,participant_lists_00,que,participant_choices,user_teams

    if ctx.author != draft_host:
        await ctx.send("あなたはドラフトの開催者ではありません。")
        return
    if not all_casts:
        await ctx.send("遊びたいシリーズを選択してください")
        return 
    if not participant_choices:
        participant_choices = {participant.display_name: None for participant in draft_participants}
    if not user_teams:
        user_teams = {participant.display_name: [0]*9 for participant in draft_participants}


    if not draft_participants:
        await ctx.send("ドラフトの参加者がいません。")
        return
    await ctx.send("参加者にリストを割り当てました。")
    for participant in draft_participants:
        if participant.dm_channel is None:
            await participant.create_dm()
        await participant.dm_channel.send(f"{que}巡目の希望選択選手です\n以下の選手から希望選択選手を選んでください")
        await participant.dm_channel.send("選択可能選手一覧:\n" "-----------------"+ "\n"+"\n".join(all_casts))

    await ctx.send("全参加者にDMを送信しました。")

@bot.command(name="show_casts", help="選択したシリーズのキャストを表示します")
async def show_casts(ctx, *, series_numbers):
    selected_series = series_numbers.split(',')
    for series_number in selected_series:
        series_number = series_number.strip()
        if series_number in series_num:
            await ctx.send(f"シリーズ番号{series_number} のキャスト({series_num[series_number]}):\n" + "\n".join(cast_lists[series_num[series_number]]))
        else:
            await ctx.send(f"シリーズ番号 {series_number} は存在しません。")

@bot.command(name="sh", help="選択されたシリーズの詳細を表示します")
async def show(ctx, *, arg):
    # `choices_casts`の中身がすべて文字列であることを前提とする
    if arg == "cast_num":
        outputs=[]
        if len(choices_casts)==1:
            outputs.append(series_num[choices_casts[0]])
        else:
            for n in choices_casts:
                outputs.append(series_num[n])
        await ctx.send(f"選択されたシリーズ: {', '.join(outputs)}")
    elif arg == "casts":
        await ctx.send("選択されたキャスト:\n" + "\n".join(all_casts))

@bot.command(name="end", help="ドラフトを終了します")
async def draft_end(ctx):
    global draft_in_progress, draft_host, draft_participants,draft_chk,joins_end,all_casts,participant_choices,que

    if ctx.author != draft_host:
        await ctx.send("あなたはドラフトの開催者ではありません。")
        return

    draft_in_progress = False
    draft_host = None
    draft_participants.clear()
    draft_chk=False
    joins_look=False
    joins_end=False
    all_casts=[]
    participant_choice={}
    que=1
    draft_host = None
    draft_participants = []
    choices_casts = []
    all_casts=[]
    joins_look=False
    draft_chk=False
    joins_end=False
    selected_casts=[]
    user_teams = {}
    await ctx.send("ドラフトが終了しました。")

async def conduct_lottery(participant_choices, all_casts):
    # 各キャストに対する参加者リストを作成
    cast_to_participants = {}
    for participant, cast in participant_choices.items():
        if cast not in cast_to_participants:
            cast_to_participants[cast] = []
        cast_to_participants[cast].append(participant)

    # 抽選結果を格納する辞書
    lottery_results = {}

    # 抽選の実施
    for cast, participants in cast_to_participants.items():
        if len(participants) > 1:
            # 複数の参加者がいる場合は抽選
            winner = random.choice(participants)
            lottery_results[winner] = cast
            # 選ばれたキャストを all_casts から削除
            if cast in all_casts:
                all_casts.remove(cast)
        else:
            # 参加者が1人だけの場合はその人が当選
            lottery_results[participants[0]] = cast
            # 選ばれたキャストを all_casts から削除
            if cast in all_casts:
                all_casts.remove(cast)

    return lottery_results
@bot.event
async def on_message(message):
    global participant_choices, que, selected_casts, all_casts, user_teams
    channel = bot.get_channel(1174980268046696599)

    if message.author.bot:
        return
    
    if isinstance(message.channel, discord.DMChannel):
        user = discord.utils.get(bot.users, id=message.author.id)
        content = message.content.split(" ", 1)

        if len(content) == 2 and content[0].isdigit():
            round_number = int(content[0])
            cast_name = content[1]

            if round_number == que:
                # 既に選択が行われているか確認
                if participant_choices.get(user.display_name) is not None:
                    await user.dm_channel.send(f"{que}巡目で既にあなたは希望を提出しています。")
                    return
                
                if cast_name not in all_casts:
                    await user.dm_channel.send(f"{cast_name}は選択できるキャストではありません。")
                    return

                participant_choices[user.display_name] = cast_name
                await user.dm_channel.send(f"{round_number}巡目に{cast_name}を選択しました。")
                
                if all(choice is not None for choice in participant_choices.values()):
                    await channel.send(f"{que}巡目の各選択希望選手は以下のとおりです。")
                    choices_text = "\n".join([f"{participant}: {choice}" for participant, choice in participant_choices.items()])
                    await channel.send(choices_text)

                    lottery_winners = await conduct_lottery(participant_choices, all_casts)

                    # チャンネルに抽選結果を報告
                    for winner, choice in lottery_winners.items():
                        await channel.send(f"{winner}が{choice}を引きました。")
                        user_teams[winner][que-1] = choice
                        if choice in all_casts:
                            all_casts.remove(choice)
                    # 残りの参加者に再選択を促す
                    remaining_participants = [p for p in participant_choices if p not in lottery_winners.keys()]
                    for participant in remaining_participants:
                        if user and user.dm_channel:
                            if user_teams[user.display_name][que-1]!=0:
                                return 
                            participant_choices[user.display_name]=None
                            await user.dm_channel.send(f"外れたため{que}巡目の選択希望選手を選んでください。\n選択可能選手一覧:\n" + "\n".join(all_casts))
                    if all(choice[que-1] != 0 for choice in user_teams.values()):
                        que += 1
                    # 全参加者に新しい巡目の選択肢を送信
                        for participant in participant_choices:
                            user = discord.utils.get(bot.users, display_name=participant)
                            if user and user.dm_channel:
                                await user.dm_channel.send(f"{que}巡目の選択希望選手を送ってください。\n選択可能選手一覧:\n" + "\n".join(all_casts))
    
                            # 全員の打線が組み終わったか、キャストがなくなった場合にドラフトを終了
                        if not all_casts or que > 9:
                            await channel.send("ドラフトが終了しました。")
                            return  # または他の適切な処理を行う

                        for c in participant_choices:
                            participant_choices[c] = None

                        for name in user_teams:
                            await channel.send(f"{name}の打線")
                            await channel.send("\n".join(p for p in user_teams[name] if p != 0))

                        await channel.send(f"{que}巡目の選択希望選手を送ってください")
    await bot.process_commands(message)

que=1

@bot.command(name="show_lists", help="参加者のリストを表示")
async def show_lists(ctx):
    global participant_lists_00,participant_lists_01

    if not participant_lists_01:
        await ctx.send("参加者のリストが割り当てられていません。")
        return

    list_display = "\n".join([f"{name}: {lst}" for name, lst in participant_lists_01.items()])
    await ctx.send(f"現在のドラフト参加者とリスト:\n{list_display}")

@bot.command(name='randomword', help='ランダムな単語を発す')
async def randomword(ctx):
    words = ['りんご', 'バナナ', 'ねこ', 'いぬ', 'コンピュータ', '空', '海', '本', 'ペン']
    random_word = random.choice(words)
    await ctx.send(random_word)

token="YOUR_API_TOKEN"
bot.run(token)
