<template>
    <head>
        <meta name="viewport" content="width=1100px, initial-scale=1, minimum-scale=1">
    </head>
    <div class="control_room_view">
        <div class="header">
            <img src="../assets/icon.png" alt="Icon" class="icon" />
        </div>
        <room v-for="(room, index) in rooms" :key="room.id" :room-number="room.number" :state="room.state"
            :temperature="room.temperature" :wind-speed="room.windSpeed" :customClass="`room${index + 1}`"></room>
        <div class="mode">
            <button class="hot" v-on:click="setMode('hot')" :class="{ active: isHot, 'hot': true }">热</button>
            <button class="cold" v-on:click="setMode('cold')" :class="{ active: isCold, 'cold': true }">冷</button>
            <!--button-- class="init" v-on:click="initRooms">初始化</!--button-->
        </div>
        <button class="init" v-on:click="initRooms">开机</button>
        <div class="queue-container">
            <div class="queue-box" id="waiting-queue">
                <h3>Waiting Queue</h3>
                <!-- Waiting Queue 的内容 -->
                <p> {{ waitingQueue }}</p>
            </div>
            <div class="queue-box" id="serving-queue">
                <h3>Serving Queue</h3>
                <!-- Serving Queue 的内容 -->
                <p> {{ servingQueue }}</p>
            </div>
        </div>
    </div>
</template>

<script>
import Room from '@/components/Room.vue';
import {admin_create, admin_modify} from "@/admin";
import {power_on} from "@/schedule";
import { show } from '@/schedule';
// 设置最小窗口宽度
const minWidth = 1100;

// 当窗口大小改变时触发
window.onresize = () => {
    // 如果窗口宽度小于最小宽度
    if (window.innerWidth < minWidth) {
        // 将窗口宽度设置为最小宽度
        window.resizeTo(minWidth, window.innerHeight);
    }
}
export default {
    name: 'ControlRoomView',
    components: {
        Room // 注册 Room 组件
    },
    data() {
        return {
            rooms: [], // 初始化为空数组
            isCold: true, // 用于控制按钮的激活状态
            isHot: false  // 控制热按钮的激活状态
        };
    },
    methods: {
        setMode(mode) {
            this.isCold = mode === 'cold';
            this.isHot = mode === 'hot';
        },
        initializeRoomData() {
            // 创建一个包含初始房间数据的数组
            return Array.from({ length: 5 }, (_, i) => ({
                id: i + 1,
                number: `Room${i + 1}`,
                state: 'Off',
                temperature: 'N/A',
                windSpeed: 'N/A'
            }));
        },
        initRooms() {
            // 将房间重置为初始状态
            this.rooms = this.initializeRoomData();
        },
    },
    created() {
        // 在组件创建时初始化房间
        this.initRooms();
        // 调用 power_on 函数
        power_on();
    },
};
</script>

<style scoped>
html,
body {
    min-width: 1100px;
}

/* ControlRoomView.vue 的样式 */
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

.icon {
    width: 70px;
}

.mode {
    position: absolute;
    /* 确保完全居中 */
    left: 60%;
    /* 水平居中 */
    transform: translateX(-50%);
    /* 使用绝对定位 */
    bottom: 20px;
    /* 距离屏幕底部10px */
    /* 水平居中定位的另一部分 */
    display: inline-flex;
    justify-content: center;
    /* 水平居中对齐内部按钮 */
    align-items: center;
}

.hot {
    /* 激活状态的按钮样式 */
    width: 40px;
    /* 按钮宽度与输入框相同 */
    height: 40px;
    /* 按钮高度 */
    padding: 10px;
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

}

.cold {
    /* 激活状态的按钮样式 */
    width: 40px;
    /* 按钮宽度与输入框相同 */
    height: 40px;
    /* 按钮高度 */
    padding: 10px;
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

}

.mode button:hover {
    background-color: rgb(252, 195, 97);
}

.mode button.active {
    /* 边框圆角 */
    background-color: #007bff;
    /* 背景颜色 */
    color: white;
    /* 字体颜色 */
}

.init:hover {
    background-color: rgb(252, 195, 97);
}

.init {
    width: 80px;
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
    left: 45%;
    /* 水平居中 */
    transform: translateX(-50%);
    bottom: 20px;
    /* 水平居中定位的另一部分 */
    display: flex;
    justify-content: center;
    /* 水平居中对齐内部按钮 */
    align-items: center;
}

.init:active {
    /* 点击时的样式 */
    background-color: #ddd;
    color: black;
}

.room1 {
    position: absolute;
    top: 10%;
    left: 10%;

}

.room2 {
    position: absolute;
    top: 10%;
    left: 40%;

}

.room3 {
    position: absolute;
    top: 10%;
    left: 70%;

}

.room4 {
    position: absolute;
    top: 55%;
    left: 10%;

}

.room5 {
    position: absolute;
    top: 55%;
    left: 40%;

}

.queue-container {
    position: absolute;
    top: 50%;
    left: 70%;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.queue-box {
    border: 2px solid #FFFFFF;
    /* 白色边框 */
    background-color: rgba(255, 255, 255, 0.5);
    /* 半透明背景 */
    margin-bottom: 10px;
    /* 和下一个元素的间距 */
    width: 270px;
    /* 或根据实际情况进行调整 */
    height: 120px;
    /* 或根据实际情况进行调整 */
    display: flex;
    align-items: flex-start;
    justify-content: center;
    color: black;
    /* 文字颜色 */
    font-size: 14px;
    border-radius: 5px;

    /* 文字大小 */
}
</style>
