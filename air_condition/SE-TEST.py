import pandas as pd
import argparse
import time
import threading
from fastapi import Depends
from sql_app.database import get_db, SessionLocal
import requests
from typing import List
import json
FILENAME = './test_case_empty.xlsx'

url = None
port = None

room_map = {
    '房间1': 101,
    '房间2': 102,
    '房间3': 103,
    '房间4': 104,
    '房间5': 105,
}

def read_excel_case(filename):
    df = pd.read_excel(filename, sheet_name='测试用例')
    return df.iloc[2:28, 0:6]
class Action:
    def __init__(self, room_id: str, input: str):
        self.room_id = int(room_id)
        self.input = input
        
    def post(self):
        db_session=get_db()
        if self.input == '开机' or self.input == '关机':
            self.api = '/schedule/request_on' if self.input == '开机' else '/schedule/request_off'
            params = {
                'room_id': self.room_id
            }
            requests.post(url + ':' + str(port) + self.api+'?room_id=' + str(self.room_id))
        elif self.input == '高' or self.input == '中' or self.input == '低':
            self.api = '/schedule/request_speed'
            speed_map = {
                '高': "high",
                '中': "medium",
                '低': "low"
            }
            requests.post(url + ':' + str(port) + self.api+'?room_id=' + str(self.room_id)+'&fan_speed='+speed_map[self.input])
        else:
            self.api = '/schedule/request_temp'
            requests.post(url + ':' + str(port) + self.api+'?room_id=' + str(self.room_id)+'&target_temperature='+str(self.input))
        

time_lock = [False] * 26
condition = threading.Condition()


def thread_request(actions: List[List[Action]]):
    global time_lock, condition
    try:
        # 发起请求
        for idx, action_list in enumerate(actions):
            for action in action_list:
                print('第%d分钟，%d，%s' % (idx, action.room_id, action.input))
                try:
                    action.post()
                except Exception as e:
                    print(f"请求失败: {e}")
                    exit(0)
        
            with condition:
                time_lock[idx] = True
                condition.notify_all()
            time.sleep(10)
    except KeyboardInterrupt:
        print("线程请求被中断")
        return

roomInfo = None
scheduleInfo = None

def thread_query(actions):
    global time_lock, condition
    try:
        api_room_info = '/user/show/'
        df_rooms = pd.DataFrame()
        df_schedule = pd.DataFrame()
        for idx, _ in enumerate(actions):
            with condition:
                condition.wait_for(lambda: time_lock[idx])
            print('第%d分钟' % idx)
            tmp_df = pd.DataFrame()
            for room_id in room_map.values():
                params = {
                'room_id': room_id
                }
                try:
                    res = requests.get(url + ':' + str(port) + api_room_info+str(room_id), timeout=5)
                except requests.Timeout:
                    print("请求超时,重新发送")
                    res = requests.get(url + ':' + str(port) + api_room_info, params=params)
                data_dict = res.json()
                # convert to a dataframe
                data = [data_dict]
                this_df = pd.DataFrame(data)
                tmp_df = pd.concat([tmp_df, this_df], axis=1)

            df_rooms = pd.concat([df_rooms, tmp_df], axis=0)
            print(df_rooms)

            # from routers.schedule import service_queue, waiting_queue,room_queue
            # print("房间队列")
            # for room in room_queue:
            #     print(room.room_id,room.status)
            # print("服务队列")
            # for room in service_queue:
            #     print(room.room_id)
            # print("等待队列")
            # for room in waiting_queue:
            #     print(room.room_id)
            
    except KeyboardInterrupt:
        print("线程查询被中断")
        return
    
    global roomInfo, scheduleInfo
    roomInfo = df_rooms
    scheduleInfo = df_schedule

