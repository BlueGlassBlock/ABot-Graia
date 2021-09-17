import time
import random
import asyncio

from graia.saya import Saya, Channel
from graia.application.friend import Friend
from graia.application.group import MemberInfo
from graia.application.group import Group, Member
from graia.application import GraiaMiraiApplication
from graia.application.exceptions import UnknownTarget
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.message.parser.literature import Literature
from graia.application.event.messages import GroupMessage, FriendMessage
from graia.application.message.elements.internal import MessageChain, Plain, Source, Quote, At, Image_UnsafeBytes

from util.RestControl import set_sleep
from util.text2image import create_image
from datebase.db import add_gold, give_all_gold
from config import save_config, yaml_data, group_list, user_black_list

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Literature("1", allow_quote=True, skip_one_at_in_quote=True)]))
async def get_botQueue(app: GraiaMiraiApplication, member: Member, message: MessageChain, source: Source):
    if member.id in yaml_data['Basic']['Permission']['Admin']:
        if message.has(Quote):
            messageid = message.get(Quote)[0].origin.get(Source)[0].id
            try:
                await app.revokeMessage(messageid)
                await app.revokeMessage(source)
            except:
                pass


@channel.use(ListenerSchema(listening_events=[FriendMessage], inline_dispatchers=[Literature("全员充值")]))
async def main(app: GraiaMiraiApplication, friend: Friend, message: MessageChain):
    if friend.id == yaml_data['Basic']['Permission']['Master']:
        saying = message.asDisplay().split()
        await give_all_gold(int(saying[1]))
        await app.sendFriendMessage(friend, MessageChain.create([
            Plain(f"已向所有人充值 {saying[1]} 个游戏币")
        ]))


@channel.use(ListenerSchema(listening_events=[FriendMessage], inline_dispatchers=[Literature("充值")]))
async def main(app: GraiaMiraiApplication, friend: Friend, message: MessageChain):
    if friend.id == yaml_data['Basic']['Permission']['Master']:
        saying = message.asDisplay().split()
        await add_gold(saying[1], int(saying[2]))
        await app.sendFriendMessage(friend, MessageChain.create([
            Plain(f"已向 {saying[1]} 充值 {saying[2]} 个游戏币")
        ]))


@channel.use(ListenerSchema(listening_events=[FriendMessage],
                            inline_dispatchers=[Literature("公告")]))
async def Announcement(app: GraiaMiraiApplication, friend: Friend, message: MessageChain):
    if friend.id == yaml_data['Basic']['Permission']['Master']:
        ft = time.time()
        saying = message.asDisplay().split(" ", 1)
        if len(saying) == 2:
            image = await create_image(saying[1])
            groupList = await app.groupList()
            for group in groupList:
                if group.id not in [885355617, 780537426, 474769367, 690211045, 855895642]:
                    try:
                        await app.sendGroupMessage(group.id, MessageChain.create([
                            Plain(f"公告：{str(group.name)}\n"),
                            Image_UnsafeBytes(image.getvalue())
                        ]))
                    except Exception as err:
                        await app.sendFriendMessage(yaml_data['Basic']['Permission']['Master'], MessageChain.create([
                            Plain(f"{group.id} 的公告发送失败\n{err}")
                        ]))
                    await asyncio.sleep(random.uniform(5, 7))
            tt = time.time()
            times = str(tt - ft)
            await app.sendFriendMessage(friend, MessageChain.create([Plain(f"群发已完成，耗时 {times} 秒")]))


@channel.use(ListenerSchema(listening_events=[FriendMessage],
                            inline_dispatchers=[Literature("添加群白名单")]))
async def add_white_group(app: GraiaMiraiApplication, friend: Friend, message: MessageChain):
    if friend.id == yaml_data['Basic']['Permission']['Master']:
        saying = message.asDisplay().split()
        if len(saying) == 2:
            if int(saying[1]) in group_list['white']:
                await app.sendFriendMessage(friend, MessageChain.create([Plain(f"该群已在白名单中")]))
            else:
                group_list['white'].append(int(saying[1]))
                save_config()
                await app.sendFriendMessage(friend, MessageChain.create([Plain(f"成功将该群加入白名单")]))
        else:
            await app.sendFriendMessage(friend, MessageChain.create([Plain(f"未输入群号")]))


@channel.use(ListenerSchema(listening_events=[FriendMessage],
                            inline_dispatchers=[Literature("取消群白名单")]))
async def remove_white_group(app: GraiaMiraiApplication, friend: Friend, message: MessageChain):
    if friend.id == yaml_data['Basic']['Permission']['Master']:
        saying = message.asDisplay().split()
        if len(saying) == 2:
            if int(saying[1]) not in group_list['white']:
                try:
                    await app.quit(int(saying[1]))
                    await app.sendFriendMessage(friend, MessageChain.create([Plain(f"该群未在白名单中，但成功退出")]))
                except:
                    pass
                else:
                    await app.sendFriendMessage(friend, MessageChain.create([Plain(f"该群未在白名单中")]))
            else:
                group_list['white'].remove(int(saying[1]))
                save_config()
                try:
                    await app.sendGroupMessage(int(saying[1]), MessageChain.create([Plain(f"该群已被移出白名单，将在3秒后退出")]))
                    await asyncio.sleep(3)
                    await app.quit(int(saying[1]))
                except UnknownTarget:
                    pass
                await app.sendFriendMessage(friend, MessageChain.create([Plain(f"成功将该群移出白名单")]))
        else:
            await app.sendFriendMessage(friend, MessageChain.create([Plain(f"未输入群号")]))


