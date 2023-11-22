import discord
import csv
import os
import re
import random
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
from discord.ext import commands
from discord import File
"------------------------------------------------------------------------"
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.voice_states = True
intents.members = True

draft_host = None
joins_look=False
draft_chk=False
joins_end=False
Finish=False
alst=False
waiting=False
cho=False
draft_participants = []
choices_casts = []
all_casts=[]
selected_casts=[]
user_teams = {}
participant_choices = {}
participant_selection_done=set()
count=1
round=9
que=1

#シリーズに対応する辞書
series_num={
    "2":"初代",
    "3":"水",
    "4":"虹",
    "5":"星",
    "6":"蓮"
}
# シリーズごとのキャストリスト
cast_lists = {
    "初代": ["新田恵海", "南條愛乃", "内田彩", "三森すずこ", "飯田里穂", "Pile", "楠田亜衣奈", "久保ユリカ", "徳井青空"],
    "水": ["伊波杏樹", "逢田梨香子", "諏訪ななか", "小宮有紗", "斉藤 朱夏", "小林愛香", "高槻かなこ", "鈴木愛奈", "降幡愛"],
    "虹": ["大西亜玖璃", "相良茉優", "前田佳織里", "久保田未夢", "村上奈津実", "鬼頭明里", "林鼓子", "指出毬亜", "田中ちえ美", "小泉萌香", "内田秀", "法元明菜", "矢野妃菜喜", "楠木ともり"],
    "星": ["伊達さゆり", "Liyuu", "岬なこ", "ペイトン尚未", "青山なぎさ", "鈴原希実", "薮島朱音", "大熊和奏", "絵森彩", "結那", "坂倉花"],
    "蓮": ["野中ここな", "佐々木琴子", "月音こな", "楡井希実", "菅叶和", "花宮初奈"]
}

async def conduct_lottery(participant_choices, all_casts):
    global cho
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
            cho=True
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

#使ってない
def convert_to_halfwidth(s):
    # 全角スペースと全角数字を半角に変換する変換テーブル
    trans_table = str.maketrans({
        "　": " ",  # 全角スペースを半角スペースに
        "０": "0", "１": "1", "２": "2", "３": "3", "４": "4",
        "５": "5", "６": "6", "７": "7", "８": "8", "９": "9"
    })
    return s.translate(trans_table)

bot = commands.Bot(command_prefix='!', intents=intents)
"------------------------------------------------------------------------"
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # CSVファイルの初期化
    file_path = 'draft_results.csv'
    with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        # ヘッダー行の書き込み
        header = ['参加者', '1巡目', '2巡目', '3巡目', '4巡目', '5巡目', '6巡目', '7巡目', '8巡目', '9巡目']
        writer.writerow(header)

#!joinで参加者を募集、参加、募集停止用のコマンド
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
        await ctx.send("ドラフトの参加受付を終了しました。\n!round {1~9}で遊ぶ回数を変更できます。")
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
#!joins で参加者の一覧を表示できる
@bot.command(name="joins", help="現在のドラフト参加者を表示します")
async def joins(ctx):
    if not draft_participants:
        await ctx.send("現在のドラフトにはまだ参加者がいません。")
        return

    participant_names = [participant.display_name for participant in draft_participants]
    await ctx.send("現在のドラフト参加者:\n" + "\n".join(participant_names))

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

@bot.command(name="start", help="ドラフトの各巡目の開始")
async def draft_start(ctx):
    global draft_participants,que,participant_lists_01,participant_lists_00,que,participant_choices,user_teams,Finish,alst

    if ctx.author != draft_host:
        await ctx.send("あなたはドラフトの開催者ではありません。")
        return
    if not all_casts:
        await ctx.send("遊びたいシリーズを選択してください。!draftで出来ます")
        return 
    if alst:
        await ctx.send("既にドラフトは始まっています。")
        return 
    if not participant_choices:
        participant_choices = {participant.display_name: None for participant in draft_participants}
    if not user_teams:
        user_teams = {participant.display_name: [0]*9 for participant in draft_participants}


    if not draft_participants:
        await ctx.send("ドラフトの参加者がいません。")
        return
    await ctx.send("参加者にリストを割り当てました。")
    if Finish:
        return 
    for participant in draft_participants:
        if participant.dm_channel is None:
            await participant.create_dm()
        await participant.dm_channel.send(f"{que}巡目の希望選択選手です\n以下の選手から希望選択選手を選んでください")
        await participant.dm_channel.send("選択可能選手一覧:\n" "-----------------"+ "\n"+"\n".join(all_casts))
    alst=True
    await ctx.send("全参加者にDMを送信しました。")

