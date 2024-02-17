import discord, sqlite3, datetime, random, asyncio, schedule, time
from discord.ext import commands, tasks
from discord import ui
from discord import app_commands 
from discord.ui import Button, View
from discord import ButtonStyle
from datetime import date
from itertools import cycle

status = cycle(["만나서 반갑습니다.", "Nice to meet you."])  

db_path = 'ronadata.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

async def update_database():
    update_query = "UPDATE userdata SET rsplimit = 0"
    cursor.execute(update_query)
    conn.commit()

async def update_database2():
    update_query = "UPDATE userdata SET bljlimit = 0"
    cursor.execute(update_query)
    conn.commit()

@tasks.loop(hours=24)  # 매일 24시간마다 작업 수행
async def scheduled_task():
    await update_database()
    await update_database2()

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False
    async def on_ready(self):
        await self.wait_until_ready()
        change_status.start() 
        if not self.synced: 
            await tree.sync() 
            self.synced = True
        scheduled_task.start()
        schedule.every().day.at("00:12").do(scheduled_task)

        # 봇이 시작할 때 바로 작업을 수행
        await scheduled_task()

        # 스케줄러 시작
        while True:
            await client.wait_until_ready()
            schedule.run_pending()
            await asyncio.sleep(1)

@tasks.loop(seconds=5)    # n초마다 다음 메시지 출력
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

def name_check(name) :
    alr_exist = []
    con = sqlite3.connect('ronadata.db', isolation_level = None)
    cur = con.cursor()
    cur.execute("SELECT name FROM userdata WHERE name = ?", (name,))
    rows = cur.fetchall()
    for i in rows :
        alr_exist.append(i[0])
    if name not in alr_exist :
        return 0
    elif name in alr_exist :
        return 1
    con.close()

def nickname_check(닉네임):
    alr_exist = []
    con = sqlite3.connect('ronadata.db', isolation_level = None)
    cur = con.cursor()
    cur.execute("SELECT nickname FROM userdata WHERE nickname = ?", (닉네임,))
    rows = cur.fetchall()
    for i in rows :
        alr_exist.append(i[0])
    if 닉네임 not in alr_exist :
        return 0
    elif 닉네임 in alr_exist :
        return 1
    con.close()

intents = discord.Intents.all()
client = aclient()
tree = app_commands.CommandTree(client)
token = "MTEwODMxOTIzNDMzOTEzMTM5NQ.GyTcCo.0fXFge1FSUZyxZlNJC4EnHlTaiHw3h7REDXsig"