@channel.use(ListenerSchema(listening_events=[FriendMessage],
                            inline_dispatchers=[Literature("拉黑用户")]))
async def add_black_user(app: GraiaMiraiApplication, friend: Friend, message: MessageChain):
    if friend.id == yaml_data['Basic']['Permission']['Master']:
        saying = message.asDisplay().split()
        if len(saying) == 2:
            if int(saying[1]) in user_black_list:
                await app.sendFriendMessage(friend, MessageChain.create([Plain(f"该用户已在黑名单中")]))
            else:
                user_black_list.append(int(saying[1]))
                save_config()
                await app.sendFriendMessage(friend, MessageChain.create([Plain(f"成功将该用户加入黑名单")]))
        else:
            await app.sendFriendMessage(friend, MessageChain.create([Plain(f"未输入qq号")]))


@channel.use(ListenerSchema(listening_events=[FriendMessage],
                            inline_dispatchers=[Literature("取消拉黑用户")]))
async def remove_block_user(app: GraiaMiraiApplication, friend: Friend, message: MessageChain):
    if friend.id == yaml_data['Basic']['Permission']['Master']:
        saying = message.asDisplay().split()
        if len(saying) == 2:
            if int(saying[1]) not in user_black_list:
                await app.sendFriendMessage(friend, MessageChain.create([Plain(f"该用户未在黑名单中")]))
            else:
                user_black_list.remove(int(saying[1]))
                save_config()
                await app.sendFriendMessage(friend, MessageChain.create([Plain(f"成功将该用户移出白名单")]))
        else:
            await app.sendFriendMessage(friend, MessageChain.create([Plain(f"未输入qq号")]))


@channel.use(ListenerSchema(listening_events=[GroupMessage],
                            inline_dispatchers=[Literature("拉黑用户")]))
async def add_black_user(app: GraiaMiraiApplication, group: Group, member: Member, message: MessageChain):
    if member.id == yaml_data['Basic']['Permission']['Master']:
        if message.has(At):
            user = message.getFirst(At).target
            if user in user_black_list:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(user),
                    Plain(" 已在黑名单中")
                ]))
            else:
                user_black_list.append(user)
                save_config()
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain("成功将 "),
                    At(user),
                    Plain(" 加入黑名单")
                ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([Plain(f"请at要操作的用户")]))


@channel.use(ListenerSchema(listening_events=[GroupMessage],
                            inline_dispatchers=[Literature("取消拉黑用户")]))
async def remove_block_user(app: GraiaMiraiApplication, group: Group, member: Member, message: MessageChain):
    if member.id == yaml_data['Basic']['Permission']['Master']:
        if message.has(At):
            user = message.getFirst(At).target
            if user not in user_black_list:
                await app.sendGroupMessage(group, MessageChain.create([Plain(f"{user} 未在黑名单中")]))
            else:
                user_black_list.remove(user)
                save_config()
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain("成功将 "),
                    At(user),
                    Plain(" 移出黑名单")
                ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([Plain(f"请at要操作的用户")]))


@channel.use(ListenerSchema(listening_events=[FriendMessage], inline_dispatchers=[Literature("休息")]))
async def Announcement(app: GraiaMiraiApplication, friend: Friend):
    if friend.id == yaml_data['Basic']['Permission']['Master']:
        set_sleep(1)
        await app.sendFriendMessage(friend, MessageChain.create([Plain(f"已进入休息")]))


@channel.use(ListenerSchema(listening_events=[FriendMessage], inline_dispatchers=[Literature("工作")]))
async def Announcement(app: GraiaMiraiApplication, friend: Friend):
    if friend.id == yaml_data['Basic']['Permission']['Master']:
        set_sleep(0)
        await app.sendFriendMessage(friend, MessageChain.create([Plain(f"已开始工作")]))


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Literature("休息")]))
async def Announcement(app: GraiaMiraiApplication, group: Group, member: Member):
    if member.id == yaml_data['Basic']['Permission']['Master']:
        set_sleep(1)
        await app.sendGroupMessage(group, MessageChain.create([Plain(f"已进入休息")]))


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Literature("工作")]))
async def Announcement(app: GraiaMiraiApplication, group: Group, member: Member):
    if member.id == yaml_data['Basic']['Permission']['Master']:
        set_sleep(0)
        await app.sendGroupMessage(group, MessageChain.create([Plain(f"已开始工作")]))


@channel.use(ListenerSchema(listening_events=[FriendMessage], inline_dispatchers=[Literature("群名片修正")]))
async def mute(app: GraiaMiraiApplication, friend: Friend):
    if friend.id == yaml_data['Basic']['Permission']['Master']:
        grouplits = await app.groupList()
        i = 0
        for group in grouplits:
            opt = await app.modifyMemberInfo(member=yaml_data['Basic']['MAH']['BotQQ'],
                                             info=MemberInfo(name=yaml_data['Basic']['BotName']),
                                             group=group.id)
            if opt == None:
                i += 1
            else:
                await app.sendFriendMessage(yaml_data['Basic']['Permission']['Master'], MessageChain.create([
                    Plain(f"群 {group.name}（{group.id}）名片修改失败，请检查后重试")
                ]))
                break
            await asyncio.sleep(0.1)
        await app.sendFriendMessage(yaml_data['Basic']['Permission']['Master'], MessageChain.create([
            Plain(f"共完成 {i} 个群的名片修改。")
        ]))