@bot.command(name="end", help="ドラフトを終了します")
async def draft_end(ctx):
    global draft_in_progress, draft_host, draft_participants,draft_chk,joins_end,all_casts,participant_choices,que

    if ctx.author != draft_host:
        await ctx.send("あなたはドラフトの開催者ではありません。")
        return

    draft_in_progress = False
    draft_chk = False
    joins_look = False
    joins_end = False
    Finish = False
    waiting = False
    cho = False
    alst = False

    draft_host = None
    draft_participants = []
    participant_choices = {}
    participant_selection_done = set()
    user_teams = {}

    all_casts = []
    choices_casts = []
    selected_casts = []

    que = 1
    count = 1
    round = 9

    await ctx.send("ドラフトが終了しました。")

@bot.event
async def on_message(message):
    global participant_choices, que, selected_casts, all_casts, user_teams, channel,count,waiting,participant_selection_done,cho,round
    channel = bot.get_channel("送信したいチャンネルのID")
    show_list={}
    
    if message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        # メッセージの内容から数字とそれに続くテキストを抽出
        match = re.match(r'(\d+)(.*)', message.content.replace('　', '').replace(' ', ''))
        user = discord.utils.get(bot.users, id=message.author.id)

        if user.display_name in participant_selection_done:
            await user.dm_channel.send("あなたは既に選択を終了しています。")
            return

        if waiting:
            await user.dm_channel.send("まだ待機時間です。")
            return

        if match:
            round_number = int(match.group(1))  # 最初のキャプチャグループがラウンド番号
            cast_name = match.group(2).strip()  # 2番目のキャプチャグループがキャスト名

            if round_number!=que:
                await user.dm_channel.send(f"現在は{que}巡目です。")
                return

            if round_number == que:
                if participant_choices.get(user.display_name) is not None:
                    await user.dm_channel.send(f"{que}巡目で既にあなたは希望を提出しています。")
                    return
                
                if cast_name not in all_casts:
                    await user.dm_channel.send(f"{cast_name}は選択できるキャストではありません。")
                    return

                participant_choices[user.display_name] = cast_name
                await user.dm_channel.send(f"{round_number}巡目に{cast_name}を選択しました。")
                if all(choice is not None for choice in participant_choices.values()):
                    if count==1:
                        await channel.send(".\n"+"-"+f"{que}巡目"+"-")
                    for participant, choice in participant_choices.items():
                        if user_teams[participant][que-1]==0:
                            show_list[participant]=choice
                        else:
                            if participant in show_list:
                                del show_list[participant]
                    await channel.send(f"**{count}**回目の各選択希望選手は以下のとおりです。")
                    choices_text = "\n".join([f"{participant}:【{choice}】" for participant, choice in show_list.items()])
                    await channel.send(choices_text)
                    count+=1
                    lottery_winners = await conduct_lottery(participant_choices, all_casts)
                    if cho:
                        await asyncio.sleep(5)
                        await channel.send("↓重複がありました。抽選の結果↓")
                        cho=False
                    else:
                        await asyncio.sleep(3)
                        await channel.send("↓重複はありませんでした。結果↓")
                    for winner, choice in lottery_winners.items():
                        if user_teams[winner][que-1]==0:
                            await channel.send(f"{winner}が__{choice}__を獲得しました。")
                        user_teams[winner][que-1] = choice
                        if choice in all_casts:
                            all_casts.remove(choice)

                    # 残りの参加者に再選択を促す
                    remaining_participants = [p for p in participant_choices if p not in lottery_winners.keys()]
                    for participant_name in remaining_participants:
                        participant_user = discord.utils.get(bot.users, display_name=participant_name)
                        if participant_user and participant_user.dm_channel:
                            if user_teams[participant_name][que-1] != 0:
                                continue
                            participant_choices[participant_name] = None
                            await participant_user.dm_channel.send(f"外れたため{que}巡目の選択希望選手を選んでください。\n選択可能選手一覧:\n" + "\n".join(all_casts))
                  
                    if all(choice[que-1] != 0 for choice in user_teams.values()):
                        for c in participant_choices:
                            participant_choices[c] = None
                        if len(all_casts) < len(participant_choices) or que >=9:
                            await channel.send("ドラフトが終了しました。\n以下はドラフトの結果です")
                        else:
                            await channel.send("\n"+"---"+f"{que}巡目の全操作が終わりました。以下は各参加者の選択選手です"+"---")
                        csv_file_path = "draft_results.csv"
                        with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                            writer = csv.writer(file)
                            # ヘッダー行を書き込みます。
                            writer.writerow(["巡目"] + [participant for participant in user_teams.keys()])
                            # 各巡目の情報を書き込みます。
                            for i in range(1, round+1):  # 1巡目から9巡目まで
                                writer.writerow([f"{i}巡目"] + [user_teams[participant][i-1] for participant in user_teams.keys()])
                        # PandasでCSVファイルを読み込む
                        df = pd.read_csv(csv_file_path)
                        #weigthsでセルのサイズを変更できる
                        #要調整
                        weights=len(user_teams)*0.40+0.75

                        # Matplotlibでデータを可視化（高解像度で表を描画）
                        plt.figure(figsize=(5*weights, 5*weights), dpi=200)
                        ax = plt.subplot(111, frame_on=False) # 枠線を非表示
                        ax.xaxis.set_visible(False)  # x軸のラベルを非表示
                        ax.yaxis.set_visible(False)  # y軸のラベルを非表示

                        # テーブルを作成
                        table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

                        # テーブルのスタイル調整
                        table.auto_set_font_size(False)
                        table.set_fontsize(10)
                        table.scale(0.5, 1.2) # セルのサイズを調整

                        # 画像ファイルとして保存
                        image_file_path = "draft_results.png"
                        plt.savefig(image_file_path, bbox_inches='tight', pad_inches=0.1)

                        
                        # Discordにアップロードする
                        await channel.send(file=discord.File(image_file_path))
                        # 保存した画像を開く
                        # img = Image.open('draft_results.png')

                        # # 切り取りたい領域の座標を指定（左上のx座標, 左上のy座標, 右下のx座標, 右下のy座標）
                        # crop_area = (100, 100, 400, 400)  # 例としての座標
                        # cropped_img = img.crop(crop_area)

                        # # 切り取った画像を拡大
                        # zoomed_img = cropped_img.resize((800, 800))  # 800x800ピクセルに拡大

                        # # 拡大した画像を保存
                        # zoomed_img.save('zoomed_draft_results.png')

                        # 拡大した画像をDiscordに送信
                        await channel.send(file=discord.File('draft_results.png'))
                        que += 1
                        if len(all_casts) < len(participant_choices) or que > round:
                            await channel.send("ドラフトを自動的に終了しました。")
                            exit()
                        waiting=True
                        await asyncio.sleep(15)
                        waiting=False
                        if not participant_choices:
                            await channel.send("ドラフト参加者が居なくなったため終了しました。\n!eximgで結果を表示できます。")
                            return
                        await channel.send(f"{que}巡目の選択希望選手を送ってください")
                        for participant in participant_choices:
                            user = discord.utils.get(bot.users, display_name=participant)
                            if user and user.dm_channel:
                                await user.dm_channel.send(f"{que}巡目の選択希望選手を送ってください。\n選択可能選手一覧:\n" + "\n".join(all_casts))
                                count=1
    await bot.process_commands(message)