@tree.command(name='사전가입', description="로나가 돌아오기 전에 먼저 가입하세요!") #명령어와 설명 지정합니다.
async def slash1(interaction: discord.Interaction, 닉네임:str): #명령어와 상호작용합니다.
    name= interaction.user.name
    con = sqlite3.connect("ronadata.db", isolation_level = None)
    cur = con.cursor()
    check = name_check(name)
    now=datetime.datetime.now()
    if check == 0:
        check2 = nickname_check(닉네임)
        if check2 == 0:
            today=date.today()
            jointime=today.strftime("%Y%m%d")
            cur.execute("INSERT INTO userdata VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (interaction.user.name, interaction.user.id, 닉네임, 0, 0, jointime, 0, 0, 0))
            embed=discord.Embed(color=0x000)
            embed.add_field(name="", value=f"{interaction.user.name}님, '{닉네임}'으로 사전가입이 완료되었습니다.")
            embed.set_footer(text=f"{str(now.year)}년 {str(now.month)}월 {str(now.day)}일 {str(now.hour)}시 {str(now.minute)}분")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif check2 == 1:
            embed=discord.Embed(color=0x000)
            embed.add_field(name="", value=f"중복된 닉네임입니다. 다른 닉네임으로 다시 시도해 주세요!")
            embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    elif check == 1:
        embed=discord.Embed(color=0x000)
        cur.execute("SELECT nickname FROM userdata WHERE name = ?", (name,))
        row = cur.fetchone()
        nickname=row[0]
        embed.add_field(name="이미 사전가입이 완료된 계정입니다.", value=f"사용자명:{interaction.user.name}\n닉네임:{nickname}")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    con.close()

@tree.command(name='고객센터', description="문제가 발생하였나요? 고객센터를 이용하세요!") #명령어와 설명 지정합니다.
@app_commands.choices(유형=[
    app_commands.Choice(name="가입 관련 문의", value="가입중에 발생한 오류에 대해 설명해주세요."),
    app_commands.Choice(name="오류 관련 문의", value="로나 이용 중 발생한 오류에 대해 설명해주세요."),])
async def slash2(interaction: discord.Interaction, 유형: app_commands.Choice[str]): #명령어와 상호작용합니다.
    class ModalExample(ui.Modal,title=f"{유형.name}"):
        modal = ui.TextInput(
         label=f"{유형.value}",
         placeholder="자세하게 입력해주세요.", 
         min_length=1,
         max_length=1000,
         required=True,
         style=discord.TextStyle.long,
        )
        async def on_submit(self, interaction):
            embed=discord.Embed(color=0x000)
            embed.add_field(name=f"{유형.name} 도착", value=f"문의자: {interaction.user.name}\n아이디: {interaction.user.id}\n문의내용: {self.modal}")
            await interaction.client.get_channel(1201152182528000064).send(embed=embed)
            await interaction.response.send_message("문의사항이 제출되었습니다. 답변까지 최대 1~2일 소요됩니다.", ephemeral=True)
    await interaction.response.send_modal(ModalExample())
    
@tree.command(name='문의답변', description="🔒ㅣ관리자 전용 명령어 입니다.") #명령어와 설명 지정합니다.
async def slash3(interaction: discord.Interaction, id:str, 답변내용:str): #명령어와 상호작용합니다.
    if interaction.user.name == "iamwooram" or "jeongjin0237" or "000ee2_":
        embed=discord.Embed(color=0x000)
        embed.add_field(name="답변이 도착 했습니다!", value=f"{답변내용}")
        embed.set_footer(text=f"답변자: {interaction.user.name}")
        await interaction.client.get_user(int(id)).send(embed=embed)
        await interaction.response.send_message("답변이 전송되었습니다.", ephemeral=True)
    else:
        embed=discord.Embed(color=0x000)
        embed.add_field(name="", value=f"관리자 전용 명령어 입니다.")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name='내방입장', description="나의 방을 확인하세요.") #명령어와 설명 지정합니다.
async def slash4(interaction: discord.Interaction): #명령어와 상호작용합니다.
    name= interaction.user.name
    con = sqlite3.connect("ronadata.db", isolation_level = None)
    check = name_check(name)
    if check == 0:
        embed=discord.Embed(color=0x000)
        embed.add_field(name="", value=f"가입하지 않은 계정입니다. 가입 후 시도해 주세요.")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif check == 1:
        embed=discord.Embed(color=0x000)
        embed.set_image(url="https://media.discordapp.net/attachments/1200830558104715294/1208389991479382087/IMG_2078.png?ex=65e31be0&is=65d0a6e0&hm=84c2b75b58c61d579cdeb21f67ac9bfa57e0816894f4beec4a5d788988d48963&=&format=webp&quality=lossless&width=1748&height=1194")
        button = Button(label="방 꾸미기", style=ButtonStyle.blurple)
        button2 = Button(label="로나 오픈알림 신청하기", style=ButtonStyle.green)
        view = View()
        view.add_item(button)
        view.add_item(button2)
        await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
        async def button_callback(interaction: discord.Interaction):
            embed=discord.Embed(color=0x000)
            embed.add_field(name="💻 개발 중...", value=f"개발중인 기능으로 사용이 불가능 합니다.")
            embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        button.callback = button_callback
        async def button_callback2(interaction: discord.Interaction):
            con = sqlite3.connect("ronadata.db", isolation_level = None)
            cur = con.cursor()
            cur.execute("SELECT nstatus FROM userdata WHERE name = ?", (name,))
            row = cur.fetchone()
            status=row[0]
            if status == 0:
                cur.execute("UPDATE userdata SET nstatus = ? WHERE name = ?",('1',name))
                await interaction.response.send_message("로나가 정식오픈했을 때 알림을 보내드릴게요!", ephemeral=True)
            elif status == 1:
                embed=discord.Embed(color=0x000)
                embed.add_field(name="", value=f"이미 알림신청이 완료되었습니다.")
                embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            con.close()
        button2.callback = button_callback2
    con.close()