def only_for_test(actions):

    api_room_info = '/user/show/'
    df_rooms = pd.DataFrame()
    df_schedule = pd.DataFrame()

    # 发起请求
    for idx, action_list in enumerate(actions):
        for action in action_list:
            print('第%d分钟，%d，%s' % (idx, action.room_id, action.input))
            action.post()
            
        print('第%d分钟' % idx)
        tmp_df = pd.DataFrame()
        for room_id in room_map.values():
            params = {
            'room_id': room_id
            }    
            res = requests.get(url + ':' + str(port) + api_room_info+str(room_id), timeout=5)
            data_dict = res.json()
            # convert to a dataframe
            data = [data_dict]
            this_df = pd.DataFrame(data)
            tmp_df = pd.concat([tmp_df, this_df], axis=1)

        df_rooms = pd.concat([df_rooms, tmp_df], axis=0)
        print(df_rooms)

        # res2=requests.get(url + ':' + str(port) + '/schedule/show')
        # data_dict = res2.json()
        # # convert to a dataframe
        # data = [data_dict]
        # this_df = pd.DataFrame(data)
        # df_schedule = pd.concat([df_schedule, this_df], axis=0)

        requests.get(url + ':' + str(port) + '/schedule/test_poweron')

        res=requests.get(url + ':' + str(port) + '/schedule/show')
        data_dict = res.json()
        # convert to a dataframe
        data = [data_dict]
        this_df = pd.DataFrame(data)
        df_schedule = pd.concat([df_schedule, this_df], axis=0)
        print(df_schedule)
        time.sleep(10)
    # 将结果保存在Excel
    writer = pd.ExcelWriter('result.xlsx')
    df_rooms.to_excel(writer, sheet_name='房间信息', index=False)
    df_schedule.to_excel(writer, sheet_name='调度信息', index=False)
    writer._save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u',
                        '--url', 
                        type=str, 
                        default='127.0.0.1')
    parser.add_argument('-p',
                        '--port', 
                        type=int, 
                        default=8000)
    args = parser.parse_args()

    url = args.url
    port = args.port
    
    url = 'http://' + url
    
    # read excel case
    case_df = read_excel_case(FILENAME)
    
    # 表格中的数据在取用的时候全部变成str格式
    # 遍历每一行
    actions = []    # 一个二级列表
    for index, row in case_df.iterrows():
        time_ = row['时间(min)']
        # 遍历该行
        action_once = []
        for room in case_df.columns[1:]:
            operation = row[room]   # 取每个房间的信息
            if not pd.isna(operation):
                # 如果房间有操作，则记录
                tmp_op = str(operation)
                room_id = room_map[room]
                op = []
                if '，' in tmp_op:
                    op = tmp_op.split('，')
                else:
                    op.append(tmp_op)
                for item in op:
                    action_once.append(Action(room_id, item))
                    
        actions.append(action_once)

    only_for_test(actions)

    # thread1 = threading.Thread(target=thread_request, args=(actions,), daemon=True)
    # thread2 = threading.Thread(target=thread_query, args=(actions,), daemon=True)


    # requests.get(url + ':' + str(port) + '/schedule/poweron')
    # thread1.start()
    # thread2.start()    
    
    # try:
    #     # 等待线程完成
    #     thread1.join()
    #     thread2.join()
    # except KeyboardInterrupt:
    #     print("主程序中断")
    # df = pd.read_excel(FILENAME, sheet_name='测试用例')
    # target1 = df.iloc[2:28, 6:26]
    # target2 = df.iloc[2:28, 27:32]
    # assert target1.size == roomInfo.size
    # assert target2.size == scheduleInfo.size
    # # df.iloc[2:28, 6:26] = roomInfo.values
    # # df.iloc[2:28, 27:32] = scheduleInfo.values
    
    # # create a file to store the result
    # writer = pd.ExcelWriter('result.xlsx')
    # df.to_excel(writer, sheet_name='测试用例', index=False)
    # roomInfo.to_excel(writer, sheet_name='房间信息', index=False)
    # scheduleInfo.to_excel(writer, sheet_name='调度信息', index=False)
    # writer.save()