# CSVファイルを生成して送信するコマンド
@bot.command(name="excsv", help="ドラフト結果をCSVファイルで出力します")
async def export_results(ctx):
    global user_teams

    # CSVファイルのパスを設定
    csv_file_path = "draft_results.csv"
    with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        # ヘッダー行を書き込みます。
        writer.writerow(["巡目"] + [participant for participant in user_teams.keys()])
        # 各巡目の情報を書き込みます。
        for i in range(1, round+1):  # 1巡目から9巡目まで
            writer.writerow([f"{i}巡目"] + [user_teams[participant][i-1] for participant in user_teams.keys()])

    # CSVファイルをディスコードにアップロードして送信
    with open(csv_file_path, 'rb') as file:
        await ctx.send("ドラフト結果のCSVファイルです:", file=File(file, "draft_results.csv"))
@bot.command(name="eximg", help="ドラフト結果を画像で出力します")
async def export_image(ctx):
    global user_teams

    # CSVファイルのパスを設定
    csv_file_path = "draft_results.csv"
    with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        # ヘッダー行を書き込みます。
        writer.writerow(["巡目"] + [participant for participant in user_teams.keys()])
        # 各巡目の情報を書き込みます。
        for i in range(1, round+1):  # 1巡目から9巡目まで
            writer.writerow([f"{i}巡目"] + [user_teams[participant][i-1] for participant in user_teams.keys()])
    # PandasでCSVファイルを読み込む
    df = pd.read_csv(csv_file_path)
    #weigthsでセルのサイズを変更できる
    #要調整
    weights=len(user_teams)*0.40+0.75

    # Matplotlibでデータを可視化（高解像度で表を描画）
    plt.figure(figsize=(5*weights, 5*weights), dpi=200)
    ax = plt.subplot(111, frame_on=False) # 枠線を非表示
    ax.xaxis.set_visible(False)  # x軸のラベルを非表示
    ax.yaxis.set_visible(False)  # y軸のラベルを非表示

    # テーブルを作成
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

    # テーブルのスタイル調整
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(0.5, 1.2) # セルのサイズを調整

    # 画像ファイルとして保存
    image_file_path = "draft_results.png"
    plt.savefig(image_file_path, bbox_inches='tight', pad_inches=0.1)

    
    # Discordにアップロードする
    await channel.send(file=discord.File(image_file_path))
    # 保存した画像を開く
    # img = Image.open('draft_results.png')

    # # 切り取りたい領域の座標を指定（左上のx座標, 左上のy座標, 右下のx座標, 右下のy座標）
    # crop_area = (100, 100, 400, 400)  # 例としての座標
    # cropped_img = img.crop(crop_area)

    # # 切り取った画像を拡大
    # zoomed_img = cropped_img.resize((800, 800))  # 800x800ピクセルに拡大

    # # 拡大した画像を保存
    # zoomed_img.save('zoomed_draft_results.png')

    # 拡大した画像をDiscordに送信
    await channel.send(file=discord.File('draft_results.png'))

@bot.command(name="sel_end", help="選択終了コマンド")
async def end_selection(ctx):
    global participant_selection_done, user_teams, que,waiting,participant_choices
    # ユーザーがドラフトに参加しているか確認
    if ctx.author not in draft_participants:
        await ctx.send("あなたはドラフトに参加していません。")
        return
    
    if not waiting:
        await ctx.send("これは待機時間限定のコマンドです。")
        return

    # 選択終了を設定
    participant_selection_done.add(ctx.author.display_name)
    # user_teams内の未選択の選手を「終了」としてマーク
    for i in range(que-1, len(user_teams[ctx.author.display_name])):
        user_teams[ctx.author.display_name][i] = "終了"
    del participant_choices[ctx.author.display_name]
    await ctx.send(f"{ctx.author.display_name}の選択が終了しました。")

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

@bot.command(name='END', help='ボットを停止します。(管理者限定)')
async def end(ctx):
    # コマンドを実行したユーザーが管理者かどうかをチェック
    if ctx.author.guild_permissions.administrator:
        await ctx.send('ボットを停止します。')
        await bot.close()
    else:
        await ctx.send('このコマンドを使用する権限がありません。')
"------------------------------------------------------------------------"
token="YOUR_API_TOKEN"
bot.run(token)