@tree.command(name='친구방입장', description="친구의 방을 확인하세요.") #명령어와 설명 지정합니다.
async def slash4(interaction: discord.Interaction, 닉네임:str): #명령어와 상호작용합니다.
    name= interaction.user.name
    con = sqlite3.connect("ronadata.db", isolation_level = None)
    check = name_check(name)
    if check == 0:
        embed=discord.Embed(color=0x000)
        embed.add_field(name="", value=f"가입하지 않은 계정입니다. 가입 후 시도해 주세요.")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif check == 1:
        embed=discord.Embed(color=0x000)
        embed.add_field(name="💻 개발 중...", value=f"개발중인 기능으로 사용이 불가능 합니다.")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    con.close()

@tree.command(name='구매하기', description="내 방을 꾸미기 위한 배경과 가구를 구매하세요.") #명령어와 설명 지정합니다.
async def slash5(interaction: discord.Interaction): #명령어와 상호작용합니다.
    name= interaction.user.name
    con = sqlite3.connect("ronadata.db", isolation_level = None)
    check = name_check(name)
    if check == 0:
        embed=discord.Embed(color=0x000)
        embed.add_field(name="", value=f"가입하지 않은 계정입니다. 가입 후 시도해 주세요.")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif check == 1:
        embed=discord.Embed(color=0x000)
        embed.add_field(name="💻 개발 중...", value=f"개발중인 기능으로 사용이 불가능 합니다.")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    con.close()

