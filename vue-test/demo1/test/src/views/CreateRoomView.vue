<!-- 

template: 定义组件的HTML模板    李小芊
script: 定义组件的行为、通信连接  王俊杰
style: 定义组件的样式         李小芊

 -->


<!-- 

页面构建完成：12.14  李小芊
初始通信连接 12.15   王俊杰
修改了一下小bug 12.16   王俊杰
 
 -->


<template>
    <div class="control_room_view">
        <!-- <div class="header">
            <img src="../assets/icon.png" alt="Icon" class="icon" />
        </div> -->
        <div>
            <button class="room" v-for="(room, index) in rooms" :key="index" :class="buttonClasses[index]"
                @click="showDialog(index)">
                <h3>Room{{ index + 1 }}</h3>
            </button>
        </div>

        <div v-if="dialogVisible" class="dialog">
            <h2>创建房间</h2>
            <label for="room_id">room_id：</label>
            <input v-model="room_id" type="number" id="room_id" />
            <label for="identity_card">identity_card：</label>
            <input v-model="identity_card" type="number" id="identity_card" />
            <label for="initial_temperature">initial_temperature：</label>
            <input v-model="initial_temperature" type="number" id="initial_temperature" />

            <div class="button0">
                <button class="confirm" @click="confirmDialog">确认</button>
            </div>
        </div>
        <router-link to="/control-room" class="return" v-on:click="initRooms">返回中控室</router-link>
    </div>
</template>

<script>
import { admin_create } from "@/admin";

export default {
    data() {
        return {
            rooms: new Array(5).fill(null), // Assuming there are 5 rooms
            selectedRooms: new Array(5).fill(false),
            dialogVisible: false,
            room_id: null,
            identity_card: null,
            initial_temperature: null,
            buttonClasses: ['button1', 'button2', 'button3', 'button4', 'button5'],
            selectedRoomIndex: null,
        };
    },
    methods: {
        showDialog(index) {
            this.dialogVisible = true;
            this.selectedRoomIndex = index;
        },
        async create_room(room_id, identity_card, initial_temperature) {
            try {
                // Call the API to create the room
                  await admin_create(room_id, identity_card, initial_temperature);


            } catch (error) {
                console.error("An error occurred while creating the room", error);
            }
        },
        confirmDialog() {
            // Perform any necessary operations related to the input data
            // Currently, just close the dialog
            this.create_room(this.room_id, this.identity_card, this.initial_temperature);
            this.dialogVisible = false;

            // Optional: reset the form fields
            this.room_id = null;
            this.identity_card = null;
            this.initial_temperature = null;

            
        },
       
    },
};
</script>

<style>
.dialog {
    position: fixed;
    top: 65%;
    left: 80%;
    transform: translate(-50%, -50%);
    border-radius: 4px;
    background: white;
    padding: 20px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    align-items: center;
}

.button0 {
    margin-top: 50px;
}

.confirm {
    text-decoration: none;
    width: 100px;
    height: 40px;
    margin-top: 0px;
    align-self: center;
    border-radius: 4px;
    border-color: rgb(181, 178, 178);
    /* 边框圆角 */
    background-color: white;
    color: black;
    /* 字体颜色 */
    font-size: 16px;
    cursor: pointer;
    /* 鼠标悬停时的光标样式 */
    position: absolute;
    left: 50%;
    /* 水平居中 */
    transform: translateX(-50%);
    bottom: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.selected {
    background-color: blue;
    color: white;
}

.clicked {
    background-color: orange;
    /* 点击后变色的样式 */
}

.room {
    border: 1px solid #ddd;
    padding: 10px;
    border-radius: 5px;
    width: 250px;
    /* 设置房间的宽度 */
    height: 150px;
    background-color: rgba(255, 255, 255, 0.812);
}

.room-header h3 {
    text-align: center;
    /* 文本居中 */
    width: 100%;
    /* 设置宽度为100% */
    color: black;
}

.button1 {
    position: absolute;
    top: 10%;
    left: 10%;
    font-size: 18px;
}

.button2 {
    position: absolute;
    top: 10%;
    left: 40%;
    font-size: 18px;
}

.button3 {
    position: absolute;
    top: 10%;
    left: 70%;
    font-size: 18px;
}

.button4 {
    position: absolute;
    top: 55%;
    left: 10%;
    font-size: 18px;
}

.button5 {
    position: absolute;
    top: 55%;
    left: 40%;
    font-size: 18px;
}

.control_room_view {
    background-image: url('../assets/2023.10.30.jpg');
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center center;
    background-attachment: fixed;
    height: 100vh;
    width: 100vw;
    min-width: 1100px;
    display: flex;
    position: relative;
    /* 样式 */
}

.header {
    padding-top: 20px;
    padding-left: 20px;
    display: flex;
    justify-content: left;
    align-items: flex-start;
    width: 100%;
}

.return {
    text-decoration: none;
    /* 取消下划线 */
    width: 100px;
    /* 按钮宽度与输入框相同 */
    height: 40px;
    /* 按钮高度 */
    /* 按钮内边距 */
    margin-top: 0px;
    align-self: center;
    /* 与上方元素的间隔 */
    border: none;
    /* 无边框 */
    border-radius: 4px;
    /* 边框圆角 */
    background-color: white;
    /* 背景颜色 */
    color: black;
    /* 字体颜色 */
    font-size: 16px;
    /* 字体大小 */
    cursor: pointer;
    /* 鼠标悬停时的光标样式 */
    position: absolute;
    left: 50%;
    /* 水平居中 */
    transform: translateX(-50%);
    bottom: 20px;
    /* 水平居中定位的另一部分 */
    display: flex;
    justify-content: center;
    /* 水平居中对齐内部按钮 */
    align-items: center;
}

.return:hover {
    background-color: rgb(252, 195, 97);
}

.button1:hover {
    background-color: #007bff;
}

.button2:hover {
    background-color: #007bff;
}

.button3:hover {
    background-color: #007bff;
}

.button4:hover {
    background-color: #007bff;
}

.button5:hover {
    background-color: #007bff;
}
</style>