@tree.command(name='가위바위보', description="로나와의 가위바위보에서 승리해 로나머니를 획득하세요.") #명령어와 설명 지정합니다.
async def slash7(interaction: discord.Interaction): #명령어와 상호작용합니다.
    name= interaction.user.name
    con = sqlite3.connect("ronadata.db", isolation_level = None)
    check = name_check(name)
    cur = con.cursor()
    if check == 0:
        embed=discord.Embed(color=0x000)
        embed.add_field(name="", value=f"가입하지 않은 계정입니다. 가입 후 시도해 주세요.")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif check == 1:
        cur.execute("SELECT rsplimit FROM userdata WHERE name = ?", (name,))
        row = cur.fetchone()
        rsplimit=row[0]
        if rsplimit < 3:
            cur.execute("SELECT money FROM userdata WHERE name = ?", (name,))
            row = cur.fetchone()
            money=row[0]
            if money >= 5:
                embed=discord.Embed(color=0x000)
                embed.add_field(name="✌️✊✋ 안내면 진다 가위바위보!", value=f"참가비는 5로나머니 입니다. \n지면 참가비를 잃게 되고,\n이기면 15로나머니를 얻습니다.\n비기면 참가비를 돌려받습니다.\n포기하면 로나머니가 유지되지만 횟수가 1회 증가합니다.")
                button1 = Button(label="✌️ 가위", style=ButtonStyle.green)
                button2 = Button(label="✊ 바위", style=ButtonStyle.green)
                button3 = Button(label="✋ 보", style=ButtonStyle.green)
                button4 = Button(label="❌ 포기", style=ButtonStyle.green)
                view = View()
                view.add_item(button1)
                view.add_item(button2)
                view.add_item(button3)
                view.add_item(button4)
                await interaction.response.send_message(embed=embed, view=view)
                n= random.randint(1, 3)
                async def button_callback1(interaction: discord.Interaction): #가위
                    con = sqlite3.connect("ronadata.db", isolation_level = None)
                    cur = con.cursor()
                    if n == 1:
                        cur.execute("UPDATE userdata SET rsplimit=?  WHERE name = ?",(rsplimit+1, name))
                        embed=discord.Embed(color=0x000)
                        embed.add_field(name="🧐 비겼습니다", value=f"참가비를 돌려받았어요.")
                        button1.disabled = True
                        button2.disabled = True
                        button3.disabled = True
                        button4.disabled = True
                        await interaction.response.edit_message(embed=embed, view=view)
                    elif n == 2:
                        cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money+10, name))
                        cur.execute("UPDATE userdata SET rsplimit=?  WHERE name = ?",(rsplimit+1, name))
                        embed=discord.Embed(color=0x000)
                        embed.add_field(name="😆 이겼습니다!", value=f"15로나머니를 받았습니다!")
                        button1.disabled = True
                        button2.disabled = True
                        button3.disabled = True
                        button4.disabled = True
                        await interaction.response.edit_message(embed=embed, view=view)
                    elif n == 3: 
                        embed=discord.Embed(color=0x000)
                        cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money-5, name))
                        cur.execute("UPDATE userdata SET rsplimit=?  WHERE name = ?",(rsplimit+1, name))
                        embed.add_field(name="😥 졌습니다", value=f"참가비까지 잃었어요..")
                        button1.disabled = True
                        button2.disabled = True
                        button3.disabled = True
                        button4.disabled = True
                        await interaction.response.edit_message(embed=embed, view=view)
                    con.close()
                button1.callback = button_callback1
                async def button_callback2(interaction: discord.Interaction): #바위
                    con = sqlite3.connect("ronadata.db", isolation_level = None)
                    cur = con.cursor()
                    if n == 1:
                        embed=discord.Embed(color=0x000)
                        cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money-5, name))
                        cur.execute("UPDATE userdata SET rsplimit=?  WHERE name = ?",(rsplimit+1, name))
                        embed.add_field(name="😥 졌습니다", value=f"참가비까지 잃었어요..")
                        button1.disabled = True
                        button2.disabled = True
                        button3.disabled = True
                        button4.disabled = True
                        await interaction.response.edit_message(embed=embed, view=view)
                    elif n == 2:
                        cur.execute("UPDATE userdata SET rsplimit=?  WHERE name = ?",(rsplimit+1, name))
                        embed=discord.Embed(color=0x000)
                        embed.add_field(name="🧐 비겼습니다", value=f"참가비를 돌려받았어요.")
                        button1.disabled = True
                        button2.disabled = True
                        button3.disabled = True
                        button4.disabled = True
                        await interaction.response.edit_message(embed=embed, view=view)
                    elif n == 3: 
                        cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money+10, name))
                        cur.execute("UPDATE userdata SET rsplimit=?  WHERE name = ?",(rsplimit+1, name))
                        embed=discord.Embed(color=0x000)
                        embed.add_field(name="😆 이겼습니다!", value=f"15로나머니를 받았습니다!")
                        button1.disabled = True
                        button2.disabled = True
                        button3.disabled = True
                        button4.disabled = True
                        await interaction.response.edit_message(embed=embed, view=view)
                    con.close()
                button2.callback = button_callback2
                async def button_callback3(interaction: discord.Interaction): #보
                    con = sqlite3.connect("ronadata.db", isolation_level = None)
                    cur = con.cursor()
                    if n == 1:
                        cur.execute("UPDATE userdata SET money=? WHERE name = ?",(money+10, name))
                        cur.execute("UPDATE userdata SET rsplimit=?  WHERE name = ?",(rsplimit+1, name))
                        embed=discord.Embed(color=0x000)
                        embed.add_field(name="😆 이겼습니다!", value=f"15로나머니를 받았습니다!")
                        button1.disabled = True
                        button2.disabled = True
                        button3.disabled = True
                        button4.disabled = True
                        await interaction.response.edit_message(embed=embed, view=view)
                    elif n == 2:
                        cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money-5, name))
                        cur.execute("UPDATE userdata SET rsplimit=?  WHERE name = ?",(rsplimit+1, name))
                        embed=discord.Embed(color=0x000)
                        embed.add_field(name="😥 졌습니다", value=f"참가비까지 잃었어요..")
                        button1.disabled = True
                        button2.disabled = True
                        button3.disabled = True
                        button4.disabled = True
                        await interaction.response.edit_message(embed=embed, view=view)
                    elif n == 3: 
                        cur.execute("UPDATE userdata SET rsplimit=?  WHERE name = ?",(rsplimit+1, name))
                        embed=discord.Embed(color=0x000)
                        embed.add_field(name="🧐 비겼습니다", value=f"참가비를 돌려받았어요.")
                        button1.disabled = True
                        button2.disabled = True
                        button3.disabled = True
                        button4.disabled = True
                        await interaction.response.edit_message(embed=embed, view=view)
                    con.close()
                button3.callback = button_callback3
                async def button_callback4(interaction: discord.Interaction): #보
                    con = sqlite3.connect("ronadata.db", isolation_level = None)
                    cur = con.cursor()
                    button1.disabled = True
                    button2.disabled = True
                    button3.disabled = True
                    button4.disabled = True
                    cur.execute("UPDATE userdata SET rsplimit=?  WHERE name = ?",(rsplimit+1, name))
                    embed=discord.Embed(color=0x000)
                    embed.add_field(name="포기했습니다.", value=f"")
                    await interaction.response.edit_message(embed=embed, view=view)
                button4.callback = button_callback4
            else:
                embed=discord.Embed(color=0x000)
                embed.add_field(name="로나머니가 부족한데요..?", value=f"가위바위보를 하기 위해서 최소 5로나머니가 필요해요.")
                embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed=discord.Embed(color=0x000)
            embed.add_field(name="", value=f"가위바위보는 하루에 최대 3번까지 할 수 있어요.\n매일 오전 6시에 초기화 됩니다!")
            embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    con.close()

@tree.command(name='잔고확인', description="현재 가지고있는 머니와 코인의 개수를 확인합니다.") #명령어와 설명 지정합니다.
async def slash8(interaction: discord.Interaction): #명령어와 상호작용합니다.
    name= interaction.user.name
    con = sqlite3.connect("ronadata.db", isolation_level = None)
    check = name_check(name)
    if check == 0:
        embed=discord.Embed(color=0x000)
        embed.add_field(name="", value=f"가입하지 않은 계정입니다. 가입 후 시도해 주세요.")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif check == 1:
        cur = con.cursor()
        cur.execute("SELECT nickname FROM userdata WHERE name = ?", (name,))
        row = cur.fetchone()
        nickname=row[0]
        cur.execute("SELECT money FROM userdata WHERE name = ?", (name,))
        row = cur.fetchone()
        money=row[0]
        cur.execute("SELECT coin FROM userdata WHERE name = ?", (name,))
        row = cur.fetchone()
        coin=row[0]
        embed=discord.Embed(color=0x000)
        embed.add_field(name=f"{nickname}님의 잔고", value=f"<:rona_money:1202971554582106112> 로나머니: {money}(개)\n<:rona_coin:1202971577784991794> 로나코인: {coin}(개)")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    con.close()

def get_ranking():
    con = sqlite3.connect("ronadata.db")
    cur = con.cursor()
    cur.execute(f"SELECT nickname, money, coin From userdata ORDER BY money DESC LIMIT 10")
    ranking = cur.fetchall()
    con.close()
    return ranking

@tree.command(name='랭킹', description="로나봇의 랭킹을 확인하세요.") #명령어와 설명 지정합니다.
@app_commands.choices(유형=[
    app_commands.Choice(name="잔고", value="가입중에 발생한 오류에 대해 설명해주세요."),])
async def slash9(interaction: discord.Interaction, 유형: app_commands.Choice[str]): #명령어와 상호작용합니다.
    name= interaction.user.name
    con = sqlite3.connect("ronadata.db", isolation_level = None)
    check = name_check(name)
    if check == 0:
        embed=discord.Embed(color=0x000)
        embed.add_field(name="", value=f"가입하지 않은 계정입니다. 가입 후 시도해 주세요.")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif check == 1:
        if 유형.name == "잔고":
            ranking = get_ranking()
            embed = discord.Embed(title="잔고 랭킹", description="잔고 랭킹 상위 10명입니다", color=0x000)
            embed.add_field(name=f"", value=f"====================", inline=False)
            prev_money = None
            prev_rank = 0
            num_equal = 0
            for i, (nickname, money, coin) in enumerate(ranking):
                if prev_money is None or money != prev_money:
                    prev_money = money
                    prev_rank += num_equal + 1
                    num_equal = 0
                else:
                    num_equal += 1
                embed.add_field(name=f"#{prev_rank}", value=f"{nickname} - 머니/코인: {money}/{coin}", inline=False)
            embed.add_field(name=f"", value=f"====================", inline=False)
            embed.set_footer(text=f"순위는 로나머니 개수에 따라 결정됩니다.\n문제가 발생하면 '/고객센터'를 통해 문의해 주세요.")
            await interaction.response.send_message(embed=embed)
        else:
            embed=discord.Embed(color=0x000)
            embed.add_field(name="💻 개발 중...", value=f"개발중인 기능으로 사용이 불가능 합니다.")
            embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    con.close()

@tree.command(name='탈퇴', description="로나봇 서비스를 탈퇴합니다.") #명령어와 설명 지정합니다.
async def slash10(interaction: discord.Interaction): #명령어와 상호작용합니다.
    embed=discord.Embed(color=0x000)
    embed.add_field(name="", value=f"팀 로티즈는 로나봇의 서비스 탈퇴를 도와드리고 있습니다.\n'/고객센터'를 통해 문의해 주세요.")
    await interaction.response.send_message(embed=embed, ephemeral=True)


deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4

# 카드를 뽑는 함수
def draw_card():
    refill_deck()  # 덱이 비어있으면 새로운 카드 채움
    return deck.pop()

# 덱이 비어있을 때 새로운 카드로 채우는 함수
def refill_deck():
    if not deck:
        deck.extend([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4)
        random.shuffle(deck)

# 카드를 나눠주는 함수
def deal(deck):
    hand = []
    for _ in range(2):
        hand.append(draw_card())
    return hand

# 합을 계산하는 함수
def calculate_score(hand):
    score = sum(hand)
    if score > 21 and 11 in hand:
        hand.remove(11)
        hand.append(1)
        score = sum(hand)
    return score

@tree.command(name='블랙잭', description="로나와 함께하는 블랙잭!") #명령어와 설명 지정합니다.
async def slash11(interaction: discord.Interaction, 배팅금액:int): #명령어와 상호작용합니다.
    name= interaction.user.name
    con = sqlite3.connect("ronadata.db", isolation_level = None)
    check = name_check(name)
    if check == 0:
        embed=discord.Embed(color=0x000)
        embed.add_field(name="", value=f"가입하지 않은 계정입니다. 가입 후 시도해 주세요.")
        embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif check == 1:
        cur=con.cursor()
        cur.execute("SELECT bljlimit FROM userdata WHERE name = ?", (name,))
        row = cur.fetchone()
        bljlimit=row[0]
        if bljlimit < 5:
            if 배팅금액 < 5:
                embed=discord.Embed(color=0x000)
                embed.add_field(name="", value=f"최소 배팅 금액은 5로나머니 입니다.")
                embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            elif 배팅금액 > 1000:
                embed=discord.Embed(color=0x000)
                embed.add_field(name="", value=f"최대 배팅 금액은 1000로나머니 입니다.")
                embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                cur=con.cursor()
                cur.execute("SELECT money FROM userdata WHERE name = ?", (name,))
                row = cur.fetchone()
                money=row[0]
                if money >= 배팅금액:
                    player_hand = deal(deck)
                    dealer_hand = deal(deck)

                    player_score = calculate_score(player_hand)
                    dealer_score = calculate_score(dealer_hand)  # 마지막 패는 감추기
                    embed = discord.Embed(color=0x000, title=f"블랙잭 시작! (배팅금액: {배팅금액})")
                    embed.add_field(name=f"{interaction.user.name}님의 패 ({player_score})", value=', '.join(map(str, player_hand)), inline=False)
                    embed.add_field(name=f"딜러의 패 (?)", value=f"{dealer_hand[0]}, ?", inline=False)
                    button = Button(label="히트 (카드 뽑기)", style=ButtonStyle.green)
                    button2 = Button(label="스탠드 (차례 마치기)", style=ButtonStyle.green)
                    button3 = Button(label="서렌더 (포기)", style=ButtonStyle.green)
                    view = View()
                    view.add_item(button)
                    view.add_item(button2)
                    view.add_item(button3)
                    await interaction.response.send_message(embed=embed, view=view)
                    async def button_callback1(interactions: discord.Interaction):
                        name= interaction.user.name
                        con = sqlite3.connect("ronadata.db", isolation_level = None)
                        cur=con.cursor()
                        cur.execute("SELECT money FROM userdata WHERE name = ?", (name,))
                        row = cur.fetchone()
                        money=row[0]
                        nonlocal player_hand, player_score, dealer_hand, dealer_score, view
                        player_hand.append(deck.pop())
                        player_score = calculate_score(player_hand)
                        await interaction.response.edit_message(embed=update_embed(interaction, 배팅금액, player_score, player_hand, dealer_hand), view=view)
                        if player_score > 21:
                            button.disabled = True
                            button2.disabled = True
                            button3.disabled = True
                            cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money-배팅금액, name))
                            cur.execute("UPDATE userdata SET bljlimit=?  WHERE name = ?",(bljlimit+1, name))
                            await interaction.edit_original_response(embed=update_embed2(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_hand), view=view)
                        elif player_score == 21:
                            button.disabled = True
                            button2.disabled = True
                            button3.disabled = True
                            cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money+배팅금액*0.5, name))
                            cur.execute("UPDATE userdata SET bljlimit=?  WHERE name = ?",(bljlimit+1, name))
                            await interaction.edit_original_response(embed=update_embed3(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_hand), view=view)
                        else:
                            None
                        con.close()
                    button.callback = button_callback1
                    async def button_callback2(interaction: discord.Interaction):
                            name= interaction.user.name
                            con = sqlite3.connect("ronadata.db", isolation_level = None)
                            cur=con.cursor()
                            cur.execute("SELECT money FROM userdata WHERE name = ?", (name,))
                            row = cur.fetchone()
                            money=row[0]
                            nonlocal player_hand, player_score, dealer_hand, dealer_score, view
                            while dealer_score < 17:
                                dealer_hand.append(deck.pop())
                                dealer_score = calculate_score(dealer_hand)  # 마지막 패는 감추기
                            dealer_cards = ', '.join(map(str, dealer_hand))
                            if dealer_score > 21:
                                button.disabled = True
                                button2.disabled = True
                                button3.disabled = True
                                cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money+배팅금액*0.5, name))
                                cur.execute("UPDATE userdata SET bljlimit=?  WHERE name = ?",(bljlimit+1, name))
                                await interaction.response.edit_message(embed=update_embed4(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_cards), view=view)
                            elif dealer_score < player_score:
                                button.disabled = True
                                button2.disabled = True
                                button3.disabled = True
                                cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money+배팅금액*0.5, name))
                                cur.execute("UPDATE userdata SET bljlimit=?  WHERE name = ?",(bljlimit+1, name))
                                await interaction.response.edit_message(embed=update_embed5(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_cards), view=view)
                            elif dealer_score > player_score:
                                button.disabled = True
                                button2.disabled = True
                                button3.disabled = True
                                cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money-배팅금액, name))
                                cur.execute("UPDATE userdata SET bljlimit=?  WHERE name = ?",(bljlimit+1, name))
                                await interaction.response.edit_message(embed=update_embed6(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_cards), view=view)
                            else:
                                button.disabled = True
                                button2.disabled = True
                                button3.disabled = True
                                cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money+배팅금액*0.5, name))
                                cur.execute("UPDATE userdata SET bljlimit=?  WHERE name = ?",(bljlimit+1, name))
                                await interaction.response.edit_message(embed=update_embed7(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_cards), view=view)
                            con.close()
                    button2.callback = button_callback2
                    async def button_callback3(interaction: discord.Interaction):
                        name= interaction.user.name
                        con = sqlite3.connect("ronadata.db", isolation_level = None)
                        cur=con.cursor()
                        cur.execute("SELECT money FROM userdata WHERE name = ?", (name,))
                        row = cur.fetchone()
                        money=row[0]
                        button.disabled = True
                        button2.disabled = True
                        button3.disabled = True
                        cur.execute("UPDATE userdata SET money=?  WHERE name = ?",(money-배팅금액/2, name))
                        cur.execute("UPDATE userdata SET bljlimit=?  WHERE name = ?",(bljlimit+1, name))
                        await interaction.response.edit_message(embed=update_embed8(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_hand), view=view)
                        con.close()
                    button3.callback = button_callback3
                else:
                    embed=discord.Embed(color=0x000)
                    embed.add_field(name="로나머니가 부족한데요..?", value=f"가지고 계신 로나머니가 배팅금액 보다 적어요.")
                    embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
        else: 
            embed=discord.Embed(color=0x000)
            embed.add_field(name="", value=f"블랙잭은 하루에 최대 5번까지 할 수 있어요.\n매일 오전 6시에 초기화 됩니다!")
            embed.set_footer(text=f"해당 문제가 오류라고 생각되면 '/고객센터'를 통해 문의해 주세요.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    con.close()

def update_embed(interaction, 배팅금액, player_score, player_hand, dealer_hand): #embed
    embed = discord.Embed(color=0x000, title=f"블랙잭 게임 중 (배팅금액: {배팅금액})")
    embed.add_field(name=f"{interaction.user.name}님의 패 ({player_score})", value=', '.join(map(str, player_hand)), inline=False)
    embed.add_field(name=f"딜러의 패 (?)", value=f'{dealer_hand[0]}, ?', inline=False)
    return embed
def update_embed2(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_hand): #win
    embed = discord.Embed(color=0x000, title=f"블랙잭 종료! (배팅금액: {배팅금액})")
    embed.add_field(name=f"{interaction.user.name}님의 패 ({player_score})", value=', '.join(map(str, player_hand)), inline=False)
    embed.add_field(name=f"딜러의 패 ({dealer_score})", value=', '.join(map(str, dealer_hand)), inline=False)
    embed.set_footer(text=f"결과: 플레이어가 21을 넘어서 딜러가 승리했습니다.\n{배팅금액}로나머니를 잃었습니다.")
    return embed
def update_embed3(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_hand): #win
    embed = discord.Embed(color=0x000, title=f"블랙잭 종료! (배팅금액: {배팅금액})")
    embed.add_field(name=f"{interaction.user.name}님의 패 ({player_score})", value=', '.join(map(str, player_hand)), inline=False)
    embed.add_field(name=f"딜러의 패 ({dealer_score})", value=', '.join(map(str, dealer_hand)), inline=False)
    embed.set_footer(text=f"결과: 플레이어가 21을 완성하여 블랙잭으로 승리하였습니다.\n{배팅금액}x1.5 로나머니를 얻었습니다.")
    return embed
def update_embed4(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_cards): #win
    embed = discord.Embed(color=0x000, title=f"블랙잭 종료! (배팅금액: {배팅금액})")
    embed.add_field(name=f"{interaction.user.name}님의 패 ({player_score})", value=', '.join(map(str, player_hand)), inline=False)
    embed.add_field(name=f"딜러의 패 ({dealer_score})", value=dealer_cards, inline=False)
    embed.set_footer(text=f"결과: 딜러가 21을 넘어서 플레이어가 승리했습니다.\n{배팅금액}x1.5 로나머리를 얻었습니다")
    return embed
def update_embed5(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_cards): #win
    embed = discord.Embed(color=0x000, title=f"블랙잭 종료! (배팅금액: {배팅금액})")
    embed.add_field(name=f"{interaction.user.name}님의 패 ({player_score})", value=', '.join(map(str, player_hand)), inline=False)
    embed.add_field(name=f"딜러의 패 ({dealer_score})", value=dealer_cards, inline=False)
    embed.set_footer(text=f"결과: 플레이어가 딜러보다 합이 높아 플레이어가 승리했습니다.\n{배팅금액}x1..5 로나머리를 얻었습니다")
    return embed
def update_embed6(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_cards): #lose
    embed = discord.Embed(color=0x000, title=f"블랙잭 종료! (배팅금액: {배팅금액})")
    embed.add_field(name=f"{interaction.user.name}님의 패 ({player_score})", value=', '.join(map(str, player_hand)), inline=False)
    embed.add_field(name=f"딜러의 패 ({dealer_score})", value=dealer_cards, inline=False)
    embed.set_footer(text=f"결과: 딜러가 플레이어보다 합이 높아 딜러가 승리했습니다\n{배팅금액}로나머니를 잃었습니다.")
    return embed
def update_embed7(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_cards): #draw
    embed = discord.Embed(color=0x000, title=f"블랙잭 종료! (배팅금액: {배팅금액})")
    embed.add_field(name=f"{interaction.user.name}님의 패 ({player_score})", value=', '.join(map(str, player_hand)), inline=False)
    embed.add_field(name=f"딜러의 패 ({dealer_score})", value=dealer_cards, inline=False)
    embed.set_footer(text=f"결과: 플레이어와 딜러의 합이 같아 비겼습니다.\n{배팅금액}로나머니를 돌려받았습니다.")
    return embed
def update_embed8(interaction, 배팅금액, player_score, player_hand, dealer_score, dealer_hand): #lose
    embed = discord.Embed(color=0x000, title=f"블랙잭 종료! (배팅금액: {배팅금액})")
    embed.add_field(name=f"{interaction.user.name}님의 패 ({player_score})", value=', '.join(map(str, player_hand)), inline=False)
    embed.add_field(name=f"딜러의 패 ({dealer_score})", value=', '.join(map(str, dealer_hand)), inline=False)
    embed.set_footer(text=f"결과: 플레이어가 포기해 딜러가 승리했습니다.\n{배팅금액}x0.5 로나머리를 돌려받았습니다.")
    return embed

client.run(token)